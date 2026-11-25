# Company domain lookup logged to a sheet

Portfolio demo by Mustafa ([mustafaautomation](https://github.com/mustafaautomation)). Not client work. Connect your own accounts after import. Live walkthroughs, when published, sit on a subdomain of quvantic.com.

**Category:** Scraping and enrichment  
**Difficulty:** intermediate  
**Apps:** Webhooks, HTTP, Google Sheets, Slack  
**Test status:** documented blueprint, structurally validated

## Problem

Enrichment vendors differ and their Make modules are not in the allowlist this library trusts. This demo shows the shape: a webhook with a domain, an HTTP GET, a sheet row, and Slack. The URL is example.com until you paste the vendor URL you are allowed to call.

## Who it's for

SDRs who want the HTTP shape without a guessed module id.

## Module-by-module walkthrough

Ids match the blueprint. A router runs every route whose filter passes. An error handler runs only when that module throws.

### 1. Catch the webhook

`gateway:CustomWebHook` · Custom webhook · Webhooks

The form posts a domain.

No mapped fields. Configure the module after import, or it only passes the bundle through.

### 2. Look up the domain

`http:ActionSendData` · Make a request · HTTP

Replace example.com with the vendor URL. Keep the domain in the query string.

- `url`: `"https://example.com"`
- `serializeUrl`: `false`
- `method`: `"get"`
- `headers`: `[{"name": "Accept", "value": "application/json"}, {"name": "Authorization", "value": "Bearer YOUR_API_KEY"}]`
- `qs`: `[{"name": "domain", "value": "{{1.domain}}"}]`
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
- `values`: `{"0": "{{now}}", "1": "{{1.domain}}", "2": "{{2.statusCode}}"}`

### 6. Tell Slack

`slack:CreateMessage` · Send a message · Slack

The channel sees the outcome.

- `channelWType`: `"list"`
- `channelType`: `"public"`
- `channel`: `""`
- `text`: `"Lookup for {{1.domain}} returned status {{2.statusCode}}."`
- `mrkdwn`: `true`
- `parse`: `false`

## Diagram

![Scenario flow](diagram.png)

```mermaid
flowchart LR
  hook(("1 · Catch the webhook"))
  call(("2 · Look up the domain"))
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
   - B domain
   - C status
5. Select that spreadsheet and sheet on every Google Sheets module. The ids are blank in the file.
6. Run once with the bundled `sample-input.json`. Fictional payload. Paste it into the first module when you run the scenario once.
7. Check the output bundle of each module before you turn the schedule on.

## Connections

- **Slack** — create a connection and select it on every Slack module. The blueprint leaves `__IMTCONN__` unset on purpose.
- **Google Sheets** — create a connection and select it on every Google Sheets module. The blueprint leaves `__IMTCONN__` unset on purpose.

Replace these placeholders in the HTTP modules before the first live run:
- `YOUR_API_KEY`

Nothing in the file is a live connection id, webhook URL, or API key. Make rejects another team's connection id at import, so the slots are empty on purpose.

## Data mapping

References use the module id: `{{1.subject}}` is the `subject` field of module 1. Sheets columns are zero-based and backticked (`{{1.`0`}}` is column A) so a renamed header does not break the map.

- The HTTP module uses parseResponse. Map the id from the output bundle you see on the first run if the path differs.

## Error handling

Scenario settings: `maxErrors` 3, `dlq` true, `sequential` false, `autoCommit` true. After this many consecutive failed runs Make deactivates a scheduled scenario.

- Module 2 (Look up the domain) handles errors with `builtin:Break`. The API call failed.

## Customization

- Replace every YOUR_* token before the first live call. Do not commit the filled-in blueprint.
- Swap any `YOUR_*` value for the id from your own account. Do not commit the filled-in file.
- Duplicate the scenario before you change the prompt, so you can diff against this demo later.

## Time saved

About 2 minutes a domain once the URL points at a real vendor.

## Files

| File | What it is |
| --- | --- |
| `blueprint.json` | Import this into Make. |
| `sample-input.json` | Fictional bundle for the first run. |
| `diagram.png` | Flow diagram. |
| `diagram.mmd` | Mermaid source for the same flow. |
