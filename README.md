# make-blueprint-library

A portfolio library of [Make.com](https://www.make.com/) scenario blueprints by Mustafa ([mustafaautomation](https://github.com/mustafaautomation)). Demos, when published, live on subdomains of quvantic.com.

**Portfolio demos only. Not client work.** These scenarios are fictional walkthroughs a buyer can import, reconnect, and adapt. They are not deliverables from a client engagement, and they do not contain anyone's accounts, keys, or data.

Make (formerly Integromat) is the automation product these files import into. Each folder has an importable `blueprint.json`, a README, fictional sample input, and a flow diagram.

## Import a blueprint

1. Download the folder, or copy `blueprint.json`.
2. In Make: **Scenarios → Create a new scenario → the three-dot menu at the bottom → Import Blueprint**.
3. Open each red module and choose your own connection. Red means unconnected, not broken.
4. Fill blank spreadsheets, channels, and every `YOUR_*` placeholder.
5. Run once with `sample-input.json`, then turn the schedule on.

The JSON shape is the blueprint Make exports and imports: `name`, `flow`, and `metadata`. Module entries carry `id`, `module` (`google-sheets:addRow`), `version`, `parameters`, `mapper`, and `metadata.designer` coordinates. Connection ids are omitted. A numeric connection id from someone else's team fails import with `IM304 Account doesn't exist`.

## Top 20

These are the demand-heavy patterns freelance buyers ask for first: invoices, lead routing, speed-to-lead, triage, booking, store orders, and reporting.

| # | Scenario | Category | Difficulty |
| ---: | --- | --- | --- |
| 1 | [AI invoice extraction from Gmail to Sheets, Xero, or QuickBooks](scenarios/invoices-docs/ai-invoice-gmail-sheets-xero/) | Invoices and documents | intermediate |
| 2 | [AI lead capture, score, and HubSpot contact](scenarios/lead-gen-crm/ai-lead-score-hubspot/) | Lead gen and CRM | intermediate |
| 3 | [AI lead score into GoHighLevel and a text](scenarios/lead-gen-crm/ai-lead-gohighlevel/) | Lead gen and CRM | intermediate |
| 4 | [AI lead score into a Pipedrive person and deal](scenarios/lead-gen-crm/ai-lead-pipedrive/) | Lead gen and CRM | intermediate |
| 5 | [Speed-to-lead SMS and email](scenarios/speed-to-lead/speed-to-lead-sms-email/) | Speed to lead | beginner |
| 6 | [Missed-call text-back](scenarios/speed-to-lead/missed-call-text-back/) | Speed to lead | beginner |
| 7 | [AI email triage and draft replies](scenarios/email/ai-email-triage-drafts/) | Email | intermediate |
| 8 | [Support ticket classification and routing](scenarios/support/support-ticket-classify-route/) | Support | intermediate |
| 9 | [Calendly or Cal.com booking confirmation](scenarios/booking/appointment-booking-confirm/) | Booking | beginner |
| 10 | [Shopify order sync to Sheets, Slack, and HubSpot](scenarios/ecommerce/shopify-order-sync/) | E-commerce | intermediate |
| 11 | [WooCommerce order sync to Sheets and an order note](scenarios/ecommerce/woocommerce-order-sync/) | E-commerce | intermediate |
| 12 | [Repurpose an RSS article into LinkedIn, Facebook, and X](scenarios/social/social-repurpose-channels/) | Social | intermediate |
| 13 | [Assistant that picks a tool, then answers](scenarios/ai-agents/assistant-agent-with-tools/) | AI agents | advanced |
| 14 | [Knowledge-base Q&A from a sheet](scenarios/ai-agents/knowledge-base-qa/) | AI agents | intermediate |
| 15 | [Weekly KPI narrative to Slack and email](scenarios/reporting/weekly-kpi-slack-email/) | Reporting | intermediate |
| 16 | [Slack shortcut to a Notion page and a ClickUp task](scenarios/slack-notion-clickup/slack-notion-clickup/) | Slack, Notion, and ClickUp | intermediate |
| 17 | [Fetch a company page and write a summary back to the sheet](scenarios/scraping-enrichment/scrape-enrich-sheets/) | Scraping and enrichment | intermediate |
| 18 | [Parse a CV email and score it against a rubric](scenarios/hr-recruiting/hr-cv-parse-score/) | HR and recruiting | advanced |
| 19 | [Stripe balance transactions into a reconciliation sheet](scenarios/finance/stripe-balance-reconciliation/) | Finance | advanced |
| 20 | [Airtable CRM record summary](scenarios/lead-gen-crm/airtable-crm-ai-summary/) | Lead gen and CRM | intermediate |

## Catalog

109 scenarios. The machine-readable index is [`catalog.json`](catalog.json), described in [`CATALOG_SCHEMA.md`](CATALOG_SCHEMA.md).

| Category | Scenarios | What the folder covers |
| --- | ---: | --- |
| [Lead gen and CRM](scenarios/lead-gen-crm/) | 10 | Capture a lead, score or enrich it, and write it to a CRM. |
| [Speed to lead](scenarios/speed-to-lead/) | 7 | Reply by SMS or email while the inquiry is still warm. |
| [Invoices and documents](scenarios/invoices-docs/) | 7 | Pull fields out of invoices, receipts, and other documents. |
| [Email](scenarios/email/) | 8 | Triage a mailbox, draft replies, and file what matters. |
| [Social](scenarios/social/) | 8 | Turn one source into channel-ready posts. |
| [E-commerce](scenarios/ecommerce/) | 11 | Sync orders, refunds, and stock signals out of a store. |
| [Support](scenarios/support/) | 8 | Classify a ticket and route it to the right queue. |
| [Booking](scenarios/booking/) | 6 | Confirm, remind, and brief people around a booking. |
| [Reporting](scenarios/reporting/) | 8 | Roll a sheet or API up into a Slack or email digest. |
| [Slack, Notion, and ClickUp](scenarios/slack-notion-clickup/) | 7 | Turn a Slack or form event into an ops task. |
| [Scraping and enrichment](scenarios/scraping-enrichment/) | 7 | Fetch a public page or dataset and land it in a sheet. |
| [AI agents](scenarios/ai-agents/) | 7 | Let a model choose a tool, then answer from the tool result. |
| [HR and recruiting](scenarios/hr-recruiting/) | 7 | Parse applications and score them against a rubric. |
| [Finance](scenarios/finance/) | 8 | Log charges, payouts, and categories for a human to reconcile. |

### Every scenario

#### Lead gen and CRM

| Scenario | Apps | Difficulty | Tags |
| --- | --- | --- | --- |
| [AI lead capture, score, and HubSpot contact](scenarios/lead-gen-crm/ai-lead-score-hubspot/) | Webhooks, OpenAI, Google Sheets, HubSpot CRM, Slack, Gmail | intermediate | leads, openai, hubspot, slack, gmail |
| [AI lead score into a Pipedrive person and deal](scenarios/lead-gen-crm/ai-lead-pipedrive/) | Webhooks, OpenAI, Pipedrive, Slack, Google Sheets | intermediate | leads, pipedrive, openai, slack |
| [AI lead score into GoHighLevel and a text](scenarios/lead-gen-crm/ai-lead-gohighlevel/) | Webhooks, OpenAI, GoHighLevel, Twilio, Slack, Google Sheets | intermediate | leads, gohighlevel, openai, twilio, slack |
| [Airtable CRM record summary](scenarios/lead-gen-crm/airtable-crm-ai-summary/) | Airtable, OpenAI, Slack | intermediate | airtable, crm, openai, slack |
| [Booth lead with a badge email](scenarios/lead-gen-crm/event-booth-lead/) | Webhooks, OpenAI, Google Sheets, HubSpot CRM, Slack | beginner | events, leads, hubspot |
| [Pricing-page question into a draft](scenarios/lead-gen-crm/pricing-page-chat/) | Webhooks, OpenAI, Google Sheets, Gmail, Slack | intermediate | pricing, leads, gmail |
| [Qualify a chat widget transcript into HubSpot](scenarios/lead-gen-crm/chat-widget-qualify-hubspot/) | Webhooks, OpenAI, Google Sheets, HubSpot CRM, Slack | intermediate | chat, hubspot, leads |
| [Score a partner referral before a draft goes out](scenarios/lead-gen-crm/partner-referral-score/) | Webhooks, OpenAI, Google Sheets, Gmail, Slack | intermediate | referrals, partners, gmail |
| [Sheet row of a prospect to an outreach draft](scenarios/lead-gen-crm/linkedin-row-outreach-draft/) | Google Sheets, OpenAI | intermediate | outreach, google-sheets, openai |
| [Webinar registration scored into HubSpot](scenarios/lead-gen-crm/webinar-registration-score/) | Webhooks, OpenAI, Google Sheets, HubSpot CRM, Slack | intermediate | webinar, hubspot, leads |

#### Speed to lead

| Scenario | Apps | Difficulty | Tags |
| --- | --- | --- | --- |
| [After-hours form pages only the owner](scenarios/speed-to-lead/after-hours-owner-only/) | Webhooks, OpenAI, Google Sheets, Twilio, Slack | beginner | speed-to-lead, after-hours, twilio |
| [Callback request with a named time](scenarios/speed-to-lead/callback-request-score/) | Webhooks, OpenAI, Google Sheets, Slack | intermediate | speed-to-lead, callbacks, slack |
| [Demo request becomes a follow-up draft](scenarios/speed-to-lead/demo-request-draft/) | Webhooks, OpenAI, Google Sheets, Gmail, Slack | intermediate | speed-to-lead, demos, gmail |
| [Missed-call text-back](scenarios/speed-to-lead/missed-call-text-back/) | Webhooks, Twilio, Google Sheets, Slack | beginner | missed-call, twilio, sms, google-sheets |
| [Quote request texts the owner](scenarios/speed-to-lead/quote-request-text-owner/) | Webhooks, OpenAI, Google Sheets, Twilio, Slack | beginner | speed-to-lead, quotes, twilio |
| [Speed-to-lead SMS and email](scenarios/speed-to-lead/speed-to-lead-sms-email/) | Webhooks, Twilio, Gmail, Slack | beginner | speed-to-lead, twilio, gmail, slack |
| [Trial signup SMS and a quiet log](scenarios/speed-to-lead/trial-signup-speed-to-lead/) | Webhooks, OpenAI, Google Sheets, Twilio, Slack | beginner | speed-to-lead, trials, twilio |

#### Invoices and documents

| Scenario | Apps | Difficulty | Tags |
| --- | --- | --- | --- |
| [AI invoice extraction from Gmail to Sheets, Xero, or QuickBooks](scenarios/invoices-docs/ai-invoice-gmail-sheets-xero/) | Gmail, OpenAI, Google Sheets, Xero, QuickBooks, Slack | intermediate | invoices, gmail, openai, google-sheets, xero, quickbooks |
| [Invoice email flagged for approval over 5000](scenarios/invoices-docs/invoice-approval-by-amount/) | Gmail, OpenAI, Google Sheets, Slack | intermediate | invoices, approval, gmail |
| [Possible duplicate invoice subjects](scenarios/invoices-docs/duplicate-invoice-subject/) | Gmail, OpenAI, Google Sheets, Slack | intermediate | invoices, duplicates, gmail |
| [Receipt email to an expense sheet](scenarios/invoices-docs/receipt-to-expense-sheet/) | Gmail, OpenAI, Google Sheets, Slack | beginner | receipts, gmail, expenses, openai |
| [Tell a credit note from an invoice](scenarios/invoices-docs/credit-note-or-invoice/) | Gmail, OpenAI, Google Sheets, Slack | intermediate | invoices, credit-notes, gmail |
| [Vendor statement email into a sheet](scenarios/invoices-docs/vendor-statement-to-sheet/) | Gmail, OpenAI, Google Sheets, Slack | intermediate | statements, gmail, ap |
| [W-9 style email logged as received](scenarios/invoices-docs/w9-email-to-sheet/) | Gmail, OpenAI, Google Sheets, Slack | beginner | vendors, gmail, onboarding |

#### Email

| Scenario | Apps | Difficulty | Tags |
| --- | --- | --- | --- |
| [AI email triage and draft replies](scenarios/email/ai-email-triage-drafts/) | Gmail, OpenAI, Slack, Google Sheets | intermediate | email, gmail, openai, triage, drafts |
| [Classify a cold-email reply](scenarios/email/cold-reply-classifier/) | Gmail, OpenAI, Google Sheets, Slack | intermediate | email, replies, gmail, openai |
| [Draft an acknowledgement for a new client email](scenarios/email/new-client-ack-draft/) | Gmail, OpenAI, Google Sheets, Slack | beginner | email, drafts, onboarding |
| [Flag legal keywords in the shared inbox](scenarios/email/legal-keyword-mail-to-slack/) | Gmail, OpenAI, Google Sheets, Slack | beginner | email, legal, slack, gmail |
| [Intro request summarized for a double opt-in](scenarios/email/intro-request-draft-note/) | Gmail, OpenAI, Google Sheets, Slack | intermediate | email, intros, gmail |
| [Log out-of-office replies and stay quiet](scenarios/email/out-of-office-skip-log/) | Gmail, OpenAI, Google Sheets, Slack | beginner | email, ooo, gmail |
| [Parse an order confirmation email into a sheet](scenarios/email/order-email-to-sheet/) | Gmail, OpenAI, Google Sheets, Slack | beginner | email, orders, gmail |
| [Separate a newsletter reply from a lead](scenarios/email/newsletter-reply-not-a-lead/) | Gmail, OpenAI, Google Sheets, Slack | intermediate | email, newsletters, leads |

#### Social

| Scenario | Apps | Difficulty | Tags |
| --- | --- | --- | --- |
| [Competitor changelog RSS to Slack](scenarios/social/competitor-changelog-rss/) | RSS, OpenAI, Google Sheets, Slack | beginner | competitors, rss, slack |
| [Content calendar row to a caption](scenarios/social/content-calendar-caption/) | Google Sheets, OpenAI | beginner | social, captions, google-sheets |
| [Long note into a LinkedIn draft and a short post](scenarios/social/thread-to-linkedin-and-short/) | Google Sheets, OpenAI | intermediate | social, linkedin, repurpose |
| [Repurpose an RSS article into LinkedIn, Facebook, and X](scenarios/social/social-repurpose-channels/) | RSS, OpenAI, Google Sheets, LinkedIn, Facebook Pages, X (Twitter) | intermediate | social, rss, openai, linkedin, facebook, twitter |
| [Social mention webhook to Slack](scenarios/social/mention-webhook-to-slack/) | Webhooks, Google Sheets, Slack | beginner | mentions, social, slack |
| [Testimonial cell to a one-sentence quote](scenarios/social/testimonial-to-quote-card/) | Google Sheets, OpenAI | beginner | social, testimonials, google-sheets |
| [Weekly social stats note](scenarios/social/weekly-social-stats-note/) | Google Sheets, OpenAI, Slack | beginner | social, reporting, slack |
| [YouTube RSS item to show notes](scenarios/social/youtube-rss-show-notes/) | RSS, OpenAI, Google Sheets, Slack | beginner | youtube, rss, social |

#### E-commerce

| Scenario | Apps | Difficulty | Tags |
| --- | --- | --- | --- |
| [Abandoned checkout text](scenarios/ecommerce/abandoned-checkout-text/) | Webhooks, OpenAI, Google Sheets, Twilio, Slack | intermediate | checkout, twilio, ecommerce |
| [Low-stock rows to Slack](scenarios/ecommerce/low-stock-slack/) | Google Sheets, Slack | beginner | inventory, slack, google-sheets |
| [Negative review webhook to Slack](scenarios/ecommerce/review-sentiment-slack/) | Webhooks, OpenAI, Google Sheets, Slack | intermediate | reviews, sentiment, slack |
| [Order line items into a sheet](scenarios/ecommerce/line-items-to-sheet/) | Webhooks, Google Sheets, Slack | intermediate | line-items, orders, google-sheets |
| [Product blurb to a description cell](scenarios/ecommerce/product-blurb-to-description/) | Google Sheets, OpenAI | beginner | catalog, copy, google-sheets |
| [Shopify order sync to Sheets, Slack, and HubSpot](scenarios/ecommerce/shopify-order-sync/) | Webhooks, Google Sheets, Slack, HubSpot CRM | intermediate | shopify, orders, hubspot, slack, google-sheets |
| [Shopify refund webhook to Slack](scenarios/ecommerce/shopify-refund-alert/) | Webhooks, OpenAI, Google Sheets, Slack | beginner | shopify, refunds, slack |
| [Supplier delay email to the warehouse channel](scenarios/ecommerce/supplier-delay-email/) | Gmail, OpenAI, Google Sheets, Slack | beginner | suppliers, gmail, slack |
| [VIP order amount to Slack](scenarios/ecommerce/vip-order-slack/) | Webhooks, OpenAI, Google Sheets, Slack | beginner | orders, vip, slack |
| [WooCommerce order sync to Sheets and an order note](scenarios/ecommerce/woocommerce-order-sync/) | Webhooks, Google Sheets, Slack, WooCommerce | intermediate | woocommerce, orders, google-sheets, slack |
| [WooCommerce refund note back to the order](scenarios/ecommerce/woo-refund-note/) | Webhooks, WooCommerce, Google Sheets, Slack | intermediate | woocommerce, refunds, slack |

#### Support

| Scenario | Apps | Difficulty | Tags |
| --- | --- | --- | --- |
| [CSAT webhook logged to a sheet](scenarios/support/csat-webhook-to-sheet/) | Webhooks, Google Sheets, Slack | beginner | csat, support, webhooks |
| [Product changelog RSS to Slack](scenarios/support/changelog-rss-to-slack/) | RSS, OpenAI, Google Sheets, Slack | beginner | changelog, rss, support |
| [Refund language in a ticket pings finance](scenarios/support/refund-request-to-finance/) | Webhooks, OpenAI, Google Sheets, Slack | intermediate | support, refunds, slack |
| [Split a ticket into bug or billing](scenarios/support/bug-or-billing-router/) | Webhooks, OpenAI, Google Sheets, Slack | intermediate | support, bugs, billing |
| [Status page change to Slack](scenarios/support/status-page-to-slack/) | Webhooks, Google Sheets, Slack | beginner | status, support, slack |
| [Support note to a macro draft](scenarios/support/support-macro-from-note/) | Google Sheets, OpenAI | intermediate | support, macros, google-sheets |
| [Support ticket classification and routing](scenarios/support/support-ticket-classify-route/) | Webhooks, OpenAI, Zendesk, Slack, Google Sheets | intermediate | support, zendesk, openai, slack |
| [Ticket from a VIP domain pings Slack](scenarios/support/vip-domain-ticket/) | Webhooks, OpenAI, Google Sheets, Slack | intermediate | support, vip, slack |

#### Booking

| Scenario | Apps | Difficulty | Tags |
| --- | --- | --- | --- |
| [Calendly or Cal.com booking confirmation](scenarios/booking/appointment-booking-confirm/) | Webhooks, Google Sheets, Gmail, Twilio, Slack | beginner | booking, calendly, calcom, gmail, twilio |
| [Day-before appointment reminder from the sheet](scenarios/booking/appointment-day-before-reminder/) | Google Sheets, Twilio | beginner | booking, reminders, twilio |
| [No-show webhook texts a rebook line](scenarios/booking/no-show-text-back/) | Webhooks, OpenAI, Google Sheets, Twilio, Slack | beginner | booking, no-show, twilio |
| [Pre-meeting intake brief for the host](scenarios/booking/intake-brief-for-host/) | Webhooks, OpenAI, Google Sheets, Slack | intermediate | booking, intake, slack |
| [Reschedule webhook logged and acknowledged](scenarios/booking/reschedule-webhook-log/) | Webhooks, Google Sheets, Slack | beginner | booking, reschedule, slack |
| [Route a booking ping by host name](scenarios/booking/round-robin-host-ping/) | Webhooks, OpenAI, Google Sheets, Slack | beginner | booking, round-robin, slack |

#### Reporting

| Scenario | Apps | Difficulty | Tags |
| --- | --- | --- | --- |
| [Ad spend rows with a plain-language note](scenarios/reporting/ad-spend-anomaly-note/) | Google Sheets, OpenAI, Slack | intermediate | reporting, ads, slack |
| [Daily sales rows to a Slack note](scenarios/reporting/daily-sales-digest/) | Google Sheets, OpenAI, Slack | beginner | reporting, sales, slack |
| [Hiring funnel counts to a short note](scenarios/reporting/hiring-funnel-note/) | Google Sheets, OpenAI, Slack, Gmail | beginner | hiring, reporting, slack |
| [Inventory value lines emailed to ops](scenarios/reporting/inventory-value-email/) | Google Sheets, OpenAI, Slack, Gmail | beginner | reporting, inventory, email |
| [Month-end checklist status to Slack](scenarios/reporting/month-end-checklist-note/) | Google Sheets, OpenAI, Slack | beginner | reporting, close, slack |
| [Pipeline snapshot rows to a Monday note](scenarios/reporting/pipeline-snapshot-note/) | Google Sheets, OpenAI, Slack | beginner | pipeline, reporting, slack |
| [Support volume narrative](scenarios/reporting/support-volume-narrative/) | Google Sheets, OpenAI, Slack, Gmail | beginner | reporting, support, slack |
| [Weekly KPI narrative to Slack and email](scenarios/reporting/weekly-kpi-slack-email/) | Google Sheets, OpenAI, Slack, Gmail | intermediate | reporting, kpi, google-sheets, slack, gmail, openai |

#### Slack, Notion, and ClickUp

| Scenario | Apps | Difficulty | Tags |
| --- | --- | --- | --- |
| [Bug report webhook to a ClickUp task](scenarios/slack-notion-clickup/bug-report-to-clickup/) | Webhooks, ClickUp, Google Sheets, Slack | intermediate | bugs, clickup, slack |
| [ClickUp status webhook to Slack](scenarios/slack-notion-clickup/clickup-status-to-slack/) | Webhooks, Google Sheets, Slack | beginner | clickup, status, slack |
| [Meeting notes webhook to ClickUp tasks](scenarios/slack-notion-clickup/meeting-notes-to-clickup/) | Webhooks, ClickUp, Google Sheets, Slack | intermediate | meetings, clickup, notes |
| [Notion comment webhook to Slack](scenarios/slack-notion-clickup/notion-comment-webhook-to-slack/) | Webhooks, Google Sheets, Slack | beginner | notion, comments, slack |
| [Slack shortcut to a Notion page and a ClickUp task](scenarios/slack-notion-clickup/slack-notion-clickup/) | Webhooks, OpenAI, Notion, ClickUp, Slack | intermediate | slack, notion, clickup, openai |
| [Standup sheet rows into Slack](scenarios/slack-notion-clickup/standup-rows-to-slack/) | Google Sheets, Slack | beginner | standup, slack, google-sheets |
| [Webhook a decision into a logged note](scenarios/slack-notion-clickup/sheet-row-to-notion-proxy/) | Webhooks, Google Sheets, Slack | beginner | decisions, notion, slack |

#### Scraping and enrichment

| Scenario | Apps | Difficulty | Tags |
| --- | --- | --- | --- |
| [Apify actor run, then a sheet log](scenarios/scraping-enrichment/apify-run-to-sheet-shape/) | Webhooks, Apify, Google Sheets, Slack | advanced | apify, scraping, google-sheets |
| [Company domain lookup logged to a sheet](scenarios/scraping-enrichment/clearbit-style-enrichment/) | Webhooks, HTTP, Google Sheets, Slack | intermediate | enrichment, http, google-sheets |
| [Fetch a company page and write a summary back to the sheet](scenarios/scraping-enrichment/scrape-enrich-sheets/) | Google Sheets, HTTP, OpenAI | intermediate | scraping, enrichment, google-sheets, openai, http |
| [Fetch a public page title into the sheet](scenarios/scraping-enrichment/public-page-title-fetch/) | Webhooks, HTTP, Google Sheets, Slack | intermediate | http, scraping, google-sheets |
| [Industry RSS items summarized to Slack](scenarios/scraping-enrichment/industry-rss-to-slack/) | RSS, OpenAI, Google Sheets, Slack | beginner | rss, research, slack |
| [Job RSS items scored into a sheet](scenarios/scraping-enrichment/job-feed-to-sheet/) | RSS, OpenAI, Google Sheets, Slack | intermediate | jobs, rss, hiring |
| [Release-notes feed for support](scenarios/scraping-enrichment/release-notes-for-support/) | RSS, OpenAI, Google Sheets, Slack | beginner | releases, rss, support |

#### AI agents

| Scenario | Apps | Difficulty | Tags |
| --- | --- | --- | --- |
| [Assistant that picks a tool, then answers](scenarios/ai-agents/assistant-agent-with-tools/) | Webhooks, OpenAI, Google Sheets, Slack | advanced | ai-agent, openai, tools, google-sheets, slack |
| [Claude summarizes a sheet cell](scenarios/ai-agents/claude-page-summary/) | Google Sheets, Anthropic Claude | intermediate | claude, summaries, google-sheets |
| [Gemini summarizes a sheet cell](scenarios/ai-agents/gemini-blurb-summary/) | Google Sheets, Gemini | intermediate | gemini, summaries, google-sheets |
| [Knowledge-base Q&A from a sheet](scenarios/ai-agents/knowledge-base-qa/) | Webhooks, Google Sheets, OpenAI | intermediate | knowledge-base, openai, google-sheets, qa |
| [Moderate a webhook comment](scenarios/ai-agents/moderation-allow-or-block/) | Webhooks, OpenAI, Google Sheets, Slack | advanced | moderation, openai, slack |
| [Onboarding questions to an agent](scenarios/ai-agents/onboarding-agent-webhook/) | Webhooks, Make AI Agent | advanced | ai-agent, onboarding, webhooks |
| [Policy agent over a webhook](scenarios/ai-agents/policy-agent-webhook/) | Webhooks, Make AI Agent | advanced | ai-agent, policy, webhooks |

#### HR and recruiting

| Scenario | Apps | Difficulty | Tags |
| --- | --- | --- | --- |
| [Draft a rejection from the stage in the subject](scenarios/hr-recruiting/rejection-stage-draft/) | Gmail, OpenAI, Google Sheets, Slack | advanced | hiring, rejections, gmail |
| [Draft an application acknowledgement](scenarios/hr-recruiting/application-ack-draft/) | Gmail, OpenAI, Google Sheets, Slack | beginner | hiring, gmail, drafts |
| [Employee referral to the hiring channel](scenarios/hr-recruiting/referral-candidate-slack/) | Webhooks, OpenAI, Google Sheets, Slack | beginner | hiring, referrals, slack |
| [Interview invite drafts from a sheet](scenarios/hr-recruiting/interview-invite-drafts/) | Google Sheets, Gmail | intermediate | hiring, interviews, gmail |
| [Interview notes to a scorecard cell](scenarios/hr-recruiting/interview-notes-scorecard/) | Google Sheets, OpenAI | intermediate | hiring, interviews, google-sheets |
| [Offer details logged for a human draft](scenarios/hr-recruiting/offer-details-draft-slot/) | Webhooks, Google Sheets, Slack | intermediate | hiring, offers, slack |
| [Parse a CV email and score it against a rubric](scenarios/hr-recruiting/hr-cv-parse-score/) | Gmail, OpenAI, Google Sheets, Slack | advanced | hr, cv, recruiting, gmail, openai |

#### Finance

| Scenario | Apps | Difficulty | Tags |
| --- | --- | --- | --- |
| [Bank export rows categorized into a sheet](scenarios/finance/bank-csv-rows-to-sheet/) | Webhooks, Google Sheets, Slack | advanced | bank, csv, reconciliation |
| [Failed payment webhook to email ops](scenarios/finance/stripe-payment-failed-text/) | Webhooks, Google Sheets, Slack | intermediate | stripe, dunning, slack |
| [Invoice paid webhook to Slack](scenarios/finance/invoice-paid-webhook/) | Webhooks, Google Sheets, Slack | beginner | invoices, payments, slack |
| [Monthly expense lines, described not judged](scenarios/finance/monthly-expense-anomaly/) | Google Sheets, OpenAI, Slack, Gmail | intermediate | expenses, reporting, email |
| [Stripe balance transactions into a reconciliation sheet](scenarios/finance/stripe-balance-reconciliation/) | Stripe, HTTP, Google Sheets, Slack | advanced | stripe, reconciliation, google-sheets, finance |
| [Stripe charge succeeded webhook to a sheet](scenarios/finance/stripe-charge-succeeded-log/) | Webhooks, Google Sheets, Slack | beginner | stripe, charges, slack |
| [Stripe refund webhook to the sheet](scenarios/finance/stripe-refund-log/) | Webhooks, Google Sheets, Slack | beginner | stripe, refunds, finance |
| [Subscription canceled webhook to Slack](scenarios/finance/subscription-canceled-log/) | Webhooks, Google Sheets, Slack | beginner | subscriptions, churn, slack |

## Validate

Make has no free import API in this repo's CI, and this project does not buy a plan. Every blueprint is a **documented blueprint, structurally validated**:

```bash
python3 -m pip install -r requirements.txt
python3 scripts/build_library.py
python3 scripts/validate_blueprints.py --min 100
python3 -m unittest tests/test_validator.py
```

The validator checks the JSON Schema in `schema/blueprint.schema.json`, the module allowlist in `schema/modules.allowlist.json`, `{{id.field}}` references, router and filter shape, aggregator feeders, and that no connection id, live webhook, or non-example email shipped.

Module ids come from Make's own scenario-building examples and from public blueprint exports. Apps whose module id was not in those sources are called with `http:ActionSendData` and the vendor's documented REST URL. See [MODULES.md](MODULES.md).

## Layout

```text
scenarios/<category>/<id>/
  blueprint.json      import this
  README.md           problem, walkthrough, setup
  sample-input.json   fictional first run
  diagram.png         flow diagram
  diagram.mmd         Mermaid source
catalog.json          gallery index
schema/               JSON Schema and module allowlist
```

## License

[MIT](LICENSE). Make, Integromat, and the names of the connected products are trademarks of their owners. This library is not affiliated with Make.
