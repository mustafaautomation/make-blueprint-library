"""Compile scenario specs into importable Make blueprints and the catalog."""

from __future__ import annotations

import json
import re
from pathlib import Path

from makebp.allowlist import INSTANT_TRIGGERS, MODULES
from makebp.render import mermaid, render_png
from makebp.validate import ROOT, TEST_STATUS, dump_allowlist

RESERVED_KEYS = {
    "now",
    "if",
    "formatDate",
    "length",
    "lower",
    "upper",
    "sum",
    "emptystring",
    "toString",
    "parseDate",
    "substring",
    "replace",
    "trim",
    "first",
    "last",
    "join",
    "split",
    "contains",
    "floor",
    "ceil",
    "round",
    "max",
    "min",
    "avg",
}

CATEGORIES = [
    ("lead-gen-crm", "Lead gen and CRM"),
    ("speed-to-lead", "Speed to lead"),
    ("invoices-docs", "Invoices and documents"),
    ("email", "Email"),
    ("social", "Social"),
    ("ecommerce", "E-commerce"),
    ("support", "Support"),
    ("booking", "Booking"),
    ("reporting", "Reporting"),
    ("slack-notion-clickup", "Slack, Notion, and ClickUp"),
    ("scraping-enrichment", "Scraping and enrichment"),
    ("ai-agents", "AI agents"),
    ("hr-recruiting", "HR and recruiting"),
    ("finance", "Finance"),
]

CATEGORY_BLURB = {
    "lead-gen-crm": "Capture a lead, score or enrich it, and write it to a CRM.",
    "speed-to-lead": "Reply by SMS or email while the inquiry is still warm.",
    "invoices-docs": "Pull fields out of invoices, receipts, and other documents.",
    "email": "Triage a mailbox, draft replies, and file what matters.",
    "social": "Turn one source into channel-ready posts.",
    "ecommerce": "Sync orders, refunds, and stock signals out of a store.",
    "support": "Classify a ticket and route it to the right queue.",
    "booking": "Confirm, remind, and brief people around a booking.",
    "reporting": "Roll a sheet or API up into a Slack or email digest.",
    "slack-notion-clickup": "Turn a Slack or form event into an ops task.",
    "scraping-enrichment": "Fetch a public page or dataset and land it in a sheet.",
    "ai-agents": "Let a model choose a tool, then answer from the tool result.",
    "hr-recruiting": "Parse applications and score them against a rubric.",
    "finance": "Log charges, payouts, and categories for a human to reconcile.",
}


def _walk_steps(steps: list[dict]):
    for step in steps:
        yield step
        for route in step.get("routes") or []:
            yield from _walk_steps(route["steps"])


def _validate_spec(spec: dict) -> None:
    keys = []
    for step in _walk_steps(spec["steps"]):
        key = step["key"]
        if not re.fullmatch(r"[a-z][a-z0-9_]*", key):
            raise ValueError(f"{spec['id']}: bad step key {key}")
        if key in RESERVED_KEYS:
            raise ValueError(f"{spec['id']}: key {key} collides with an IML function")
        if step["module"] not in MODULES:
            raise ValueError(f"{spec['id']}: {step['module']} is not allowlisted")
        keys.append(key)
        if step.get("routes") and step is not spec["steps"][-1] and False:
            pass
    if len(keys) != len(set(keys)):
        raise ValueError(f"{spec['id']}: duplicate step keys")
    _assert_routers_last(spec["steps"], spec["id"])


def _assert_routers_last(steps: list[dict], scenario_id: str) -> None:
    for index, step in enumerate(steps):
        if step.get("routes") and index != len(steps) - 1:
            raise ValueError(f"{scenario_id}: router {step['key']} is not the last step in its flow")
        for route in step.get("routes") or []:
            if not route["steps"]:
                raise ValueError(f"{scenario_id}: route {route['name']} is empty")
            _assert_routers_last(route["steps"], scenario_id)


def _assign(steps: list[dict], counter: list[int]) -> list[dict]:
    nodes = []
    for step in steps:
        counter[0] += 1
        node = {
            "key": step["key"],
            "id": counter[0],
            "module": step["module"],
            "name": step["name"],
            "why": step["why"],
            "mapper": step.get("mapper"),
            "parameters": dict(step.get("parameters") or {}),
            "notes": list(step.get("notes") or []),
            "filter": step.get("filter"),
            "feeder": step.get("feeder"),
            "routes": None,
            "onerror_nodes": None,
            "onerror_why": None,
        }
        if step.get("onerror"):
            handler = step["onerror"]
            chain = []
            notify = handler.get("notify")
            if notify:
                counter[0] += 1
                chain.append(
                    {
                        "key": f"{step['key']}_alert",
                        "id": counter[0],
                        "module": notify["module"],
                        "name": notify["name"],
                        "why": notify["why"],
                        "mapper": notify.get("mapper") or {},
                        "parameters": dict(notify.get("parameters") or {}),
                        "notes": list(notify.get("notes") or []),
                        "filter": None,
                        "feeder": None,
                        "routes": None,
                        "onerror_nodes": None,
                        "onerror_why": None,
                    }
                )
            counter[0] += 1
            directive = handler["directive"]
            chain.append(
                {
                    "key": f"{step['key']}_directive",
                    "id": counter[0],
                    "module": directive,
                    "name": MODULES[directive]["label"],
                    "why": handler["why"],
                    "mapper": handler.get("mapper") or {},
                    "parameters": {},
                    "notes": [],
                    "filter": None,
                    "feeder": None,
                    "routes": None,
                    "onerror_nodes": None,
                    "onerror_why": None,
                }
            )
            node["onerror_nodes"] = chain
            node["onerror_why"] = handler["why"]
        if step.get("routes"):
            compiled_routes = []
            for branch in step["routes"]:
                compiled = _assign(branch["steps"], counter)
                if branch.get("filter"):
                    if compiled[0].get("filter"):
                        raise ValueError(f"route {branch['name']} first step already has a filter")
                    compiled[0]["filter"] = branch["filter"]
                compiled_routes.append(
                    {"name": branch["name"], "why": branch["why"], "steps": compiled, "filter": branch.get("filter")}
                )
            node["routes"] = compiled_routes
        nodes.append(node)
    return nodes


def _keymap(nodes: list[dict], acc: dict[str, int]) -> None:
    for node in nodes:
        acc[node["key"]] = node["id"]
        if node.get("onerror_nodes"):
            _keymap(node["onerror_nodes"], acc)
        for route in node.get("routes") or []:
            _keymap(route["steps"], acc)


def _rewrite(value, keymap: dict[str, int]):
    if isinstance(value, str):

        def repl_block(match: re.Match) -> str:
            inner = match.group(1)
            for key, module_id in sorted(keymap.items(), key=lambda item: -len(item[0])):
                inner = re.sub(
                    rf"(?<![A-Za-z0-9_]){re.escape(key)}(?=\.)",
                    str(module_id),
                    inner,
                )
            return "{{" + inner + "}}"

        return re.sub(r"\{\{(.*?)\}\}", repl_block, value, flags=re.S)
    if isinstance(value, list):
        return [_rewrite(item, keymap) for item in value]
    if isinstance(value, dict):
        return {key: _rewrite(item, keymap) for key, item in value.items()}
    return value


def _apply_keys(nodes: list[dict], keymap: dict[str, int]) -> None:
    for node in nodes:
        if node.get("feeder"):
            feeder_key = node["feeder"]
            if feeder_key not in keymap:
                raise ValueError(f"unknown feeder {feeder_key}")
            node["parameters"]["feeder"] = keymap[feeder_key]
            if node["module"] == "util:TextAggregator" and "rowSeparator" not in node["parameters"]:
                node["parameters"]["rowSeparator"] = "\n"
        node["mapper"] = _rewrite(node["mapper"], keymap)
        node["parameters"] = _rewrite(node["parameters"], keymap)
        node["filter"] = _rewrite(node["filter"], keymap)
        if node.get("onerror_nodes"):
            _apply_keys(node["onerror_nodes"], keymap)
        for route in node.get("routes") or []:
            _apply_keys(route["steps"], keymap)


def _place_designer(nodes: list[dict], x: int, y: int) -> None:
    cursor = x
    for node in nodes:
        node["x"] = cursor
        node["y"] = y
        if node.get("onerror_nodes"):
            handler_x = cursor
            for handler in node["onerror_nodes"]:
                handler["x"] = handler_x
                handler["y"] = y + 300
                handler_x += 300
        if node.get("routes"):
            for index, route in enumerate(node["routes"]):
                _place_designer(route["steps"], cursor + 300, y + index * 300)
        cursor += 300


def _emit(node: dict) -> dict:
    meta = MODULES[node["module"]]
    designer = {"x": node["x"], "y": node["y"], "name": node["name"]}
    metadata: dict = {"designer": designer}
    if meta["connection"]:
        metadata["parameters"] = [
            {
                "name": meta["connection"]["parameter"],
                "type": meta["connection"]["type"],
                "label": meta["connection"]["label"],
                "required": True,
            }
        ]
    module = {
        "id": node["id"],
        "module": node["module"],
        "version": meta["version"],
        "parameters": node["parameters"] if node["module"] != "gateway:CustomWebHook" else {},
        "mapper": None if node["module"] == "builtin:BasicRouter" else node["mapper"],
        "metadata": metadata,
    }
    if node.get("filter"):
        module["filter"] = node["filter"]
    if node.get("onerror_nodes"):
        module["onerror"] = [_emit(child) for child in node["onerror_nodes"]]
    if node.get("routes"):
        module["routes"] = [{"flow": [_emit(child) for child in route["steps"]]} for route in node["routes"]]
    return module


def _uses_break(nodes: list[dict]) -> bool:
    for node in nodes:
        for handler in node.get("onerror_nodes") or []:
            if handler["module"] == "builtin:Break":
                return True
        for route in node.get("routes") or []:
            if _uses_break(route["steps"]):
                return True
    return False


def compile_spec(spec: dict) -> tuple[dict, list[dict]]:
    _validate_spec(spec)
    nodes = _assign(spec["steps"], [0])
    keymap = {}
    _keymap(nodes, keymap)
    _apply_keys(nodes, keymap)
    _place_designer(nodes, 0, 0)
    first = nodes[0]["module"]
    blueprint = {
        "name": spec["title"],
        "flow": [_emit(node) for node in nodes],
        "metadata": {
            "instant": first in INSTANT_TRIGGERS,
            "version": 1,
            "designer": {"orphans": []},
            "scenario": {
                "roundtrips": 1,
                "maxErrors": spec["max_errors"],
                "autoCommit": True,
                "autoCommitTriggerLast": True,
                "sequential": bool(spec["sequential"]),
                "confidential": False,
                "dataloss": False,
                "dlq": _uses_break(nodes),
                "freshVariables": False,
            },
        },
    }
    return blueprint, nodes


def _flatten(nodes: list[dict], depth: int = 0, route_name: str | None = None):
    for node in nodes:
        yield depth, route_name, node
        for handler in node.get("onerror_nodes") or []:
            yield depth + 1, "error handler", handler
        for route in node.get("routes") or []:
            yield from _flatten(route["steps"], depth + 1, route["name"])


def _mapper_preview(mapper) -> str:
    if not mapper:
        return "No mapped fields. Configure the module after import, or it only passes the bundle through."
    if not isinstance(mapper, dict):
        return "Mapper is empty."
    lines = []
    for key, value in mapper.items():
        rendered = json.dumps(value, ensure_ascii=False)
        if len(rendered) > 220:
            rendered = rendered[:217] + "..."
        lines.append(f"- `{key}`: `{rendered}`")
    return "\n".join(lines)


def _connections(nodes: list[dict]) -> list[str]:
    seen = []
    found = []

    def visit(items: list[dict]) -> None:
        for node in items:
            conn = MODULES[node["module"]]["connection"]
            app = MODULES[node["module"]]["app"]
            if conn and app not in seen:
                seen.append(app)
                found.append(
                    f"- **{app}** — create a connection and select it on every {app} module. "
                    f"The blueprint leaves `{conn['parameter']}` unset on purpose."
                )
            if node.get("onerror_nodes"):
                visit(node["onerror_nodes"])
            for route in node.get("routes") or []:
                visit(route["steps"])

    visit(nodes)
    return found


def _placeholders(blueprint: dict) -> list[str]:
    return sorted(set(re.findall(r"YOUR_[A-Z0-9_]+", json.dumps(blueprint))))


def render_readme(spec: dict, blueprint: dict, nodes: list[dict], diagram: str) -> str:
    settings = blueprint["metadata"]["scenario"]
    lines = [
        f"# {spec['title']}",
        "",
        "Portfolio demo by Mustafa ([mustafaautomation](https://github.com/mustafaautomation)). "
        "Not client work. Connect your own accounts after import. Live walkthroughs, when published, "
        "sit on a subdomain of quvantic.com.",
        "",
        f"**Category:** {dict(CATEGORIES)[spec['category']]}  ",
        f"**Difficulty:** {spec['difficulty']}  ",
        f"**Apps:** {', '.join(spec['apps'])}  ",
        f"**Test status:** {TEST_STATUS}",
        "",
        "## Problem",
        "",
        spec["problem"].strip(),
        "",
        "## Who it's for",
        "",
        spec["audience"].strip(),
        "",
        "## Module-by-module walkthrough",
        "",
        "Ids match the blueprint. A router runs every route whose filter passes. "
        "An error handler runs only when that module throws.",
        "",
    ]
    for _depth, route_name, node in _flatten(nodes):
        where = f" — route **{route_name}**" if route_name and route_name != "error handler" else ""
        if route_name == "error handler":
            where = " — error handler"
        meta = MODULES[node["module"]]
        lines.append(f"### {node['id']}. {node['name']}{where}")
        lines.append("")
        lines.append(f"`{node['module']}` · {meta['label']} · {meta['app']}")
        lines.append("")
        lines.append(node["why"].strip())
        lines.append("")
        if node.get("filter"):
            lines.append(f"Filter **{node['filter']['name']}**: `{json.dumps(node['filter']['conditions'])}`")
            lines.append("")
        if node["module"] != "builtin:BasicRouter":
            lines.append(_mapper_preview(node.get("mapper")))
            lines.append("")
        for note in node.get("notes") or []:
            lines.append(note)
            lines.append("")
    lines.extend(["## Diagram", "", "![Scenario flow](diagram.png)", "", "```mermaid", diagram.rstrip(), "```", ""])
    lines.extend(["## Setup", ""])
    lines.append("1. In Make, create a scenario, open the three-dot menu at the bottom of the editor, and choose **Import Blueprint**. Select `blueprint.json`.")
    lines.append("2. Open every red module and pick or create the connection. Red means the account is not selected yet.")
    lines.append(f"3. Schedule: {spec['schedule']}")
    if spec.get("sheet_columns"):
        lines.append("4. Create the spreadsheet tab this scenario expects, with a header row in row 1:")
        for column in spec["sheet_columns"]:
            lines.append(f"   - {column}")
        lines.append("5. Select that spreadsheet and sheet on every Google Sheets module. The ids are blank in the file.")
    else:
        lines.append("4. Fill every blank selector (spreadsheet, channel, base, calendar) from your own account.")
    lines.append("6. Run once with the bundled `sample-input.json`. " + spec["sample_note"])
    lines.append("7. Check the output bundle of each module before you turn the schedule on.")
    lines.append("")
    lines.extend(["## Connections", ""])
    connections = _connections(nodes)
    if connections:
        lines.extend(connections)
    else:
        lines.append("- This scenario uses modules that do not ask for an account connection.")
    placeholders = _placeholders(blueprint)
    if placeholders:
        lines.append("")
        lines.append("Replace these placeholders in the HTTP modules before the first live run:")
        for token in placeholders:
            lines.append(f"- `{token}`")
    lines.append("")
    lines.append("Nothing in the file is a live connection id, webhook URL, or API key. Make rejects another team's connection id at import, so the slots are empty on purpose.")
    lines.append("")
    lines.extend(["## Data mapping", ""])
    lines.append("References use the module id: `{{1.subject}}` is the `subject` field of module 1. Sheets columns are zero-based and backticked (`{{1.`0`}}` is column A) so a renamed header does not break the map.")
    lines.append("")
    for note in spec.get("mapping") or []:
        lines.append(f"- {note}")
    if not spec.get("mapping"):
        lines.append("- Map only the fields listed in the walkthrough. Leave every other field untouched.")
    lines.append("")
    lines.extend(["## Error handling", ""])
    lines.append(
        f"Scenario settings: `maxErrors` {settings['maxErrors']}, "
        f"`dlq` {str(settings['dlq']).lower()}, "
        f"`sequential` {str(settings['sequential']).lower()}, "
        f"`autoCommit` true. "
        "After this many consecutive failed runs Make deactivates a scheduled scenario."
    )
    lines.append("")
    described = False
    for _, route_name, node in _flatten(nodes):
        if node.get("onerror_why"):
            described = True
            directive = node["onerror_nodes"][-1]["module"]
            lines.append(f"- Module {node['id']} ({node['name']}) handles errors with `{directive}`. {node['onerror_why']}")
        if node.get("filter"):
            described = True
            lines.append(f"- Module {node['id']} runs only when filter **{node['filter']['name']}** passes. A blocked bundle stops on that path. It is not an error.")
        if node["module"] == "builtin:BasicRouter":
            described = True
            lines.append(f"- Router {node['id']} ({node['name']}) {node['why']}")
            for branch in node["routes"]:
                filt = branch["steps"][0].get("filter")
                filt_text = f" Filter: **{filt['name']}**." if filt else " No filter, so this route runs for every bundle that reaches the router."
                lines.append(f"  - **{branch['name']}.** {branch['why']}{filt_text}")
    if not described:
        lines.append("No router, filter, or error handler is attached. A failed module stops the run, which is the right default when a partial write would be worse than a visible failure.")
    lines.append("")
    lines.extend(["## Customization", ""])
    for tip in spec.get("customization") or []:
        lines.append(f"- {tip}")
    if placeholders:
        lines.append("- Swap any `YOUR_*` value for the id from your own account. Do not commit the filled-in file.")
    lines.append("- Duplicate the scenario before you change the prompt, so you can diff against this demo later.")
    lines.append("")
    lines.extend(["## Time saved", "", spec["time_saved"].strip(), ""])
    lines.append("## Files")
    lines.append("")
    lines.append("| File | What it is |")
    lines.append("| --- | --- |")
    lines.append("| `blueprint.json` | Import this into Make. |")
    lines.append("| `sample-input.json` | Fictional bundle for the first run. |")
    lines.append("| `diagram.png` | Flow diagram. |")
    lines.append("| `diagram.mmd` | Mermaid source for the same flow. |")
    lines.append("")
    return "\n".join(lines)


def scenario_readme_path(spec: dict) -> Path:
    return ROOT / "scenarios" / spec["category"] / spec["id"]


def write_scenario(spec: dict) -> dict:
    blueprint, nodes = compile_spec(spec)
    folder = scenario_readme_path(spec)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "blueprint.json").write_text(json.dumps(blueprint, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (folder / "sample-input.json").write_text(
        json.dumps(spec["sample"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    diagram = mermaid(nodes)
    (folder / "diagram.mmd").write_text(diagram, encoding="utf-8")
    render_png(spec["title"], nodes, folder / "diagram.png")
    (folder / "README.md").write_text(render_readme(spec, blueprint, nodes, diagram), encoding="utf-8")
    return {
        "id": spec["id"],
        "title": spec["title"],
        "category": spec["category"],
        "apps": spec["apps"],
        "difficulty": spec["difficulty"],
        "tags": spec["tags"],
        "path": f"scenarios/{spec['category']}/{spec['id']}",
        "description": spec["description"],
        "test_status": TEST_STATUS,
        "screenshot": f"scenarios/{spec['category']}/{spec['id']}/diagram.png",
    }


def render_root_readme(specs: list[dict], catalog_entries: list[dict]) -> str:
    by_id = {spec["id"]: spec for spec in specs}
    featured = sorted((spec for spec in specs if spec.get("featured_rank")), key=lambda item: item["featured_rank"])
    lines = [
        "# make-blueprint-library",
        "",
        "A portfolio library of [Make.com](https://www.make.com/) scenario blueprints by Mustafa "
        "([mustafaautomation](https://github.com/mustafaautomation)). "
        "Demos, when published, live on subdomains of quvantic.com.",
        "",
        "**Portfolio demos only. Not client work.** These scenarios are fictional walkthroughs a buyer can import, "
        "reconnect, and adapt. They are not deliverables from a client engagement, and they do not contain anyone's accounts, keys, or data.",
        "",
        "Make (formerly Integromat) is the automation product these files import into. "
        "Each folder has an importable `blueprint.json`, a README, fictional sample input, and a flow diagram.",
        "",
        "## Import a blueprint",
        "",
        "1. Download the folder, or copy `blueprint.json`.",
        "2. In Make: **Scenarios → Create a new scenario → the three-dot menu at the bottom → Import Blueprint**.",
        "3. Open each red module and choose your own connection. Red means unconnected, not broken.",
        "4. Fill blank spreadsheets, channels, and every `YOUR_*` placeholder.",
        "5. Run once with `sample-input.json`, then turn the schedule on.",
        "",
        "The JSON shape is the blueprint Make exports and imports: `name`, `flow`, and `metadata`. "
        "Module entries carry `id`, `module` (`google-sheets:addRow`), `version`, `parameters`, `mapper`, and `metadata.designer` coordinates. "
        "Connection ids are omitted. A numeric connection id from someone else's team fails import with `IM304 Account doesn't exist`.",
        "",
        "## Top 20",
        "",
        "These are the demand-heavy patterns freelance buyers ask for first: invoices, lead routing, speed-to-lead, triage, booking, store orders, and reporting.",
        "",
        "| # | Scenario | Category | Difficulty |",
        "| ---: | --- | --- | --- |",
    ]
    for spec in featured:
        lines.append(
            f"| {spec['featured_rank']} | [{spec['title']}](scenarios/{spec['category']}/{spec['id']}/) | {dict(CATEGORIES)[spec['category']]} | {spec['difficulty']} |"
        )
    lines.extend(["", "## Catalog", "", f"{len(catalog_entries)} scenarios. The machine-readable index is [`catalog.json`](catalog.json), described in [`CATALOG_SCHEMA.md`](CATALOG_SCHEMA.md).", ""])
    lines.append("| Category | Scenarios | What the folder covers |")
    lines.append("| --- | ---: | --- |")
    for slug, title in CATEGORIES:
        count = sum(1 for entry in catalog_entries if entry["category"] == slug)
        if count == 0:
            continue
        lines.append(f"| [{title}](scenarios/{slug}/) | {count} | {CATEGORY_BLURB[slug]} |")
    lines.extend(["", "### Every scenario", ""])
    for slug, title in CATEGORIES:
        group = [entry for entry in catalog_entries if entry["category"] == slug]
        if not group:
            continue
        lines.append(f"#### {title}")
        lines.append("")
        lines.append("| Scenario | Apps | Difficulty | Tags |")
        lines.append("| --- | --- | --- | --- |")
        for entry in group:
            tags = ", ".join(entry["tags"])
            apps = ", ".join(entry["apps"])
            lines.append(
                f"| [{entry['title']}]({entry['path']}/) | {apps} | {entry['difficulty']} | {tags} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Validate",
            "",
            "Make has no free import API in this repo's CI, and this project does not buy a plan. "
            "Every blueprint is a **documented blueprint, structurally validated**:",
            "",
            "```bash",
            "python3 -m pip install -r requirements.txt",
            "python3 scripts/build_library.py",
            "python3 scripts/validate_blueprints.py --min 100",
            "python3 -m unittest tests/test_validator.py",
            "```",
            "",
            "The validator checks the JSON Schema in `schema/blueprint.schema.json`, the module allowlist in `schema/modules.allowlist.json`, "
            "`{{id.field}}` references, router and filter shape, aggregator feeders, and that no connection id, live webhook, or non-example email shipped.",
            "",
            "Module ids come from Make's own scenario-building examples and from public blueprint exports. "
            "Apps whose module id was not in those sources are called with `http:ActionSendData` and the vendor's documented REST URL. "
            "See [MODULES.md](MODULES.md).",
            "",
            "## Layout",
            "",
            "```text",
            "scenarios/<category>/<id>/",
            "  blueprint.json      import this",
            "  README.md           problem, walkthrough, setup",
            "  sample-input.json   fictional first run",
            "  diagram.png         flow diagram",
            "  diagram.mmd         Mermaid source",
            "catalog.json          gallery index",
            "schema/               JSON Schema and module allowlist",
            "```",
            "",
            "## License",
            "",
            "[MIT](LICENSE). Make, Integromat, and the names of the connected products are trademarks of their owners. This library is not affiliated with Make.",
            "",
        ]
    )
    return "\n".join(lines)


def write_category_readmes(entries: list[dict]) -> None:
    for slug, title in CATEGORIES:
        group = [entry for entry in entries if entry["category"] == slug]
        if not group:
            continue
        folder = ROOT / "scenarios" / slug
        folder.mkdir(parents=True, exist_ok=True)
        lines = [
            f"# {title}",
            "",
            "Portfolio demos by Mustafa ([mustafaautomation](https://github.com/mustafaautomation)). Not client work.",
            "",
            CATEGORY_BLURB[slug],
            "",
            "| Scenario | Difficulty | Description |",
            "| --- | --- | --- |",
        ]
        for entry in group:
            lines.append(f"| [{entry['title']}]({entry['id']}/) | {entry['difficulty']} | {entry['description']} |")
        lines.append("")
        (folder / "README.md").write_text("\n".join(lines), encoding="utf-8")


def build_all(specs: list[dict]) -> list[dict]:
    ids = [spec["id"] for spec in specs]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate scenario ids")
    categories = {slug for slug, _ in CATEGORIES}
    for spec in specs:
        if spec["category"] not in categories:
            raise ValueError(f"{spec['id']}: unknown category {spec['category']}")
    entries = [write_scenario(spec) for spec in specs]
    entries.sort(key=lambda item: (item["category"], item["title"].lower()))
    catalog = {"schema_version": "1.0.0", "scenarios": entries}
    (ROOT / "catalog.json").write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ROOT / "README.md").write_text(render_root_readme(specs, entries), encoding="utf-8")
    write_category_readmes(entries)
    dump_allowlist()
    return entries
