"""More portfolio scenarios, built with the factories in rest_items.py."""

from makebp.specs.rest_items import D, EACH, G, H, HTTP, ITER, ROW, RSS

B: list[dict] = [
    G(
        id="legal-keyword-mail-to-slack",
        title="Flag legal keywords in the shared inbox",
        category="email",
        difficulty="beginner",
        tags=["email", "legal", "slack", "gmail"],
        apps=["Gmail", "OpenAI", "Google Sheets", "Slack"],
        description="Log inbound mail and ping Slack when the model sees a contract, lawsuit, or subpoena.",
        problem="A shared inbox treats a subpoena like a newsletter until someone notices the subject line. This demo reads the inbox minus promotions, logs every message, and pings Slack only when the model sets legal to true.",
        audience="Operators of a shared Gmail who need a loud signal for legal mail and a quiet log for everything else.",
        time_saved="The save is the one message a month you would have missed. Sorting the rest is about a minute a message you no longer open.",
        schedule="Every 10 minutes.",
        query="in:inbox -category:promotions newer_than:2d",
        system="Decide if the email needs a lawyer's eyes. Return JSON only: legal (true or false), topic (one of contract, lawsuit, subpoena, none), summary.",
        columns=["A received_at", "B from", "C subject", "D legal", "E topic", "F summary"],
        row=["{{now}}", "{{mail.from}}", "{{mail.subject}}", "{{parsed.legal}}", "{{parsed.topic}}", "{{parsed.summary}}"],
        slack="*Legal mail* {{parsed.topic}} from {{mail.from}}: {{parsed.summary}}",
        subject="Subpoena for records",
        body="Please produce records for matter 19-CV-100 by December 12.",
        sender="counsel@example.com",
        gate=("Legal is true", "{{parsed.legal}}", "text:equal", "true"),
    ),
]
