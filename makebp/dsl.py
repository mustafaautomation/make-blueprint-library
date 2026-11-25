"""Small helpers for authoring scenario specs.

Mapper strings refer to other steps by key: ``{{gmail.subject}}`` is rewritten
to ``{{<id>.subject}}`` once ids are assigned. Keys are unique inside a scenario.
"""

from __future__ import annotations


def M(
    key: str,
    module: str,
    name: str,
    why: str,
    mapper: dict | None = None,
    parameters: dict | None = None,
    onerror: dict | None = None,
    feeder: str | None = None,
    notes: list[str] | None = None,
    filter: dict | None = None,
) -> dict:
    return {
        "key": key,
        "module": module,
        "name": name,
        "why": why,
        "mapper": {} if mapper is None else mapper,
        "parameters": {} if parameters is None else parameters,
        "onerror": onerror,
        "feeder": feeder,
        "notes": notes or [],
        "filter": filter,
        "routes": None,
    }


def router(key: str, name: str, why: str, routes: list[dict]) -> dict:
    return {
        "key": key,
        "module": "builtin:BasicRouter",
        "name": name,
        "why": why,
        "mapper": None,
        "parameters": {},
        "onerror": None,
        "feeder": None,
        "notes": [],
        "filter": None,
        "routes": routes,
    }


def route(name: str, why: str, steps: list[dict], when: dict | None = None) -> dict:
    return {"name": name, "why": why, "steps": steps, "filter": when}


def when(name: str, left: str, op: str, right: str | None = None) -> dict:
    condition = {"a": left, "o": op}
    if right is not None:
        condition["b"] = right
    return {"name": name, "conditions": [[condition]]}


def when_all(name: str, conditions: list[dict]) -> dict:
    return {"name": name, "conditions": [conditions]}


def cond(left: str, op: str, right: str | None = None) -> dict:
    item = {"a": left, "o": op}
    if right is not None:
        item["b"] = right
    return item


def handler(directive: str, why: str, mapper: dict | None = None, notify: dict | None = None) -> dict:
    return {"directive": directive, "why": why, "mapper": mapper or {}, "notify": notify}


def retry(why: str, notify: dict | None = None, count: int = 3, interval: int = 15) -> dict:
    return handler(
        "builtin:Break",
        why,
        mapper={"retry": True, "count": count, "interval": interval},
        notify=notify,
    )


def skip(why: str, notify: dict | None = None) -> dict:
    return handler("builtin:Ignore", why, notify=notify)


def resume(why: str, mapper: dict, notify: dict | None = None) -> dict:
    return handler("builtin:Resume", why, mapper=mapper, notify=notify)


def commit(why: str, notify: dict | None = None) -> dict:
    return handler("builtin:Commit", why, notify=notify)


def chat(system: str, user: str, max_tokens: int = 700, model: str = "gpt-4o-mini") -> dict:
    return {
        "select": "chat",
        "model": model,
        "max_tokens": str(max_tokens),
        "temperature": "0.2",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }


def claude(system: str, user: str, max_tokens: int = 800, model: str = "claude-sonnet-4-5") -> dict:
    return {
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }


def row(*values: str) -> dict:
    return {str(index): value for index, value in enumerate(values)}


def sheets_add(*values: str) -> dict:
    return {
        "from": "drive",
        "mode": "select",
        "spreadsheetId": "",
        "sheetId": "",
        "includesHeaders": True,
        "insertDataOption": "INSERT_ROWS",
        "valueInputOption": "USER_ENTERED",
        "values": row(*values),
    }


def sheets_update(row_number: str, values: dict) -> dict:
    return {
        "mode": "map",
        "spreadsheetId": "",
        "sheetId": "",
        "rowNumber": row_number,
        "tableFirstRow": "A1:Z1",
        "includesHeaders": True,
        "valueInputOption": "USER_ENTERED",
        "values": values,
    }


def sheets_watch(limit: int = 10) -> dict:
    return {
        "mode": "select",
        "from": "drive",
        "spreadsheetId": "",
        "sheetId": "",
        "includesHeaders": True,
        "tableFirstRow": "A1:Z1",
        "limit": limit,
        "valueRenderOption": "FORMATTED_VALUE",
        "dateTimeRenderOption": "FORMATTED_STRING",
    }


def sheets_filter(column: str, op: str, value: str, limit: int = 5) -> dict:
    return {
        "from": "drive",
        "spreadsheetId": "",
        "sheetId": "",
        "includesHeaders": True,
        "tableFirstRow": "A1:Z1",
        "valueRenderOption": "FORMATTED_VALUE",
        "dateTimeRenderOption": "FORMATTED_STRING",
        "limit": limit,
        "filter": [[{"a": column, "o": op, "b": value}]],
    }


def gmail_query(query: str, limit: int = 5) -> dict:
    return {"q": query, "maxResults": limit}


def gmail_message(to: str, subject: str, html: str) -> dict:
    return {
        "from": "",
        "to": [to],
        "cc": [],
        "bcc": [],
        "replyTo": "",
        "subject": subject,
        "html": html,
        "attachments": [],
    }


def slack(text: str) -> dict:
    return {
        "channelWType": "list",
        "channelType": "public",
        "channel": "",
        "text": text,
        "mrkdwn": True,
        "parse": False,
    }


def http(method: str, url: str, data: str = "", headers: list | None = None, query: list | None = None) -> dict:
    if headers is None:
        headers = [
            {"name": "Accept", "value": "application/json"},
            {"name": "Content-Type", "value": "application/json"},
            {"name": "Authorization", "value": "Bearer YOUR_API_KEY"},
        ]
    return {
        "url": url,
        "serializeUrl": False,
        "method": method.lower(),
        "headers": headers,
        "qs": query or [],
        "bodyType": "raw",
        "parseResponse": True,
        "contentType": "application/json",
        "data": data,
        "timeout": "",
        "shareCookies": False,
        "ca": "",
        "rejectUnauthorized": True,
        "followRedirect": True,
        "useQuerystring": False,
        "gzip": True,
        "useMtls": False,
        "followAllRedirects": False,
    }


def json_headers() -> list:
    return [
        {"name": "Accept", "value": "application/json"},
        {"name": "Content-Type", "value": "application/json"},
    ]


def bearer_headers(extra: list | None = None) -> list:
    headers = json_headers() + [{"name": "Authorization", "value": "Bearer YOUR_API_KEY"}]
    if extra:
        headers.extend(extra)
    return headers


def hubspot_contact(email: str, first: str, last: str, company: str = "", phone: str = "") -> dict:
    payload = {"email": email, "firstname": first, "lastname": last}
    if company:
        payload["company"] = company
    if phone:
        payload["phone"] = phone
    return payload


def twilio(to: str, body: str) -> dict:
    return {"to": to, "from": "YOUR_TWILIO_NUMBER", "message": body}


def airtable_record(fields: dict) -> dict:
    return {"baseId": "", "tableId": "", "fields": fields}


def notion_page(title: str, content: str) -> dict:
    return {"select": "page", "title": title, "content": content}


def set_var(name: str, value: str, scope: str = "roundtrip") -> dict:
    return {"name": name, "scope": scope, "value": value}


def scenario(**kwargs) -> dict:
    required = [
        "id",
        "title",
        "category",
        "difficulty",
        "tags",
        "apps",
        "description",
        "problem",
        "audience",
        "time_saved",
        "schedule",
        "sample",
        "steps",
    ]
    missing = [key for key in required if key not in kwargs]
    if missing:
        raise ValueError(f"scenario missing {missing}")
    kwargs.setdefault("phase", 2)
    kwargs.setdefault("featured_rank", None)
    kwargs.setdefault("customization", [])
    kwargs.setdefault("mapping", [])
    kwargs.setdefault("sheet_columns", [])
    kwargs.setdefault("sample_note", "Fictional payload. Paste it into the first module when you run the scenario once.")
    kwargs.setdefault("sequential", False)
    kwargs.setdefault("max_errors", 3)
    return kwargs
