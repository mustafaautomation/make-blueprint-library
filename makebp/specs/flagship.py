"""The twenty scenarios buyers ask for first. Each one is authored, not cloned."""

from makebp.dsl import (
    M,
    airtable_record,
    bearer_headers,
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
    set_var,
    sheets_add,
    sheets_filter,
    sheets_update,
    sheets_watch,
    skip,
    slack,
    twilio,
    when,
    when_all,
    cond,
)

INVOICE_PROMPT = (
    "You extract supplier invoices. Return one JSON object and no other text. "
    "Keys: vendor (string), invoice_number (string), currency (ISO code), total (number), "
    "due_date (YYYY-MM-DD or empty), confidence (number from 0 to 1). "
    "Use only facts in the email. If a field is missing, use an empty string, 0 for total, "
    "and confidence below 0.5. Never invent a vendor."
)


def _alert(text: str) -> dict:
    return M("ignored", "slack:CreateMessage", "Tell the channel", text, mapper=slack(text))


FLAGSHIP = [
    scenario(
        id="ai-invoice-gmail-sheets-xero",
        title="AI invoice extraction from Gmail to Sheets, Xero, or QuickBooks",
        category="invoices-docs",
        phase=1,
        featured_rank=1,
        difficulty="intermediate",
        tags=["invoices", "gmail", "openai", "google-sheets", "xero", "quickbooks"],
        apps=["Gmail", "OpenAI", "Google Sheets", "Xero", "QuickBooks", "Slack"],
        description="Read an invoice email, write the fields to a sheet, and draft a bill in Xero or QuickBooks when the model is confident.",
        problem=(
            "A bookkeeper still opens every supplier email, retypes the vendor, number, total, and due date, "
            "then creates the bill in the accounting tool. The mistakes show up at month end, when the sheet "
            "and the ledger disagree. This demo watches a Gmail label, asks OpenAI for those fields as JSON, "
            "logs every attempt, and only calls the accounting API when confidence is at least 0.8."
        ),
        audience=(
            "Freelance bookkeepers and finance operators who already live in Gmail plus Xero or QuickBooks. "
            "It is a portfolio demo, so the companies in the sample (Harbor Goods, Northwind Studio) are fictional."
        ),
        time_saved="About 4 to 6 minutes per invoice. At 80 invoices a month that is roughly 6 to 8 hours of retyping.",
        schedule="Every 15 minutes. Gmail's watch module is polling, so the schedule is what wakes the scenario.",
        sample={
            "from": "billing@example.com",
            "subject": "Invoice 1842 from Harbor Goods",
            "text": (
                "Harbor Goods\nInvoice number 1842\nCurrency USD\nTotal 1280.00\n"
                "Due date 2026-12-15\nDescription: studio rental, November."
            ),
        },
        sheet_columns=[
            "A received_at — {{now}}",
            "B from — sender",
            "C vendor",
            "D invoice_number",
            "E currency",
            "F total",
            "G due_date",
            "H confidence",
            "I status — logged, xero, quickbooks, or review",
        ],
        mapping=[
            "The model must return raw JSON. Module 3 parses `{{2.result}}` into vendor, invoice_number, currency, total, due_date, and confidence.",
            "Column letters in the sheet are positional. Column A is values[\"0\"]. Do not switch the mapper to header names or a renamed header silently shifts every cell.",
            "Change the Set variable module from `xero` to `quickbooks` to send the bill to QuickBooks instead. Both HTTP modules stay in the blueprint so you can see the payload.",
        ],
        customization=[
            "Point the Gmail search at your label, for example `label:invoices newer_than:14d`.",
            "Xero needs the tenant id header and a bill payload that matches your chart of accounts. The demo uses one line for the total.",
            "QuickBooks company id sits in the URL path. Replace YOUR_COMPANY_ID.",
            "Raise the 0.8 cutoff if the model is guessing vendor names on forwarded threads.",
        ],
        steps=[
            M("mail", "google-email:TriggerWatchEmails", "Watch the invoices label",
              "Polls Gmail for mail that already landed in the invoices label. Limit 5 so a backlog cannot drain the operation quota in one run.",
              mapper=gmail_query("label:invoices newer_than:14d", 5)),
            M("extract", "openai-gpt-3:CreateCompletion", "Extract the invoice fields",
              "Asks for a single JSON object. The low temperature is deliberate: this is extraction, not copywriting.",
              mapper=chat("You are a careful accounts-payable clerk.", INVOICE_PROMPT + "\n\nEmail:\n{{mail.text}}", 500),
              onerror=retry("The model call failed. Retry three times, 15 minutes apart, and keep the incomplete execution.",
                            notify=_alert("Invoice extraction failed for {{mail.subject}}. The run will retry."))),
            M("parsed", "json:ParseJSON", "Parse the JSON",
              "Turns the model text into fields the sheet and the accounting calls can map one by one.",
              mapper={"json": "{{extract.result}}"}),
            M("choice", "util:SetVariable2", "Choose Xero or QuickBooks",
              "One switch for the whole scenario. Leave the value as xero, or set it to quickbooks. Routes read this variable, not a hard-coded module.",
              mapper=set_var("books", "xero")),
            M("log", "google-sheets:addRow", "Log every invoice",
              "Writes the row before any accounting call. A failed API call still leaves a paper trail with status `logged`.",
              mapper=sheets_add("{{now}}", "{{mail.from}}", "{{parsed.vendor}}", "{{parsed.invoice_number}}",
                                 "{{parsed.currency}}", "{{parsed.total}}", "{{parsed.due_date}}",
                                 "{{parsed.confidence}}", "logged")),
            router("books", "Route the confident bills",
                   "Every matching route runs. Confidence and the books variable are AND-ed so a low-confidence bill never becomes a live invoice.",
                   [
                       route("Xero", "Create an accounts-payable invoice in Xero.", [
                           M("xero", "http:ActionSendData", "Create the Xero bill",
                             "POST /Invoices with Type ACCPAY. The tenant header is a placeholder until you paste your own.",
                             mapper=http("post", "https://api.xero.com/api.xro/2.0/Invoices",
                                         data='{"Type":"ACCPAY","Contact":{"Name":"{{parsed.vendor}}"},"InvoiceNumber":"{{parsed.invoice_number}}","DueDate":"{{parsed.due_date}}","CurrencyCode":"{{parsed.currency}}","LineItems":[{"Description":"Imported from Gmail","Quantity":1,"UnitAmount":"{{parsed.total}}"}]}',
                                         headers=bearer_headers([{"name": "xero-tenant-id", "value": "YOUR_XERO_TENANT_ID"}])),
                             parameters={"handleErrors": True},
                             onerror=retry("Xero returned an error. Retry the bill, and ping Slack so the row is not forgotten.",
                                           notify=_alert("Xero bill failed for {{parsed.invoice_number}} ({{parsed.vendor}})."))),
                       ], when_all("Confident and Xero", [
                           cond("{{parsed.confidence}}", "number:greaterorequal", "0.8"),
                           cond("{{choice.books}}", "text:equal", "xero"),
                       ])),
                       route("QuickBooks", "Create a bill in QuickBooks Online.", [
                           M("qbo", "http:ActionSendData", "Create the QuickBooks bill",
                             "POST /bill on the company id you paste in. The body is a single expense line for the extracted total.",
                             mapper=http("post", "https://quickbooks.api.intuit.com/v3/company/YOUR_COMPANY_ID/bill",
                                         data='{"VendorRef":{"name":"{{parsed.vendor}}"},"DocNumber":"{{parsed.invoice_number}}","CurrencyRef":{"value":"{{parsed.currency}}"},"Line":[{"DetailType":"AccountBasedExpenseLineDetail","Amount":"{{parsed.total}}","Description":"Imported from Gmail"}]}'),
                             parameters={"handleErrors": True},
                             onerror=retry("QuickBooks rejected the bill. Retry and alert.",
                                           notify=_alert("QuickBooks bill failed for {{parsed.invoice_number}}."))),
                       ], when_all("Confident and QuickBooks", [
                           cond("{{parsed.confidence}}", "number:greaterorequal", "0.8"),
                           cond("{{choice.books}}", "text:equal", "quickbooks"),
                       ])),
                       route("Review", "A person should read this one before it becomes a bill.", [
                           M("review", "slack:CreateMessage", "Ask a human to review",
                             "Posts the extracted fields and the original subject. The sheet row already exists.",
                             mapper=slack("*Invoice needs review* — {{parsed.vendor}} {{parsed.invoice_number}} {{parsed.currency}} {{parsed.total}} (confidence {{parsed.confidence}}). Subject: {{mail.subject}}")),
                       ], when("Low confidence", "{{parsed.confidence}}", "number:less", "0.8")),
                   ]),
        ],
    ),
    scenario(
        id="ai-lead-score-hubspot",
        title="AI lead capture, score, and HubSpot contact",
        category="lead-gen-crm",
        phase=1,
        featured_rank=2,
        difficulty="intermediate",
        tags=["leads", "openai", "hubspot", "slack", "gmail"],
        apps=["Webhooks", "OpenAI", "Google Sheets", "HubSpot CRM", "Slack", "Gmail"],
        description="Score a new lead from a form webhook, create the HubSpot contact when they are warm, and draft email for the middle of the list.",
        problem=(
            "Form fills sit in an inbox until someone copies them into HubSpot. Hot leads cool off. "
            "This demo takes the webhook, asks the model for a 0–100 score and a one-sentence reason, "
            "logs the row, creates the contact only at 70 or above, and leaves a Gmail draft for the 40–69 band "
            "so a person still sends the first note."
        ),
        audience="Solo SDRs and small B2B teams that capture leads on a site form and sell from HubSpot.",
        time_saved="About 3 minutes of copy-paste per lead, and the first touch goes out in the same run instead of the next morning.",
        schedule="Immediately. The webhook is the trigger, so the scenario stays on and Make wakes it per request.",
        sample={
            "first_name": "Alex",
            "last_name": "Rivera",
            "email": "alex.rivera@example.com",
            "company": "Northwind Studio",
            "phone": "+15555550123",
            "message": "We need the invoice workflow running before month end. Team of 12. Timeline is this quarter.",
            "page": "https://example.com/invoice-automation",
        },
        sheet_columns=["A received_at", "B email", "C company", "D score", "E reason", "F band — hot, nurture, or low"],
        mapping=[
            "HubSpot's create-contact module in Make's own examples maps email, firstname, and lastname at the top level of the mapper. If your UI shows a properties group after import, map those same three fields inside it.",
            "The score is a number in the parsed JSON. The filters compare it with number operators, not text.",
        ],
        customization=[
            "Edit the rubric in the system prompt. The demo treats a timeline plus a team size as buying signals.",
            "Swap the nurture draft for your own first-touch copy. It stays a draft so nothing sends itself.",
            "Add a company property if your portal requires it. The native module call here is the contact only.",
        ],
        steps=[
            M("lead", "gateway:CustomWebHook", "Catch the form webhook",
              "The form, or a tool in front of it, POSTs the lead here. Parameters stay empty so Make creates a new hook after import."),
            M("score", "openai-gpt-3:CreateCompletion", "Score the lead",
              "Returns JSON with score, band (hot, nurture, low), and reason. The rubric is in the prompt, not buried in a filter.",
              mapper=chat(
                  "You qualify B2B leads. Return JSON only, with keys score (0-100), band (hot, nurture, or low), and reason (one sentence).",
                  "Score this lead. Hot means they named a timeline or a budget. Nurture means a real company with a vague need. Low means student, spam, or no way to reply.\n\n"
                  "{{lead.first_name}} {{lead.last_name}} <{{lead.email}}> at {{lead.company}}\n{{lead.message}}",
                  300,
              ),
              onerror=retry("Scoring failed. Retry before the lead goes cold.",
                            notify=_alert("Lead scoring failed for {{lead.email}}."))),
            M("parsed", "json:ParseJSON", "Parse score JSON",
              "Exposes score, band, and reason to the sheet and the filters.",
              mapper={"json": "{{score.result}}"}),
            M("log", "google-sheets:addRow", "Log the lead and the score",
              "Every lead is logged, including the ones you do not contact. That is the audit trail.",
              mapper=sheets_add("{{now}}", "{{lead.email}}", "{{lead.company}}", "{{parsed.score}}", "{{parsed.reason}}", "{{parsed.band}}")),
            router("band", "Branch on the score",
                   "Hot creates the CRM contact and pings Slack. Nurture only drafts an email. Low stops after the sheet, which already ran.",
                   [
                       route("Hot", "Create the HubSpot contact and ping the channel.", [
                           M("contact", "hubspotcrm:createContact", "Create the HubSpot contact",
                             "Uses the native HubSpot module confirmed in Make's scenario-building examples. Email is the identity.",
                             mapper=hubspot_contact("{{lead.email}}", "{{lead.first_name}}", "{{lead.last_name}}", "{{lead.company}}", "{{lead.phone}}"),
                             onerror=retry("HubSpot rejected the contact. Retry, then a person can create it from the sheet.",
                                           notify=_alert("HubSpot create failed for {{lead.email}} (score {{parsed.score}})."))),
                           M("ping", "slack:CreateMessage", "Ping sales",
                             "The channel sees the score and the reason, not just the email.",
                             mapper=slack("*Hot lead* {{lead.first_name}} {{lead.last_name}} at {{lead.company}} — {{parsed.score}}. {{parsed.reason}}")),
                       ], when("Score at least 70", "{{parsed.score}}", "number:greaterorequal", "70")),
                       route("Nurture", "Leave a draft. Do not send it.", [
                           M("draft", "google-email:ActionCreateDraft", "Draft the first touch",
                             "A draft, not a send. The seller reviews tone before it goes out.",
                             mapper=gmail_message(
                                 "{{lead.email}}",
                                 "Re: {{lead.company}} and the form you just sent",
                                 "<p>Hi {{lead.first_name}},</p><p>Thanks for the note from {{lead.company}}. "
                                 "We read this as: {{parsed.reason}}</p><p>Worth a 20-minute look this week?</p>",
                             )),
                       ], when_all("Between 40 and 69", [
                           cond("{{parsed.score}}", "number:greaterorequal", "40"),
                           cond("{{parsed.score}}", "number:less", "70"),
                       ])),
                   ]),
        ],
    ),
]
