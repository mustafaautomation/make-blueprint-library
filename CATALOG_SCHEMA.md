# Catalog schema

`catalog.json` is the index a gallery site can read without parsing every blueprint.

```json
{
  "schema_version": "1.0.0",
  "scenarios": [
    {
      "id": "ai-invoice-gmail-sheets-xero",
      "title": "AI invoice extraction from Gmail to Sheets, Xero, or QuickBooks",
      "category": "invoices-docs",
      "apps": ["Gmail", "OpenAI", "Google Sheets", "Xero", "QuickBooks", "Slack"],
      "difficulty": "intermediate",
      "tags": ["invoices", "gmail", "openai"],
      "path": "scenarios/invoices-docs/ai-invoice-gmail-sheets-xero",
      "description": "One sentence a card can show.",
      "test_status": "documented blueprint, structurally validated",
      "screenshot": "scenarios/invoices-docs/ai-invoice-gmail-sheets-xero/diagram.png"
    }
  ]
}
```

The JSON Schema is `schema/catalog.schema.json`.

## Envelope

| Field | Required | Meaning |
| --- | --- | --- |
| `schema_version` | yes | Always `"1.0.0"` for this document. |
| `scenarios` | yes | Array of scenario objects. Order is category, then title. |

## Scenario object

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | string | Folder name. Lowercase words separated by hyphens. Unique. |
| `title` | string | Same name as the blueprint's `name`. |
| `category` | string | Folder under `scenarios/`. One of the slugs in the root README. |
| `apps` | string array | Products a buyer sees on the card. Includes HTTP targets such as Xero even when the module is `http:ActionSendData`. |
| `difficulty` | string | `beginner`, `intermediate`, or `advanced`. |
| `tags` | string array | Lowercase tags, hyphens allowed. |
| `path` | string | Repo-relative folder, no trailing slash. |
| `description` | string | One sentence. No markdown. |
| `test_status` | string | Always `documented blueprint, structurally validated`. |
| `screenshot` | string | Repo-relative path to `diagram.png`. |

## `test_status`

`documented blueprint, structurally validated` means:

- The file is a Make blueprint (`name`, `flow`, `metadata`).
- Every module id is on the allowlist in `schema/modules.allowlist.json`.
- Mapper references point at real upstream module ids.
- Routers, filters, and error handlers match Make's shape.
- No connection id, live Make webhook URL, or non-example email is in the file.

It does **not** mean the file was imported into a Make account. This library does not call Make's API and does not require a paid plan. A free-account import check is out of scope.

## What a gallery should not invent

Do not treat `apps` as module ids. Do not assume `path` contains only `blueprint.json`. Each folder also has `README.md`, `sample-input.json`, `diagram.mmd`, and `diagram.png`.

These records are portfolio demos by Mustafa (GitHub: mustafaautomation). They are not client work.
