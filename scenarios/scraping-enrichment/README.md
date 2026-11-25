# Scraping and enrichment

Portfolio demos by Mustafa ([mustafaautomation](https://github.com/mustafaautomation)). Not client work.

Fetch a public page or dataset and land it in a sheet.

| Scenario | Difficulty | Description |
| --- | --- | --- |
| [Apify actor run, then a sheet log](apify-run-to-sheet-shape/) | advanced | Start an Apify actor from a webhook and log the run id. Dataset rows are a second step you confirm. |
| [Company domain lookup logged to a sheet](clearbit-style-enrichment/) | intermediate | Look up a domain on a placeholder enrichment URL and log the status. |
| [Fetch a company page and write a summary back to the sheet](scrape-enrich-sheets/) | intermediate | When a domain is added to a sheet, fetch the homepage, strip the HTML, and write a two-sentence summary onto the same row. |
| [Fetch a public page title into the sheet](public-page-title-fetch/) | intermediate | GET a URL the webhook names and log the status. The sample URL is example.com. |
| [Industry RSS items summarized to Slack](industry-rss-to-slack/) | beginner | Summarize a new industry feed item in two sentences and post it with the link. |
| [Job RSS items scored into a sheet](job-feed-to-sheet/) | intermediate | Summarize a job-feed item and keep the link. Slack gets every new item. |
| [Release-notes feed for support](release-notes-for-support/) | beginner | Turn a release-notes item into two sentences a support agent can say. |
