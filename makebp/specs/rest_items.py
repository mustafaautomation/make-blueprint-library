"""Factories for long-tail records. Callers pass the words that make a scenario specific."""

from __future__ import annotations


def G(**k) -> dict:
    k["kind"] = "gmail"
    k.setdefault("watch_name", "Watch the label")
    k.setdefault("watch_why", "A Gmail filter already applied this label. The scenario does not try to classify the whole inbox.")
    k.setdefault("model_name", "Read the message")
    k.setdefault("model_why", "The system prompt is the rubric. The email is the only source.")
    k.setdefault("prompt", "Email follows.")
    return k


def H(**k) -> dict:
    k["kind"] = "hook_score"
    k.setdefault("hook_name", "Catch the webhook")
    k.setdefault("hook_why", "The form posts JSON to this hook. Parameters stay empty so Make creates the hook on import.")
    k.setdefault("model_name", "Score the payload")
    k.setdefault("model_why", "Returns JSON with a numeric score and a one-sentence reason.")
    k.setdefault("router_name", "Branch on the score")
    k.setdefault("router_why", "The two number filters are mutually exclusive.")
    k.setdefault("high_route", "High")
    k.setdefault("low_route", "Low")
    k.setdefault("high_why", "The score cleared the line.")
    k.setdefault("low_why_route", "The score stayed under the line.")
    k.setdefault("high_filter", "At or above the line")
    k.setdefault("low_filter", "Below the line")
    k.setdefault("score_ref", "{{parsed.score}}")
    k.setdefault("high_name", "Act on the high score")
    k.setdefault("high_step_why", "This module runs only on the high route.")
    k.setdefault("low_slack", "Below the line: {{lead.email}} scored {{parsed.score}}. {{parsed.reason}}")
    return k


def D(**k) -> dict:
    k["kind"] = "digest"
    k.setdefault("search_name", "Read the included rows")
    k.setdefault("search_why", "The first module is a search, so the scenario schedule is what wakes it.")
    k.setdefault("model_name", "Write the note")
    k.setdefault("model_why", "Use only the joined lines. Do not invent a cause.")
    k.setdefault("system", "Write a short operational note from the lines. Five sentences. No new numbers.")
    k.setdefault("col", "D")
    k.setdefault("match", "YES")
    k.setdefault("line", "{{rows.`0`}}: {{rows.`1`}}")
    k.setdefault("slack", "*Update*\n{{model.result}}")
    return k


def RSS(**k) -> dict:
    k["kind"] = "rss"
    k.setdefault("watch_why", "Polls the feed on the scenario schedule.")
    k.setdefault("model_name", "Summarize the item")
    k.setdefault("model_why", "Two sentences and a reason to read it, or to skip it.")
    k.setdefault("columns", ["A received_at", "B title", "C url", "D summary"])
    k.setdefault("slack", "{{model.result}}\n{{post.url}}")
    return k


def ROW(**k) -> dict:
    k["kind"] = "row"
    k.setdefault("watch_name", "Watch new rows")
    k.setdefault("watch_why", "New rows only. The update writes back to the same row.")
    k.setdefault("model_name", "Write the cell")
    k.setdefault("model_why", "The prompt is the whole policy for this column.")
    k.setdefault("system", "Follow the user instructions. Plain text, no preamble.")
    return k


def HTTP(**k) -> dict:
    k["kind"] = "hook_http"
    k.setdefault("hook_name", "Catch the webhook")
    k.setdefault("hook_why", "The other system posts the event here.")
    k.setdefault("http_name", "Call the API")
    k.setdefault("http_why", "The URL and body are the contract. Replace YOUR_* before a live run.")
    k.setdefault("method", "post")
    k.setdefault("slack_name", "Tell Slack")
    return k


def EACH(**k) -> dict:
    k["kind"] = "sheet_each"
    k.setdefault("search_name", "Find rows to send")
    k.setdefault("search_why", "A flag column marks rows that still need this action.")
    k.setdefault("col", "A")
    k.setdefault("match", "YES")
    return k


def AGENT(**k) -> dict:
    k["kind"] = "agent"
    k.setdefault("agent_name", "Run the agent")
    k.setdefault("agent_why", "The system prompt is the job. The message is the webhook field message.")
    k.setdefault("hook_why", "The caller posts message and an optional thread id.")
    return k


def ITER(**k) -> dict:
    k["kind"] = "hook_iter"
    k.setdefault("hook_name", "Catch the batch")
    k.setdefault("hook_why", "The body contains an array. The iterator splits it.")
    k.setdefault("iter_why", "One bundle per element, in order.")
    k.setdefault("array", "{{hook.items}}")
    return k
