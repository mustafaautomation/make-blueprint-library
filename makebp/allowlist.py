"""Known Make module identifiers.

Every entry is a module id witnessed in at least one of:

* Integromat's make-skills examples (github.com/integromat/make-skills), which
  name the modules the scenario API accepts.
* The public blueprint corpus measured by migrate-to-n8n (1,432 Make exports).
* Import-shaped templates published against a live Make create call
  (awesome-make-templates ground truth, including google-email:ActionSendEmail).

Versions are the ones those sources shipped. Modules whose version was not in
the snippet are pinned to 1, which is what those exports used for that app
family when no higher version was recorded.

Native apps whose module id was not in those sources (Shopify, Pipedrive,
GoHighLevel, WooCommerce, Calendly, Xero, QuickBooks, ClickUp, and others)
are called through ``http:ActionSendData``. Guessing a module id would fail
import with "module not found".
"""

from __future__ import annotations

# connection: None, or (parameter_name, account_type)
# kind: trigger | action | router | aggregator | iterator | directive | transformer | responder | throw

def _c(param: str, account: str) -> dict:
    return {"parameter": param, "type": account, "label": "Connection"}


G = _c("__IMTCONN__", "account:google")
GMAIL_ACCOUNT = _c("account", "account:google-restricted")
GMAIL_CONN = _c("__IMTCONN__", "account:google-restricted")
SLACK = _c("__IMTCONN__", "account:slack2,slack3")
OPENAI = _c("__IMTCONN__", "account:openai-gpt-3")
ANTHROPIC = _c("__IMTCONN__", "account:anthropic-claude")
HUBSPOT = _c("__IMTCONN__", "account:hubspotcrm")
NOTION = _c("__IMTCONN__", "account:notion2,notion3")
AIRTABLE = _c("__IMTCONN__", "account:airtable")
TWILIO = _c("__IMTCONN__", "account:twilio")
STRIPE = _c("__IMTCONN__", "account:stripe")
ZENDESK = _c("__IMTCONN__", "account:zendesk")
LINKEDIN = _c("__IMTCONN__", "account:linkedin")
FACEBOOK = _c("__IMTCONN__", "account:facebook-pages")
TWITTER = _c("__IMTCONN__", "account:twitter")
INSTAGRAM = _c("__IMTCONN__", "account:instagram-business")
TYPEFORM = _c("__IMTCONN__", "account:typeform")
APIFY = _c("__IMTCONN__", "account:apify")
GEMINI = _c("__IMTCONN__", "account:gemini-ai")
PERPLEXITY = _c("__IMTCONN__", "account:perplexity-ai")
AGENT = _c("makeConnectionId", "account:ai-provider")
DROPBOX = _c("__IMTCONN__", "account:dropbox")
DISCORD = _c("__IMTCONN__", "account:discord")
TELEGRAM = _c("__IMTCONN__", "account:telegram")
RSS = None
HTTP = None
NONE = None


def entry(version: int, app: str, label: str, kind: str, connection, source: str) -> dict:
    return {
        "version": version,
        "app": app,
        "label": label,
        "kind": kind,
        "connection": connection,
        "source": source,
    }


OFFICIAL = "integromat/make-skills"
CORPUS = "public Make blueprint corpus (migrate-to-n8n module map, 1432 exports)"
TEMPLATE = "import-tested public template (awesome-make-templates / live create)"
GIST = "public exported blueprint"

MODULES: dict[str, dict] = {}


def add(module: str, version: int, app: str, label: str, kind: str, connection, source: str) -> None:
    MODULES[module] = entry(version, app, label, kind, connection, source)


# --- Official make-skills examples -------------------------------------------------
add("ai-local-agent:RunLocalAIAgent", 1, "Make AI Agent", "Run an AI agent", "action", AGENT, OFFICIAL)
add("gateway:CustomWebHook", 1, "Webhooks", "Custom webhook", "trigger", NONE, OFFICIAL)
add("gateway:WebhookRespond", 1, "Webhooks", "Webhook response", "responder", NONE, OFFICIAL)
add("google-drive:uploadAFile", 4, "Google Drive", "Upload a file", "action", G, OFFICIAL)
add("google-email:TriggerNewEmail", 1, "Gmail", "Watch emails", "trigger", GMAIL_CONN, OFFICIAL)
add("google-sheets:addRow", 2, "Google Sheets", "Add a row", "action", G, OFFICIAL)
add("google-sheets:updateRow", 2, "Google Sheets", "Update a row", "action", G, OFFICIAL)
add("google-sheets:watchRows", 2, "Google Sheets", "Watch new rows", "trigger", G, OFFICIAL)
add("hubspotcrm:createContact", 2, "HubSpot CRM", "Create a contact", "action", HUBSPOT, OFFICIAL)
add("openai-gpt-3:CreateCompletion", 1, "OpenAI", "Create a completion", "action", OPENAI, OFFICIAL)
add("scenario-service:ReturnData", 1, "Scenarios", "Return data", "responder", NONE, OFFICIAL)
add("scenario-service:StartSubscenario", 1, "Scenarios", "Start a subscenario", "trigger", NONE, OFFICIAL)
add("slack:CreateMessage", 4, "Slack", "Send a message", "action", SLACK, OFFICIAL)
add("stripe:CreateCharge", 1, "Stripe", "Create a charge", "action", STRIPE, OFFICIAL)
add("zendesk:UpdateTicket", 1, "Zendesk", "Update a ticket", "action", ZENDESK, OFFICIAL)
add("builtin:BasicAggregator", 1, "Flow control", "Array aggregator", "aggregator", NONE, OFFICIAL)
add("builtin:BasicFeeder", 1, "Flow control", "Iterator", "iterator", NONE, OFFICIAL)
add("builtin:BasicRepeater", 1, "Flow control", "Repeater", "iterator", NONE, OFFICIAL)
add("builtin:BasicRouter", 1, "Flow control", "Router", "router", NONE, OFFICIAL)
add("builtin:Break", 1, "Flow control", "Retry (Break)", "directive", NONE, OFFICIAL)
add("builtin:Commit", 1, "Flow control", "Commit", "directive", NONE, OFFICIAL)
add("builtin:Ignore", 1, "Flow control", "Skip (Ignore)", "directive", NONE, OFFICIAL)
add("builtin:Resume", 1, "Flow control", "Resume", "directive", NONE, OFFICIAL)
add("builtin:Rollback", 1, "Flow control", "Rollback", "directive", NONE, OFFICIAL)
add("builtin:ThrowError", 1, "Flow control", "Throw error", "throw", NONE, OFFICIAL)
add("builtin:ThrowWarning", 1, "Flow control", "Throw warning", "throw", NONE, OFFICIAL)
add("util:AggregateAggregator", 1, "Tools", "Table aggregator", "aggregator", NONE, OFFICIAL)
add("util:FunctionAggregator2", 1, "Tools", "Numeric aggregator", "aggregator", NONE, OFFICIAL)
add("util:GetVariable2", 1, "Tools", "Get a variable", "transformer", NONE, OFFICIAL)
add("util:SetVariable2", 1, "Tools", "Set a variable", "transformer", NONE, OFFICIAL)
add("util:TextAggregator", 1, "Tools", "Text aggregator", "aggregator", NONE, OFFICIAL)

# --- Public blueprint corpus and import-tested templates ---------------------------
add("google-email:ActionSendEmail", 2, "Gmail", "Send an email", "action", GMAIL_ACCOUNT, TEMPLATE)
add("google-email:ActionCreateDraft", 2, "Gmail", "Create a draft", "action", GMAIL_ACCOUNT, CORPUS)
add("google-email:createADraft", 1, "Gmail", "Create a draft", "action", GMAIL_ACCOUNT, CORPUS)
add("google-email:sendAnEmail", 1, "Gmail", "Send an email", "action", GMAIL_ACCOUNT, CORPUS)
add("google-email:TriggerWatchEmails", 1, "Gmail", "Watch emails", "trigger", GMAIL_CONN, CORPUS)
add("google-email:triggerWatchNewEmails", 1, "Gmail", "Watch emails", "trigger", GMAIL_CONN, CORPUS)
add("google-sheets:filterRows", 2, "Google Sheets", "Search rows", "action", G, GIST)
add("google-sheets:searchRows", 2, "Google Sheets", "Search rows", "action", G, CORPUS)
add("google-sheets:searchRowsAdvanced", 2, "Google Sheets", "Search rows (advanced)", "action", G, CORPUS)
add("google-sheets:deleteRow", 2, "Google Sheets", "Delete a row", "action", G, CORPUS)
add("google-sheets:createSpreadsheet", 2, "Google Sheets", "Create a spreadsheet", "action", G, CORPUS)
add("google-sheets:getSheetContent", 2, "Google Sheets", "Get sheet content", "action", G, CORPUS)
add("google-drive:getAFile", 1, "Google Drive", "Get a file", "action", G, CORPUS)
add("google-drive:watchFilesInAFolder", 1, "Google Drive", "Watch files in a folder", "trigger", G, CORPUS)
add("google-drive:createAFolder", 1, "Google Drive", "Create a folder", "action", G, CORPUS)
add("google-drive:searchForFilesFolders", 1, "Google Drive", "Search for files", "action", G, CORPUS)
add("google-docs:createADocument", 1, "Google Docs", "Create a document", "action", G, CORPUS)
add("google-docs:getADocument", 1, "Google Docs", "Get a document", "action", G, CORPUS)
add("google-calendar:createAnEvent", 1, "Google Calendar", "Create an event", "action", G, CORPUS)
add("google-calendar:searchEvents", 1, "Google Calendar", "Search events", "action", G, CORPUS)
add("google-calendar:deleteAnEvent", 1, "Google Calendar", "Delete an event", "action", G, CORPUS)
add("google-forms:watchResponses", 2, "Google Forms", "Watch responses", "trigger", G, TEMPLATE)
add("openai-gpt-3:transformTextToStructuredData", 1, "OpenAI", "Transform text to structured data", "action", OPENAI, CORPUS)
add("openai-gpt-3:askAnything", 1, "OpenAI", "Ask anything", "action", OPENAI, CORPUS)
add("openai-gpt-3:createModelResponse", 1, "OpenAI", "Create a model response", "action", OPENAI, CORPUS)
add("openai-gpt-3:GenerateImage", 1, "OpenAI", "Generate an image", "action", OPENAI, CORPUS)
add("openai-gpt-3:messageAssistantAdvanced", 1, "OpenAI", "Message an assistant", "action", OPENAI, CORPUS)
add("anthropic-claude:createAMessage", 1, "Anthropic Claude", "Create a message", "action", ANTHROPIC, CORPUS)
add("anthropic-claude:simpleTextPrompt", 1, "Anthropic Claude", "Simple text prompt", "action", ANTHROPIC, CORPUS)
add("gemini-ai:createACompletionGeminiPro", 1, "Gemini", "Create a completion", "action", GEMINI, CORPUS)
add("perplexity-ai:createAChatCompletion", 1, "Perplexity", "Create a chat completion", "action", PERPLEXITY, CORPUS)
add("slack:InviteUsers", 1, "Slack", "Invite users", "action", SLACK, CORPUS)
add("notion:createAPage", 1, "Notion", "Create a page", "action", NOTION, CORPUS)
add("notion:createDataSourceItem", 1, "Notion", "Create a data source item", "action", NOTION, TEMPLATE)
add("notion:updateADatabaseItem", 1, "Notion", "Update a database item", "action", NOTION, CORPUS)
add("airtable:ActionCreateRecord", 1, "Airtable", "Create a record", "action", AIRTABLE, CORPUS)
add("airtable:ActionGetRecord", 1, "Airtable", "Get a record", "action", AIRTABLE, CORPUS)
add("airtable:ActionSearchRecords", 1, "Airtable", "Search records", "action", AIRTABLE, CORPUS)
add("airtable:ActionUpdateRecords", 1, "Airtable", "Update records", "action", AIRTABLE, CORPUS)
add("airtable:TriggerWatchRecords", 1, "Airtable", "Watch records", "trigger", AIRTABLE, CORPUS)
add("twilio:SendSMS", 1, "Twilio", "Send an SMS", "action", TWILIO, CORPUS)
add("http:ActionSendData", 3, "HTTP", "Make a request", "action", HTTP, CORPUS)
add("http:ActionSendDataAPIKeyAuth", 3, "HTTP", "Make a request (API key)", "action", _c("auth", "keychain:apikeyauth"), GIST)
add("http:ActionSendDataBasicAuth", 3, "HTTP", "Make a request (basic auth)", "action", _c("auth", "keychain:basicauth"), CORPUS)
add("http:ActionGetFile", 3, "HTTP", "Get a file", "action", HTTP, GIST)
add("http:MakeRequest", 3, "HTTP", "Make a request", "action", HTTP, CORPUS)
add("http:DownloadFile", 3, "HTTP", "Download a file", "action", HTTP, CORPUS)
add("json:ParseJSON", 1, "JSON", "Parse JSON", "transformer", NONE, "Make API blueprint example (developers.make.com)")
add("json:CreateJSON", 1, "JSON", "Create JSON", "transformer", NONE, CORPUS)
add("json:TransformToJSON", 1, "JSON", "Transform to JSON", "transformer", NONE, CORPUS)
add("json:AggregateToJSON", 1, "JSON", "Aggregate to JSON", "aggregator", NONE, CORPUS)
add("regexp:HTMLToText", 1, "Text parser", "HTML to text", "transformer", NONE, CORPUS)
add("regexp:Replace", 1, "Text parser", "Replace", "transformer", NONE, CORPUS)
add("regexp:Parser", 1, "Text parser", "Match pattern", "transformer", NONE, CORPUS)
add("csv:ParseCSV", 1, "CSV", "Parse CSV", "transformer", NONE, CORPUS)
add("rss:TriggerNewArticle", 1, "RSS", "Watch RSS feed items", "trigger", RSS, CORPUS)
add("rss:ActionReadArticles", 1, "RSS", "Retrieve RSS feed items", "action", RSS, CORPUS)
add("util:SetVariables", 1, "Tools", "Set multiple variables", "transformer", NONE, GIST)
add("util:SetMultipleVariables", 1, "Tools", "Set multiple variables", "transformer", NONE, CORPUS)
add("util:FunctionSleep", 1, "Tools", "Sleep", "action", NONE, GIST)
add("util:Sleep", 1, "Tools", "Sleep", "action", NONE, CORPUS)
add("linkedin:CreatePost", 1, "LinkedIn", "Create a post", "action", LINKEDIN, CORPUS)
add("linkedin:CreateCompanyPost", 1, "LinkedIn", "Create a company post", "action", LINKEDIN, CORPUS)
add("facebook-pages:CreatePost", 1, "Facebook Pages", "Create a post", "action", FACEBOOK, CORPUS)
add("twitter:createATweet", 1, "X (Twitter)", "Create a tweet", "action", TWITTER, CORPUS)
add("instagram-business:CreatePostPhoto", 1, "Instagram", "Create a photo post", "action", INSTAGRAM, CORPUS)
add("typeform:WatchEventsWithResponses", 1, "Typeform", "Watch responses", "trigger", TYPEFORM, CORPUS)
add("typeform:ListResponses", 1, "Typeform", "List responses", "action", TYPEFORM, CORPUS)
add("apify:runActor", 1, "Apify", "Run an actor", "action", APIFY, CORPUS)
add("apify:fetchDatasetItems", 1, "Apify", "Fetch dataset items", "action", APIFY, CORPUS)
add("email:ActionSendEmail", 1, "Email", "Send an email", "action", _c("account", "account:email"), CORPUS)
add("email:TriggerNewEmail", 1, "Email", "Watch emails", "trigger", _c("__IMTCONN__", "account:email"), CORPUS)
add("discord:createMessage", 1, "Discord", "Send a message", "action", DISCORD, CORPUS)
add("telegram:SendReplyMessage", 1, "Telegram", "Send a message", "action", TELEGRAM, CORPUS)
add("dropbox:uploadLargeFile", 1, "Dropbox", "Upload a file", "action", DROPBOX, CORPUS)
add("markdown:Compile", 1, "Markdown", "Markdown to HTML", "transformer", NONE, CORPUS)
add("code:ExecuteCode", 1, "Code", "Execute code", "transformer", NONE, CORPUS)
add("placeholder:Placeholder", 1, "Flow control", "Placeholder", "transformer", NONE, CORPUS)

AGGREGATOR_MODULES = {name for name, meta in MODULES.items() if meta["kind"] == "aggregator"}
DIRECTIVES = {name for name, meta in MODULES.items() if meta["kind"] == "directive"}
ROUTERS = {name for name, meta in MODULES.items() if meta["kind"] == "router"}
TRIGGERS = {name for name, meta in MODULES.items() if meta["kind"] == "trigger"}

# Triggers that Make marks instant. metadata.instant follows the trigger.
INSTANT_TRIGGERS = {
    "gateway:CustomWebHook",
    "typeform:WatchEventsWithResponses",
    "google-forms:watchResponses",
}

CONNECTION_VALUE_KEYS = {
    "__IMTCONN__",
    "__IMTKEY__",
    "__IMTHOOK__",
    "makeConnectionId",
    "account",
    "auth",
    "hook",
}

SECRET_PATTERNS = [
    r"sk_live_[A-Za-z0-9]",
    r"sk_test_[A-Za-z0-9]",
    r"rk_live_[A-Za-z0-9]",
    r"xox[baprs]-",
    r"\bAKIA[0-9A-Z]{16}\b",
    r"-----BEGIN [A-Z ]+PRIVATE KEY-----",
    r"ghp_[A-Za-z0-9]{20,}",
    r"github_pat_[A-Za-z0-9_]{20,}",
    r"xoxe\.xoxp-",
    r"AIza[0-9A-Za-z\-_]{20,}",
    r"hooks\.slack\.com/services/",
    r"https?://hook\.[a-z0-9]+\.make\.com/\S+",
]
