"""Turn compact records into full scenario specs for the long tail of the catalog.

Each record still carries its own problem, prompt, and sample. The helpers only
share the module shape (watch, score, parse, route), which is how these
automations are actually built in Make.
"""

from __future__ import annotations

from makebp.dsl import (
    M,
    chat,
    claude,
    gmail_message,
    gmail_query,
    http,
    hubspot_contact,
    json_headers,
    notion_page,
    retry,
    route,
    router,
    scenario,
    sheets_add,
    sheets_filter,
    sheets_update,
    sheets_watch,
    skip,
    slack,
    twilio,
    when,
)
from makebp.specs.common import alert


def _notes(record: dict, mapping: list[str], tips: list[str]) -> dict:
    copy = dict(record)
    copy["mapping"] = list(record.get("mapping") or []) + mapping
    copy["customization"] = list(record.get("customization") or []) + tips
    return copy


def _base(record: dict, steps: list, sample: dict, columns: list[str] | None = None) -> dict:
    return scenario(
        id=record["id"],
        title=record["title"],
        category=record["category"],
        phase=2,
        difficulty=record["difficulty"],
        tags=record["tags"],
        apps=record["apps"],
        description=record["description"],
        problem=record["problem"].strip(),
        audience=record["audience"].strip(),
        time_saved=record["time_saved"].strip(),
        schedule=record["schedule"],
        sample=sample,
        sample_note=record.get("sample_note", "Fictional payload. Paste it into the first module when you run the scenario once."),
        sheet_columns=columns or record.get("sheet_columns") or [],
        mapping=record.get("mapping") or [],
        customization=record.get("customization") or [],
        steps=steps,
        sequential=record.get("sequential", False),
    )


def gmail_flow(record: dict) -> dict:
    gate = record.get("gate")
    slack_step = M(
        "ping",
        "slack:CreateMessage",
        record.get("slack_name", "Post the result"),
        record.get("slack_why", "The channel sees the extracted fields, not the whole email."),
        mapper=slack(record["slack"]),
        filter=when(gate[0], gate[1], gate[2], gate[3]) if gate else when("Model returned text", "{{model.result}}", "exist"),
    )
    steps = [
        M("mail", "google-email:TriggerWatchEmails", record["watch_name"], record["watch_why"],
          mapper=gmail_query(record["query"], record.get("limit", 5))),
        M("model", "openai-gpt-3:CreateCompletion", record["model_name"], record["model_why"],
          mapper=chat(record["system"], record["prompt"] + "\n\nFrom: {{mail.from}}\nSubject: {{mail.subject}}\n\n{{mail.text}}", record.get("tokens", 400)),
          onerror=retry(record.get("retry", "The model failed. Retry before writing a bad row."),
                        notify=alert("Alert the model failure", record.get("alert", "Model failed for {{mail.subject}}.")))),
        M("parsed", "json:ParseJSON", "Parse the JSON",
          "The prompt asks for one JSON object. This module exposes its keys.",
          mapper={"json": "{{model.result}}"}),
        M("log", "google-sheets:addRow", "Log the row",
          record.get("log_why", "Every message is logged, whether or not Slack fires."),
          mapper=sheets_add(*record["row"])),
        slack_step,
    ]
    sample = {
        "from": record.get("sender", record.get("from", "person@example.com")),
        "subject": record["subject"],
        "text": record["body"],
    }
    record = _notes(record, [
        "Parsed JSON keys match the prompt. Sheet columns are positional, starting at values[\"0\"].",
        "The Slack filter is on the last module, so the sheet row is written even when Slack does not fire.",
    ], [
        f"Point the Gmail query at your label. The demo uses `{record['query']}`.",
        "Keep the model on JSON-only output. A preamble breaks Parse JSON.",
    ])
    return _base(record, steps, sample, record["columns"])


def hook_score(record: dict) -> dict:
    high_steps = _high_steps(record)
    low_steps = [
        M("low", "slack:CreateMessage", record.get("low_name", "Note the low score"),
          record.get("low_why", "So the channel can see the lead was stored and not contacted."),
          mapper=slack(record["low_slack"])),
    ]
    steps = [
        M("lead", "gateway:CustomWebHook", record["hook_name"], record["hook_why"]),
        M("model", "openai-gpt-3:CreateCompletion", record["model_name"], record["model_why"],
          mapper=chat(record["system"], record["prompt"], record.get("tokens", 300)),
          onerror=retry("Scoring failed. Retry before the router picks a side.",
                        notify=alert("Alert scoring", record.get("alert", "Scoring failed.")))),
        M("parsed", "json:ParseJSON", "Parse the score",
          "Exposes the numeric field the routes compare.",
          mapper={"json": "{{model.result}}"}),
        M("log", "google-sheets:addRow", "Log it",
          "The row is written before the route, so both outcomes have an audit line.",
          mapper=sheets_add(*record["row"])),
        router("band", record["router_name"], record["router_why"], [
            route(record["high_route"], record["high_why"], high_steps,
                  when(record["high_filter"], record["score_ref"], "number:greaterorequal", str(record["threshold"]))),
            route(record["low_route"], record["low_why_route"], low_steps,
                  when(record["low_filter"], record["score_ref"], "number:less", str(record["threshold"]))),
        ]),
    ]
    record = _notes(record, [
        f"Routes compare `{record['score_ref']}` with {record['threshold']} using number operators, so the two routes do not both run.",
    ], [
        "Edit the rubric in the system prompt before you reuse this for a different offer.",
        "The webhook parameters are empty. Make creates the hook when you import.",
    ])
    return _base(record, steps, record["sample"], record["columns"])


def _maybe_ping(record: dict, steps: list) -> list:
    if record.get("high_slack"):
        steps.append(M("high_ping", "slack:CreateMessage", "Tell the channel", record.get("high_ping_why", "The channel sees why this route ran."),
                       mapper=slack(record["high_slack"])))
    return steps


def _high_steps(record: dict) -> list:
    kind = record["high_kind"]
    if kind == "slack":
        return [M("high", "slack:CreateMessage", record["high_name"], record["high_step_why"], mapper=slack(record["high_slack"]))]
    if kind == "draft":
        return _maybe_ping(record, [M("high", "google-email:ActionCreateDraft", record["high_name"], record["high_step_why"],
                  mapper=gmail_message(record["draft_to"], record["draft_subject"], record["draft_html"]))])
    if kind == "hubspot":
        return _maybe_ping(record, [M("high", "hubspotcrm:createContact", record["high_name"], record["high_step_why"],
                  mapper=hubspot_contact(record["hs_email"], record["hs_first"], record["hs_last"], record.get("hs_company", "")),
                  onerror=retry("HubSpot rejected the contact.", notify=alert("Alert HubSpot", record.get("alert", "HubSpot create failed."))))])
    if kind == "twilio":
        return _maybe_ping(record, [M("high", "twilio:SendSMS", record["high_name"], record["high_step_why"],
                  mapper=twilio(record["sms_to"], record["sms_body"]),
                  onerror=retry("Twilio failed.", notify=alert("Alert SMS", "SMS failed.")))])
    if kind == "notion":
        return _maybe_ping(record, [M("high", "notion:createAPage", record["high_name"], record["high_step_why"],
                  mapper=notion_page(record["notion_title"], record["notion_body"]))])
    raise ValueError(record["id"])


def digest_flow(record: dict) -> dict:
    steps = [
        M("rows", "google-sheets:filterRows", record["search_name"], record["search_why"],
          mapper=sheets_filter(record["col"], record.get("op", "text:equal"), record["match"], record.get("limit", 25))),
        M("digest", "util:TextAggregator", "Join the rows",
          "One text bundle. The feeder is the search.",
          feeder="rows",
          mapper={"value": record["line"]}),
        M("model", "openai-gpt-3:CreateCompletion", record["model_name"], record["model_why"],
          mapper=chat(record["system"], "{{digest.text}}", record.get("tokens", 450)),
          onerror=retry("The narrative failed.", notify=alert("Alert narrative", record.get("alert", "Narrative failed.")))),
        M("ping", "slack:CreateMessage", "Post the narrative",
          "Skipped when the search returned nothing.",
          mapper=slack(record["slack"]),
          filter=when("Digest exists", "{{digest.text}}", "exist")),
    ]
    if record.get("email_to"):
        steps.append(M("mail", "google-email:ActionSendEmail", "Email the same note",
                       "Same text as Slack. Same empty-digest filter.",
                       mapper=gmail_message(record["email_to"], record["email_subject"], "<p>{{model.result}}</p><pre>{{digest.text}}</pre>"),
                       filter=when("Digest exists", "{{digest.text}}", "exist")))
    sample = {"note": record.get("sample_note_body", "This scenario reads the sheet. Add rows that match the filter, then run once.")}
    record = _notes(record, [
        f"Column {record['col']} is filtered with {record.get('op', 'text:equal')} against {record['match']}.",
        "Aggregator output is {{digest.text}}. The model is told to use only that text.",
    ], ["Schedule it for the morning you actually read the update. The search module does not watch the sheet."])
    return _base(record, steps, sample, record["columns"])


def rss_flow(record: dict) -> dict:
    steps = [
        M("post", "rss:TriggerNewArticle", "Watch the feed", record["watch_why"],
          mapper={"url": record["feed"], "maxResults": record.get("limit", 2)}),
        M("model", "openai-gpt-3:CreateCompletion", record["model_name"], record["model_why"],
          mapper=chat(record["system"], "Title: {{post.title}}\n{{post.url}}\n{{post.description}}", record.get("tokens", 350)),
          onerror=retry("The model failed on this item.", notify=alert("Alert feed", "Feed item failed: {{post.title}}"))),
        M("log", "google-sheets:addRow", "Archive the item",
          "Keeps the title and the model text.",
          mapper=sheets_add("{{now}}", "{{post.title}}", "{{post.url}}", "{{model.result}}")),
        M("ping", "slack:CreateMessage", "Post it",
          record.get("slack_why", "The channel gets the model text and the link."),
          mapper=slack(record["slack"])),
    ]
    sample = {"title": record["sample_title"], "url": record.get("sample_url", "https://example.com/post"), "description": record["sample_description"]}
    record = _notes(record, [
        "RSS fields used here are title, url, and description. Confirm them on the first bundle.",
    ], [f"Replace the feed URL. The demo points at `{record['feed']}`."])
    return _base(record, steps, sample, record["columns"])


def row_flow(record: dict) -> dict:
    steps = [
        M("row", "google-sheets:watchRows", record["watch_name"], record["watch_why"], parameters=sheets_watch(record.get("limit", 5))),
        M("model", record.get("model_module", "openai-gpt-3:CreateCompletion"), record["model_name"], record["model_why"],
          mapper=_model_mapper(record),
          onerror=retry("The model failed. Leave the row unchanged.",
                        notify=alert("Alert row", record.get("alert", "Row model failed.")))),
        M("save", "google-sheets:updateRow", "Write the result back",
          "Writes one column on the same row. Other columns are left alone.",
          mapper=sheets_update("{{row.__ROW_NUMBER__}}", {record.get("out_col", "1"): "{{model.result}}"}),
          filter=when("Result exists", "{{model.result}}", "exist")),
    ]
    if record.get("slack"):
        steps.append(M("ping", "slack:CreateMessage", "Tell the channel", record.get("slack_why", "Optional ping after the write."),
                       mapper=slack(record["slack"]),
                       filter=when(record["gate_name"], record["gate_ref"], record["gate_op"], record["gate_value"]) if record.get("gate_ref") else None))
    sample = {"0": record["sample_a"], "1": record.get("sample_b", "")}
    record = _notes(record, [
        "Column A on a watch-rows bundle is {{row.`0`}}. The update writes back to {{row.__ROW_NUMBER__}}.",
        "Only the output column is in the update mapper, so other cells on the row stay as they are.",
    ], ["If the watch module also fires when you write the result, exclude that column or the scenario loops."])
    return _base(record, steps, sample, record["columns"])


def _model_mapper(record: dict) -> dict:
    module = record.get("model_module", "openai-gpt-3:CreateCompletion")
    user = record["prompt"]
    if module == "anthropic-claude:createAMessage":
        return claude(record["system"], user, record.get("tokens", 400))
    if module == "gemini-ai:createACompletionGeminiPro":
        return {"model": "gemini-1.5-pro", "prompt": record["system"] + "\n\n" + user}
    return chat(record["system"], user, record.get("tokens", 400))


def hook_http(record: dict) -> dict:
    if record.get("use_apify"):
        call = M("call", "apify:runActor", record["http_name"], record["http_why"],
                 mapper={"actorId": "{{hook.actor_id}}", "inputBody": "{{hook.input}}"},
                 onerror=retry(record.get("retry", "The actor failed to start."),
                               notify=alert("Alert Apify", record.get("alert", "Apify run failed."))))
    else:
        call = M("call", "http:ActionSendData", record["http_name"], record["http_why"],
                 mapper=http(record["method"], record["url"], data=record.get("body", ""), headers=record.get("headers", json_headers()), query=record.get("query")),
                 parameters={"handleErrors": True},
                 onerror=retry(record.get("retry", "The API call failed."), notify=alert("Alert API", record.get("alert", "API call failed."))))
    steps = [
        M("hook", "gateway:CustomWebHook", record["hook_name"], record["hook_why"]),
        call,
        M("log", "google-sheets:addRow", "Log the call",
          record.get("log_why", "A row even when the later Slack filter blocks."),
          mapper=sheets_add(*record["row"])),
        M("ping", "slack:CreateMessage", record.get("slack_name", "Tell Slack"),
          record.get("slack_why", "The channel sees the outcome."),
          mapper=slack(record["slack"]),
          filter=when(record["gate_name"], record["gate_left"], record["gate_op"], record["gate_right"]) if record.get("gate_left") else None),
    ]
    record = _notes(record, [
        "The HTTP module uses parseResponse. Map the id from the output bundle you see on the first run if the path differs.",
    ], ["Replace every YOUR_* token before the first live call. Do not commit the filled-in blueprint."])
    return _base(record, steps, record["sample"], record["columns"])


def sheet_each(record: dict) -> dict:
    action = record["action"]
    if action == "sms":
        act = M("act", "twilio:SendSMS", record["act_name"], record["act_why"],
                mapper=twilio(record["sms_to"], record["sms_body"]),
                onerror=skip("One bad number should not stop the rest of the rows.", notify=alert("Alert SMS", "SMS failed for a reminder row.")))
    elif action == "draft":
        act = M("act", "google-email:ActionCreateDraft", record["act_name"], record["act_why"],
                mapper=gmail_message(record["draft_to"], record["draft_subject"], record["draft_html"]))
    elif action == "slack":
        act = M("act", "slack:CreateMessage", record["act_name"], record["act_why"], mapper=slack(record["slack"]))
    else:
        raise ValueError(record["id"])
    steps = [
        M("rows", "google-sheets:filterRows", record["search_name"], record["search_why"],
          mapper=sheets_filter(record["col"], "text:equal", record["match"], record.get("limit", 20))),
        act,
    ]
    sample = {"note": "Reads the sheet. Rows whose filter column matches are each processed."}
    record = _notes(record, [
        f"Each matching row is its own bundle. Column letters in the filter are the sheet's own filter, not a scenario filter.",
    ], ["Clear or change the flag column inside the action if you do not want the same row processed again tomorrow."])
    return _base(record, steps, sample, record["columns"])


def hook_iter(record: dict) -> dict:
    steps = [
        M("hook", "gateway:CustomWebHook", record["hook_name"], record["hook_why"]),
        M("item", "builtin:BasicFeeder", "One bundle per item",
          record["iter_why"],
          mapper={"array": record["array"]}),
        M("line", "google-sheets:addRow", "Write the item",
          record.get("log_why", "One row per item."),
          mapper=sheets_add(*record["row"])),
        M("digest", "util:TextAggregator", "Summarize the batch",
          "Feeds on the iterator so Slack gets one message.",
          feeder="item",
          mapper={"value": record["line"]}),
        M("ping", "slack:CreateMessage", "Post the batch",
          "After every row is written.",
          mapper=slack(record["slack"]),
          onerror=skip("Slack failed. The rows stay.", notify=None)),
    ]
    record = _notes(record, [
        "The iterator's fields are the object keys inside the array. The aggregator feeds on the iterator, not on the sheet.",
    ], ["If the array is nested under a different key, change the iterator's array mapping and nothing else."])
    return _base(record, steps, record["sample"], record["columns"])


def agent_flow(record: dict) -> dict:
    steps = [
        M("ask", "gateway:CustomWebHook", "Catch the question", record["hook_why"]),
        M("agent", "ai-local-agent:RunLocalAIAgent", record["agent_name"], record["agent_why"],
          mapper={"systemPrompt": record["system"], "message": "{{ask.message}}", "threadId": "{{ask.thread}}"},
          onerror=retry("The agent failed. Retry once before telling the caller it is down.",
                        notify=alert("Alert agent", "Agent failed."))),
        M("out", "gateway:WebhookRespond", "Return the agent text",
          "Make's example maps the agent output as response. If your first run names the field differently, change this body.",
          mapper={"status": 200, "body": "{{agent.response}}"}),
    ]
    record = _notes(record, [
        "The agent module's connection parameter is makeConnectionId and is left unset.",
        "Tools are attached in the Make agent panel after import. They are not in this file, because tool arms are designer state rather than ordinary routes. The assistant-agent-with-tools scenario is the one that shows tools as routes.",
    ], ["Pass a stable thread id if you want the agent to remember the caller. Leave it blank for a stateless call."])
    return _base(record, steps, record["sample"], record.get("columns"))


BUILDERS = {
    "gmail": gmail_flow,
    "hook_score": hook_score,
    "digest": digest_flow,
    "rss": rss_flow,
    "row": row_flow,
    "hook_http": hook_http,
    "sheet_each": sheet_each,
    "hook_iter": hook_iter,
    "agent": agent_flow,
}


def build_rest(records: list[dict]) -> list[dict]:
    specs = []
    ids = set()
    for record in records:
        if record["id"] in ids:
            raise ValueError(f"duplicate rest id {record['id']}")
        ids.add(record["id"])
        specs.append(BUILDERS[record["kind"]](record))
    return specs
