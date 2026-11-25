# Invoices and documents

Portfolio demos by Mustafa ([mustafaautomation](https://github.com/mustafaautomation)). Not client work.

Pull fields out of invoices, receipts, and other documents.

| Scenario | Difficulty | Description |
| --- | --- | --- |
| [AI invoice extraction from Gmail to Sheets, Xero, or QuickBooks](ai-invoice-gmail-sheets-xero/) | intermediate | Read an invoice email, write the fields to a sheet, and draft a bill in Xero or QuickBooks when the model is confident. |
| [Invoice email flagged for approval over 5000](invoice-approval-by-amount/) | intermediate | Log an invoice email and ping Slack for approval when the total is at least 5000. |
| [Possible duplicate invoice subjects](duplicate-invoice-subject/) | intermediate | Extract the invoice number and ping Slack so a person can spot a duplicate. |
| [Receipt email to an expense sheet](receipt-to-expense-sheet/) | beginner | Pull merchant, date, and total from a receipt email and flag anything over 200. |
| [Tell a credit note from an invoice](credit-note-or-invoice/) | intermediate | Classify a finance email as invoice or credit note and log the signed amount. |
| [Vendor statement email into a sheet](vendor-statement-to-sheet/) | intermediate | Read a monthly vendor statement email and log the balance due. |
| [W-9 style email logged as received](w9-email-to-sheet/) | beginner | Log that a vendor emailed a tax form. Do not store the form number in Slack. |
