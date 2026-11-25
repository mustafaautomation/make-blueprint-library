# Finance

Portfolio demos by Mustafa ([mustafaautomation](https://github.com/mustafaautomation)). Not client work.

Log charges, payouts, and categories for a human to reconcile.

| Scenario | Difficulty | Description |
| --- | --- | --- |
| [Bank export rows categorized into a sheet](bank-csv-rows-to-sheet/) | advanced | Split a posted array of bank lines into sheet rows and one Slack summary. |
| [Failed payment webhook to email ops](stripe-payment-failed-text/) | intermediate | Log a failed payment and always tell Slack. No charge is retried from here. |
| [Invoice paid webhook to Slack](invoice-paid-webhook/) | beginner | Log a paid-invoice event from the billing tool and tell Slack. |
| [Monthly expense lines, described not judged](monthly-expense-anomaly/) | intermediate | Describe the expense rows marked YES. Do not call them fraud. |
| [Stripe balance transactions into a reconciliation sheet](stripe-balance-reconciliation/) | advanced | Pull recent Stripe balance transactions, write one sheet row each, and post the id list to Slack. |
| [Stripe charge succeeded webhook to a sheet](stripe-charge-succeeded-log/) | beginner | Log a charge.succeeded payload and ping Slack at or above 1000. |
| [Stripe refund webhook to the sheet](stripe-refund-log/) | beginner | Log a Stripe refund and post the id. |
| [Subscription canceled webhook to Slack](subscription-canceled-log/) | beginner | Log a cancellation and post the plan name. |
