# CSAT webhook logged to a sheet

Portfolio demo by Mustafa ([mustafaautomation](https://github.com/mustafaautomation)). Not client work. Connect your own accounts after import. Live walkthroughs, when published, sit on a subdomain of quvantic.com.

**Category:** Support  
**Difficulty:** beginner  
**Apps:** Webhooks, Google Sheets, Slack  
**Test status:** documented blueprint, structurally validated

## Problem

CSAT responses go to a vendor dashboard. This demo logs score, comment, and ticket id, and pings Slack for a score of 2 or less. It does not call the vendor back. The HTTP module is omitted on purpose: the webhook is the whole event.

## Who it's for

Support leads who can point their CSAT tool at a webhook.

## Module-by-module walkthrough

Ids match the blueprint. A router runs every route whose filter passes. An error handler runs only when that module throws.

### 1. Catch the CSAT event

`gateway:CustomWebHook` · Custom webhook · Webhooks

The survey tool posts score, comment, and ticket id.

No mapped fields. Configure the module after import, or it only passes the bundle through.

### 2. Acknowledge with a no-op status fetch

`http:ActionSendData` · Make a request · HTTP

GET example.com so the scenario shows where a follow-up API call would sit. Replace it with your help desk if you want to tag the ticket.

- `url`: `"https://example.com"`
- `serializeUrl`: `false`
- `method`: `"get"`
- `headers`: `[{"name": "Accept", "value": "application/json"}]`
- `qs`: `[]`
- `bodyType`: `"raw"`
- `parseResponse`: `true`
- `contentType`: `"application/json"`
- `data`: `""`
- `timeout`: `""`
- `shareCookies`: `false`
- `ca`: `""`
- `rejectUnauthorized`: `true`
- `followRedirect`: `true`
- `useQuerystring`: `false`
- `gzip`: `true`
- `useMtls`: `false`
- `followAllRedirects`: `false`

### 3. Alert API — error handler

`slack:CreateMessage` · Send a message · Slack

API call failed.

- `channelWType`: `"list"`
- `channelType`: `"public"`
- `channel`: `""`
- `text`: `"API call failed."`
- `mrkdwn`: `true`
- `parse`: `false`

### 4. Retry (Break) — error handler

`builtin:Break` · Retry (Break) · Flow control

The API call failed.

- `retry`: `true`
- `count`: `3`
- `interval`: `15`

### 5. Log the call

`google-sheets:addRow` · Add a row · Google Sheets

A row even when the later Slack filter blocks.

- `from`: `"drive"`
- `mode`: `"select"`
- `spreadsheetId`: `""`
- `sheetId`: `""`
- `includesHeaders`: `true`
- `insertDataOption`: `"INSERT_ROWS"`
- `valueInputOption`: `"USER_ENTERED"`
- `values`: `{"0": "{{now}}", "1": "{{1.ticket_id}}", "2": "{{1.score}}", "3": "{{1.comment}}"}`

### 6. Tell Slack

`slack:CreateMessage` · Send a message · Slack

The channel sees the outcome.

Filter **Score of 2 or less**: `[[{"a": "{{1.score}}", "o": "number:lessequal", "b": "2"}]]`

- `channelWType`: `"list"`
- `channelType`: `"public"`
- `channel`: `""`
- `text`: `"*Low CSAT* ticket {{1.ticket_id}} scored {{1.score}}. {{1.comment}}"`
- `mrkdwn`: `true`
- `parse`: `false`

## Diagram

![Scenario flow](diagram.png)

```mermaid
flowchart LR
  hook(("1 · Catch the CSAT event"))
  call(("2 · Acknowledge with a no-op status fetch"))
  hook --> call
  call -->|"error"| call_alert
  call_alert(("3 · Alert API"))
  call_directive(("4 · Retry (Break)"))
  call_alert --> call_directive
  log(("5 · Log the call"))
  call --> log
  ping(("6 · Tell Slack"))
  log --> ping
```

## Setup

1. In Make, create a scenario, open the three-dot menu at the bottom of the editor, and choose **Import Blueprint**. Select `blueprint.json`.
2. Open every red module and pick or create the connection. Red means the account is not selected yet.
3. Schedule: Immediately.
4. Create the spreadsheet tab this scenario expects, with a header row in row 1:
   - A received_at
   - B ticket
   - C score
   - D comment
5. Select that spreadsheet and sheet on every Google Sheets module. The ids are blank in the file.
6. Run once with the bundled `sample-input.json`. Fictional payload. Paste it into the first module when you run the scenario once.
7. Check the output bundle of each module before you turn the schedule on.

## Connections

- **Slack** — create a connection and select it on every Slack module. The blueprint leaves `__IMTCONN__` unset on purpose.
- **Google Sheets** — create a connection and select it on every Google Sheets module. The blueprint leaves `__IMTCONN__` unset on purpose.

Nothing in the file is a live connection id, webhook URL, or API key. Make rejects another team's connection id at import, so the slots are empty on purpose.

## Data mapping

References use the module id: `{{1.subject}}` is the `subject` field of module 1. Sheets columns are zero-based and backticked (`{{1.`0`}}` is column A) so a renamed header does not break the map.

- The HTTP module uses parseResponse. Map the id from the output bundle you see on the first run if the path differs.

## Error handling

Scenario settings: `maxErrors` 3, `dlq` true, `sequential` false, `autoCommit` true. After this many consecutive failed runs Make deactivates a scheduled scenario.

- Module 2 (Acknowledge with a no-op status fetch) handles errors with `builtin:Break`. The API call failed.
- Module 6 runs only when filter **Score of 2 or less** passes. A blocked bundle stops on that path. It is not an error.

## Customization

- Replace every YOUR_* token before the first live call. Do not commit the filled-in blueprint.
- Duplicate the scenario before you change the prompt, so you can diff against this demo later.

## Time saved

About 5 minutes a detractor of finding the response in a dashboard.

## Files

| File | What it is |
| --- | --- |
| `blueprint.json` | Import this into Make. |
| `sample-input.json` | Fictional bundle for the first run. |
| `diagram.png` | Flow diagram. |
| `diagram.mmd` | Mermaid source for the same flow. |
