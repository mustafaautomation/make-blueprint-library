"""Structural validator for Make scenario blueprints.

Make is a hosted product, so CI cannot import a blueprint into an account.
This checks the export shape that Import Blueprint and
``POST /api/v2/scenarios`` accept, then checks module ids, mapper references,
routers, filters, and sanitization.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator

from makebp.allowlist import (
    AGGREGATOR_MODULES,
    CONNECTION_VALUE_KEYS,
    DIRECTIVES,
    INSTANT_TRIGGERS,
    MODULES,
    SECRET_PATTERNS,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "blueprint.schema.json"
CATALOG_SCHEMA_PATH = ROOT / "schema" / "catalog.schema.json"

TEST_STATUS = "documented blueprint, structurally validated"

REQUIRED_README_MARKERS = (
    "Portfolio demo",
    "Not client work.",
    "## Problem",
    "## Who it's for",
    "## Module-by-module walkthrough",
    "## Diagram",
    "```mermaid",
    "## Setup",
    "## Connections",
    "## Data mapping",
    "## Error handling",
    "## Customization",
    "## Time saved",
)

OPERATORS = {
    "text:equal",
    "text:notequal",
    "text:contain",
    "text:startwith",
    "text:pattern",
    "text:equal:ci",
    "number:equal",
    "number:greater",
    "number:less",
    "number:greaterorequal",
    "number:lessequal",
    "date:greater",
    "date:less",
    "boolean:equal",
    "array:contain",
    "exist",
    "notexist",
}

IML_BLOCK = re.compile(r"\{\{(.*?)\}\}", re.S)
MODULE_REF = re.compile(r"(?<![A-Za-z0-9_`])(\d+)(?=\.)")
WHOLE_BUNDLE = re.compile(r"^\s*`(\d+)`\s*$")
EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@([A-Za-z0-9.\-]+\.[A-Za-z]{2,})")
ALLOWED_EMAIL_DOMAINS = {"example.com", "example.org", "example.net"}
SHEET_ID = re.compile(r"^[A-Za-z0-9_\-]{25,}$")
SECRET_RES = [re.compile(p) for p in SECRET_PATTERNS]

REQUIRED_FILES = (
    "blueprint.json",
    "sample-input.json",
    "README.md",
    "diagram.mmd",
    "diagram.png",
)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except json.JSONDecodeError as exc:
        return None, f"{path}: not valid JSON ({exc})"


def blueprint_validator() -> Draft202012Validator:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return Draft202012Validator(schema)


def catalog_validator() -> Draft202012Validator:
    schema = json.loads(CATALOG_SCHEMA_PATH.read_text(encoding="utf-8"))
    return Draft202012Validator(schema)


def iter_strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from iter_strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from iter_strings(value)


def referenced_ids(value) -> set[int]:
    found: set[int] = set()
    if isinstance(value, str):
        for block in IML_BLOCK.findall(value):
            for match in MODULE_REF.finditer(block):
                found.add(int(match.group(1)))
            whole = WHOLE_BUNDLE.match(block)
            if whole:
                found.add(int(whole.group(1)))
    elif isinstance(value, dict):
        for item in value.values():
            found |= referenced_ids(item)
    elif isinstance(value, list):
        for item in value:
            found |= referenced_ids(item)
    return found


def walk_collect(flow: list, path: str, acc: list[tuple[str, dict]]) -> None:
    for index, module in enumerate(flow):
        here = f"{path}[{index}]"
        acc.append((here, module))
        if module.get("onerror"):
            walk_collect(module["onerror"], f"{here}.onerror", acc)
        for route_index, route in enumerate(module.get("routes") or []):
            walk_collect(route.get("flow") or [], f"{here}.routes[{route_index}].flow", acc)


def check_filter(module: dict, loc: str, errors: list[str]) -> None:
    filt = module.get("filter", None)
    if filt is None:
        return
    if not isinstance(filt, dict) or "name" not in filt or "conditions" not in filt:
        errors.append(f"{loc}: filter must be {{name, conditions}}.")
        return
    conditions = filt["conditions"]
    if not isinstance(conditions, list) or not conditions:
        errors.append(f"{loc}: filter.conditions must be a non-empty array of AND groups.")
        return
    for group in conditions:
        if not isinstance(group, list) or not group:
            errors.append(f"{loc}: each OR group in filter.conditions must be a non-empty AND array.")
            continue
        for condition in group:
            if not isinstance(condition, dict) or "a" not in condition or "o" not in condition:
                errors.append(f"{loc}: each filter condition needs a and o.")
                continue
            op = condition["o"]
            if op not in OPERATORS:
                errors.append(f"{loc}: unknown filter operator {op!r}.")
            if op not in {"exist", "notexist"} and "b" not in condition:
                errors.append(f"{loc}: operator {op} needs a b operand.")


def check_secrets(node, loc: str, errors: list[str]) -> None:
    for text in iter_strings(node):
        for pattern in SECRET_RES:
            if pattern.search(text):
                errors.append(f"{loc}: possible credential or live webhook matched {pattern.pattern}.")
                break
        for domain in EMAIL.findall(text):
            if domain.lower() not in ALLOWED_EMAIL_DOMAINS:
                errors.append(
                    f"{loc}: email domain {domain} is not a reserved example domain. Use example.com."
                )


def check_parameters(module: dict, loc: str, errors: list[str]) -> None:
    parameters = module.get("parameters") or {}
    if not isinstance(parameters, dict):
        errors.append(f"{loc}: parameters must be an object.")
        return
    for key, value in parameters.items():
        if key in CONNECTION_VALUE_KEYS and value not in (None, "", {}, []):
            errors.append(
                f"{loc}: parameters.{key} ships a connection, key, or hook id. Remove it so import stays unconfigured."
            )
        if key in {"teamId", "organizationId", "scenarioId", "dataStoreId", "dataStructureId"} and isinstance(value, int):
            errors.append(f"{loc}: parameters.{key} is a tenant id and must not be published.")
        if key in {"spreadsheetId", "baseId", "tableId"} and isinstance(value, str) and SHEET_ID.match(value):
            errors.append(f"{loc}: parameters.{key} looks like a real resource id. Blank it.")
    mapper = module.get("mapper") or {}
    if isinstance(mapper, dict):
        for key in ("spreadsheetId", "baseId", "tableId", "page_id", "calendarId"):
            value = mapper.get(key)
            if isinstance(value, str) and value and not value.startswith("{{") and SHEET_ID.match(value):
                errors.append(f"{loc}: mapper.{key} looks like a publisher resource id. Blank it or map it.")


def check_module_static(module: dict, loc: str, errors: list[str]) -> None:
    name = module.get("module")
    meta = MODULES.get(name)
    if meta is None:
        errors.append(f"{loc}: module {name!r} is not in the allowlist of known Make modules.")
        return
    if module.get("version") != meta["version"]:
        errors.append(
            f"{loc}: {name} version {module.get('version')} does not match allowlist version {meta['version']}."
        )
    designer = (module.get("metadata") or {}).get("designer") or {}
    if "x" not in designer or "y" not in designer:
        errors.append(f"{loc}: metadata.designer.x and y are required.")
    if (module.get("metadata") or {}).get("restore"):
        errors.append(f"{loc}: metadata.restore can carry account labels. Remove it.")
    if name == "builtin:BasicRouter":
        if module.get("filter"):
            errors.append(f"{loc}: put filters on the first module of each route, not on the router.")
        if module.get("onerror"):
            errors.append(f"{loc}: routers cannot carry an error handler.")
        routes = module.get("routes")
        if not isinstance(routes, list) or len(routes) < 2:
            errors.append(f"{loc}: router needs at least two routes.")
        else:
            for route in routes:
                if not isinstance(route, dict) or not route.get("flow"):
                    errors.append(f"{loc}: each route needs a non-empty flow.")
    elif module.get("routes"):
        errors.append(f"{loc}: only builtin:BasicRouter may define routes.")
    if name in AGGREGATOR_MODULES:
        feeder = (module.get("parameters") or {}).get("feeder")
        if not isinstance(feeder, int):
            errors.append(f"{loc}: aggregator {name} needs parameters.feeder set to an upstream module id.")
        if "feeder" in module:
            errors.append(f"{loc}: feeder must live in parameters. A top-level feeder is ignored at runtime.")
    if name == "builtin:BasicFeeder":
        mapper = module.get("mapper") or {}
        if not isinstance(mapper, dict) or "array" not in mapper:
            errors.append(f"{loc}: iterator needs mapper.array.")
    if name == "gateway:CustomWebHook" and module.get("parameters"):
        errors.append(f"{loc}: leave the webhook parameters empty. The hook is created after import.")
    check_filter(module, loc, errors)
    check_parameters(module, loc, errors)


def check_references(flow: list, available: set[int], path: str, known_ids: set[int], errors: list[str], in_handler: bool) -> None:
    upstream = set(available)
    for index, module in enumerate(flow):
        loc = f"{path}[{index}]"
        module_id = module["id"]
        if path == "flow" and index == 0 and module.get("filter"):
            errors.append(f"{loc}: the first module cannot carry a scenario filter.")
        refs = set()
        refs |= referenced_ids(module.get("mapper"))
        refs |= referenced_ids(module.get("filter"))
        refs |= referenced_ids(module.get("parameters"))
        for ref in sorted(refs):
            if ref not in known_ids:
                errors.append(f"{loc}: mapper references module {ref}, which does not exist.")
            elif ref not in upstream:
                errors.append(
                    f"{loc}: mapper references module {ref}, which is not upstream of this module. Cross-route references do not resolve in Make."
                )
        feeder = (module.get("parameters") or {}).get("feeder") if module.get("module") in AGGREGATOR_MODULES else None
        if isinstance(feeder, int):
            if feeder not in known_ids:
                errors.append(f"{loc}: aggregator feeds from module {feeder}, which does not exist.")
            elif feeder not in upstream:
                errors.append(f"{loc}: aggregator feeder {feeder} is not an upstream module.")
        if module.get("onerror"):
            if not in_handler:
                chain = module["onerror"]
                if not chain or chain[-1].get("module") not in DIRECTIVES:
                    errors.append(f"{loc}.onerror: the handler must end with a directive (Break, Ignore, Resume, Commit, or Rollback).")
                for child in chain[:-1]:
                    if child.get("module") in DIRECTIVES:
                        errors.append(f"{loc}.onerror: a directive has to be the last module in the handler.")
            check_references(module["onerror"], upstream | {module_id}, f"{loc}.onerror", known_ids, errors, True)
        if module.get("routes"):
            if index != len(flow) - 1:
                errors.append(f"{loc}: a router has to be the last module in its flow. Make does not rejoin routes.")
            for route_index, route in enumerate(module["routes"]):
                check_references(
                    route.get("flow") or [],
                    upstream | {module_id},
                    f"{loc}.routes[{route_index}].flow",
                    known_ids,
                    errors,
                    in_handler,
                )
        if module.get("module") in DIRECTIVES and not in_handler:
            errors.append(f"{loc}: {module['module']} belongs on an error-handler route, not the main flow.")
        upstream.add(module_id)


def validate_blueprint(data: dict, loc: str = "blueprint") -> list[str]:
    errors: list[str] = []
    validator = blueprint_validator()
    for err in sorted(validator.iter_errors(data), key=lambda item: list(item.path)):
        pointer = "/".join(str(part) for part in err.path) or "(root)"
        errors.append(f"{loc}: schema {pointer}: {err.message}")
    if errors:
        return errors
    if "subflows" in data or "blueprint" in data:
        errors.append(f"{loc}: unwrap UI exports so the file is {{name, flow, metadata}}.")
    collected: list[tuple[str, dict]] = []
    walk_collect(data["flow"], "flow", collected)
    ids = [module["id"] for _, module in collected]
    if len(ids) != len(set(ids)):
        dupes = sorted({item for item in ids if ids.count(item) > 1})
        errors.append(f"{loc}: duplicate module ids {dupes}.")
    known = set(ids)
    for path, module in collected:
        check_module_static(module, f"{loc}: {path} id {module.get('id')}", errors)
    check_secrets(data, loc, errors)
    check_references(data["flow"], set(), "flow", known, errors, False)
    first = data["flow"][0]["module"]
    instant = data["metadata"].get("instant")
    expects_instant = first in INSTANT_TRIGGERS
    if expects_instant and instant is not True:
        errors.append(f"{loc}: {first} scenarios set metadata.instant to true.")
    if not expects_instant and instant is True:
        errors.append(f"{loc}: metadata.instant is true but the first module is not an instant trigger.")
    if "zone" in data["metadata"]:
        errors.append(f"{loc}: remove metadata.zone. It only records the publisher's datacenter.")
    return errors


def validate_scenario_dir(folder: Path) -> list[str]:
    errors: list[str] = []
    for name in REQUIRED_FILES:
        if not (folder / name).is_file():
            errors.append(f"{folder}: missing {name}.")
    if errors:
        return errors
    blueprint, err = load_json(folder / "blueprint.json")
    if err:
        return [err]
    errors.extend(validate_blueprint(blueprint, loc=str(folder / "blueprint.json")))
    sample, sample_err = load_json(folder / "sample-input.json")
    if sample_err:
        errors.append(sample_err)
    elif not isinstance(sample, (dict, list)):
        errors.append(f"{folder / 'sample-input.json'}: sample input must be a JSON object or array.")
    else:
        check_secrets(sample, str(folder / "sample-input.json"), errors)
    readme = (folder / "README.md").read_text(encoding="utf-8")
    for marker in REQUIRED_README_MARKERS:
        if marker not in readme:
            errors.append(f"{folder / 'README.md'}: missing {marker!r}.")
    if "client work" in readme.lower() and "Not client work." not in readme:
        errors.append(f"{folder / 'README.md'}: portfolio demos must say they are not client work.")
    diagram = (folder / "diagram.mmd").read_text(encoding="utf-8")
    if "flowchart" not in diagram:
        errors.append(f"{folder / 'diagram.mmd'}: expected a Mermaid flowchart.")
    png = (folder / "diagram.png").read_bytes()[:8]
    if png != b"\x89PNG\r\n\x1a\n":
        errors.append(f"{folder / 'diagram.png'}: not a PNG.")
    return errors


def validate_catalog(min_scenarios: int = 1) -> list[str]:
    errors: list[str] = []
    catalog_path = ROOT / "catalog.json"
    catalog, err = load_json(catalog_path)
    if err:
        return [err]
    validator = catalog_validator()
    for item in sorted(validator.iter_errors(catalog), key=lambda problem: list(problem.path)):
        pointer = "/".join(str(part) for part in item.path) or "(root)"
        errors.append(f"catalog.json: schema {pointer}: {item.message}")
    if errors:
        return errors
    scenarios = catalog["scenarios"]
    if len(scenarios) < min_scenarios:
        errors.append(f"catalog.json: expected at least {min_scenarios} scenarios, found {len(scenarios)}.")
    ids = [item["id"] for item in scenarios]
    if len(ids) != len(set(ids)):
        errors.append("catalog.json: duplicate scenario ids.")
    folders = {item["id"]: item for item in scenarios}
    found_dirs = []
    scenarios_root = ROOT / "scenarios"
    if scenarios_root.is_dir():
        for category_dir in sorted(p for p in scenarios_root.iterdir() if p.is_dir()):
            for scenario_dir in sorted(p for p in category_dir.iterdir() if p.is_dir()):
                found_dirs.append(scenario_dir)
    found_ids = []
    for folder in found_dirs:
        rel = folder.relative_to(ROOT).as_posix()
        scenario_id = folder.name
        found_ids.append(scenario_id)
        entry = folders.get(scenario_id)
        if entry is None:
            errors.append(f"{rel}: folder is not listed in catalog.json.")
            continue
        if entry["path"] != rel:
            errors.append(f"{rel}: catalog path is {entry['path']}.")
        if entry["category"] != folder.parent.name:
            errors.append(f"{rel}: catalog category {entry['category']} does not match the folder.")
        if entry["screenshot"] != f"{rel}/diagram.png":
            errors.append(f"{rel}: catalog screenshot must be {rel}/diagram.png.")
        if entry["test_status"] != TEST_STATUS:
            errors.append(f"{rel}: test_status must be the structural-validation string.")
        errors.extend(validate_scenario_dir(folder))
    missing = sorted(set(ids) - set(found_ids))
    for scenario_id in missing:
        errors.append(f"catalog.json: {scenario_id} has no scenario folder.")
    return errors


def dump_allowlist(path: Path | None = None) -> Path:
    target = path or (ROOT / "schema" / "modules.allowlist.json")
    payload = {
        "note": (
            "Allowlist of Make module identifiers used by this library. "
            "See makebp/allowlist.py for the source of each id. "
            "Do not add a module id that has not been seen in a real export, "
            "Make's scenario-building examples, or the public blueprint corpus."
        ),
        "modules": MODULES,
    }
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return target
