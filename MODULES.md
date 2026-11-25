# Module allowlist

`schema/modules.allowlist.json` is the list of `module` strings this library will put in a blueprint. The validator rejects anything else.

A module is on the list only when its id showed up in one of these:

| Source | What it is |
| --- | --- |
| `integromat/make-skills` | Make's own scenario-building examples. This is where `hubspotcrm:createContact`, `stripe:CreateCharge`, `zendesk:UpdateTicket`, `google-sheets:addRow`, `slack:CreateMessage`, and `ai-local-agent:RunLocalAIAgent` are confirmed, with versions. |
| Public blueprint corpus | Module ids measured across 1,432 public Make exports by the migrate-to-n8n map, plus gists that are real exports (`google-sheets:filterRows`, `http:ActionSendDataAPIKeyAuth`). |
| Import-tested templates | Blueprints shaped like Make's create API and checked against a live import, including `google-email:ActionSendEmail` version 2 and `notion:createDataSourceItem`. |
| Make's public API example | `json:ParseJSON`, from the blueprint example in the Make API docs. |

Versions are the ones those sources shipped. Where a corpus entry did not record a version, the allowlist uses `1`.

## Why some apps are HTTP calls

Shopify, WooCommerce, Pipedrive, GoHighLevel, Calendly, Cal.com, Xero, QuickBooks, and ClickUp are in the scenarios. Their **native module ids were not in the sources above**. Guessing `shopify:watchOrders` or `pipedrive:createPerson` would fail import if the id is wrong.

Those scenarios call the vendor's documented REST API with `http:ActionSendData`, which is a real Make module. The README names the native app and the placeholder (`YOUR_API_KEY`, `YOUR_LIST_ID`, `YOUR_COMPANY_ID`) you replace. After import you can swap the HTTP module for the native one in your own account if you prefer it.

HubSpot create-contact, Zendesk update-ticket, and Stripe's create-charge module are used as native modules because Make's own examples name them. Stripe **history** is still an HTTP GET to `/v1/balance_transactions`, because create-charge does not list transactions.

## Connection slots

The blueprint omits `__IMTCONN__`, `account`, `auth`, `makeConnectionId`, and `__IMTHOOK__`. Make's create API returns 404 `IM304` if a numeric connection id does not belong to the importing team. A `metadata.parameters` entry still labels the slot (`account:google`, `account:slack2,slack3`, and so on) so the designer shows a connection field.

Webhook triggers (`gateway:CustomWebHook`) ship with empty `parameters`. The hook is created after import. Do not paste a `hook.*.make.com` URL into a blueprint. That URL is a credential.

## Shape the validator enforces

- Top level is `{name, flow, metadata}`. No `zone`. No `subflows` wrapper.
- `metadata.scenario` carries `roundtrips`, `maxErrors`, `autoCommit`, `autoCommitTriggerLast`, `sequential`, `confidential`, `dataloss`, `dlq`, `freshVariables`.
- `metadata.instant` is true only when the first module is `gateway:CustomWebHook`.
- Router is `builtin:BasicRouter`, it is the last module in its flow, and it has at least two routes. Filters sit on the first module of a route, not on the router.
- Aggregators carry `parameters.feeder` pointing at an upstream module id.
- Error handlers end with `builtin:Break`, `builtin:Ignore`, `builtin:Resume`, `builtin:Commit`, or `builtin:Rollback`.
- `{{n.field}}` and `{{n.`0`}}` must name a module id that exists and is upstream. A module on one route cannot read a module on another route.

## Adding a module

Do not add an id because the Make UI shows an action with a similar English name. Add it when you can point at an export or at Make's scenario-building examples, and put that source on the allowlist entry in `makebp/allowlist.py`. Then run `python3 scripts/build_library.py` so `schema/modules.allowlist.json` is rewritten.
