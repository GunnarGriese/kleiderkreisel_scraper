# Website crawler for kleiderkreisel.de

This repository contains exemplary code on how to deploy your own website crawler for kleiderkreisel.de search results hosted on GCP. The crawler leverages beautifulsoup as well as pandas to scrape search results and write them to Google BigQuery. The code itself is deployed to Google Cloud Functions and triggered by a cron job hosted on Google Cloud Scheduler. The crawling results are then visualised in a Google Datastudio dashboard. 

## Prerequisites

* Setup your own GCP project and enable BigQuery API as well as Cloud Functions API (free trial available)
* Install [Google Cloud SDK](https://cloud.google.com/sdk/)

## Step by step guide

1. Create Google BigQuery to store crawling results

2. Deploy Cloud Function (*/cld_function*):

```bash
gcloud functions deploy kleiderkreisel_scraper --project project-name --region europe-west1 --trigger-http --runtime python37
```

3. Deploy Google Cloud Scheduler [cron job](https://cloud.google.com/scheduler/docs/quickstart) to run once a day

4. Use [Google Datastudio](https://datastudio.google.com/open/1bXc3qFjAdCmSS2uBJQ9RrqvE3LvHnIGU) to visualise crawling results (*/sql_dashboard*)

## Outcome

Interactive Google Datastudio dashboard in which different periods of time can be analysed:

[](/img/dashboard.png)