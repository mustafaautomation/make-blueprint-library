# AI agents

Portfolio demos by Mustafa ([mustafaautomation](https://github.com/mustafaautomation)). Not client work.

Let a model choose a tool, then answer from the tool result.

| Scenario | Difficulty | Description |
| --- | --- | --- |
| [Assistant that picks a tool, then answers](assistant-agent-with-tools/) | advanced | A webhook assistant chooses sheets lookup, an HTTP lookup, or a Slack note, then answers from that tool's result. |
| [Claude summarizes a sheet cell](claude-page-summary/) | intermediate | When a long note lands in column A, Claude writes a three-sentence summary in column B. |
| [Gemini summarizes a sheet cell](gemini-blurb-summary/) | intermediate | Write a two-sentence Gemini summary of column A into column B. |
| [Knowledge-base Q&A from a sheet](knowledge-base-qa/) | intermediate | Pull matching FAQ rows, aggregate them, and answer a webhook question from that text only. |
| [Moderate a webhook comment](moderation-allow-or-block/) | advanced | Score a comment and ping Slack only when it should be blocked. |
| [Onboarding questions to an agent](onboarding-agent-webhook/) | advanced | An agent that answers onboarding questions from a fixed three-step checklist. |
| [Policy agent over a webhook](policy-agent-webhook/) | advanced | Answer a webhook with a Make AI agent that is instructed to refuse anything outside the written policy. |
