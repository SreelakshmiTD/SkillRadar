# Reddit Job Market Intelligence Pipeline

An event-driven data pipeline on AWS that ingests posts from 9 developer subreddits every 2 minutes, extracts technology and skill mentions, and enables SQL-based trend analysis on developer job market signals over time.

---

## Problem

Tech job market signals are scattered across Reddit in unstructured text. There is no systematic way to track which skills are in demand, how hiring patterns shift month over month, or which technologies are gaining or losing momentum in developer communities. This pipeline solves that by continuously ingesting, structuring, and making that data queryable.

---

## Architecture

```
EventBridge Scheduler (every 2 min)
        |
        v
Lambda — Producer
  - Polls Reddit API via PRAW
  - Fetches new posts from 9 subreddits
  - Pushes each post as a record to Kinesis
        |
        v
Kinesis Data Streams (1 shard)
  - Decouples producer from consumer
  - Buffers records for replay on failure
  - 24-hour retention (free tier)
        |
        v
Lambda — Consumer
  - Reads records from Kinesis
  - Writes raw JSON to S3 partitioned by subreddit/year/month/day
        |
        v
S3 — Raw Layer (JSON)
  - Schema-on-read
  - Preserves original data for reprocessing
        |
        v
EventBridge Scheduler (hourly)
        |
        v
Lambda — Aggregator
  - Reads raw JSON from S3
  - Extracts: tech mentions, job type, location, remote signals
  - Writes Parquet to S3 processed layer
        |
        v
S3 — Processed Layer (Parquet)
  - Columnar, compressed
  - Partitioned by subreddit/year/month/day
  - Faster and cheaper Athena queries vs JSON
        |
        v
AWS Glue Data Catalog
  - Registers processed layer schema
  - Enables Athena to query without manual DDL
        |
        v
Amazon Athena
  - SQL queries on processed Parquet
  - Trend analysis, YoY comparisons, skill rankings
        |
        v
CloudWatch + SNS + SQS DLQ
  - CloudWatch: metrics per Lambda (records in, records out, errors)
  - SNS: email alert on Lambda failure or low extraction rate
  - SQS DLQ: catches failed invocations for inspection and reprocessing
```

---

## Subreddits Monitored

| Subreddit | Focus |
|---|---|
| r/dataengineering | Data engineering roles and tools |
| r/datascience | Data science hiring and skills |
| r/MachineLearning | ML engineering and research |
| r/python | Python ecosystem trends |
| r/javascript | Frontend and full-stack |
| r/webdev | Web development roles |
| r/devops | DevOps and infrastructure |
| r/programming | General software engineering |
| r/cscareerquestions | Broad developer job market signals |

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Data source | Reddit API via PRAW | Free, reliable, covers 9 active developer communities |
| Scheduling | AWS EventBridge | Serverless, native AWS scheduler, no infrastructure to manage |
| Ingestion | AWS Lambda (producer) | Event-driven, no persistent compute needed for polling workload |
| Streaming buffer | Amazon Kinesis Data Streams | Decouples producer and consumer, enables record replay on failure, handles burst traffic across 9 subreddits |
| Raw storage | Amazon S3 (JSON) | Schema-on-read, cheap, preserves original data for reprocessing if extraction logic changes |
| Transformation | AWS Lambda (aggregator) | Lightweight keyword extraction does not require distributed compute |
| Processed storage | Amazon S3 (Parquet) | Columnar and compressed — Athena scans significantly less data vs JSON |
| Schema registry | AWS Glue Data Catalog | Free for first million objects, required by Athena, no ETL cost |
| Analytics | Amazon Athena | Pay-per-query, no cluster to manage, zero idle cost unlike Redshift |
| Observability | Amazon CloudWatch + SNS | Native AWS, no additional tooling, free tier covers this scale |
| Failure handling | Amazon SQS DLQ | Failed Lambda invocations captured for inspection and reprocessing |
| Access control | AWS IAM | Least privilege — one role per Lambda, scoped to only required actions |

---

## IAM Design

Three separate roles, one per Lambda function. Each role has only the permissions it needs.

| Role | Permissions |
|---|---|
| techpulse-producer-role | Kinesis PutRecord, CloudWatch Logs |
| techpulse-consumer-role | Kinesis GetRecords, S3 PutObject (raw bucket), SQS SendMessage, CloudWatch Logs |
| techpulse-aggregator-role | S3 GetObject (raw bucket), S3 PutObject (processed bucket), CloudWatch Logs |

---

## Project Structure

```
techpulse/
├── src/
│   ├── producer/
│   │   └── handler.py          # EventBridge → PRAW → Kinesis
│   ├── consumer/
│   │   └── handler.py          # Kinesis → S3 raw
│   ├── aggregator/
│   │   └── handler.py          # S3 raw → skill extraction → S3 processed Parquet
│   └── config.py               # Loads .env variables
├── infra/
│   └── setup.sh                # CLI commands to create all AWS resources
├── scripts/
│   └── verify_pipeline.py      # End-to-end smoke test
├── tests/
│   └── test_extraction.py      # Unit tests for skill mention extraction
├── .env.example                # Template — copy to .env and fill in values
├── requirements.txt
└── README.md
```

---

## Setup

**Prerequisites**
- Python 3.11
- AWS CLI configured (`aws configure`)
- Reddit API credentials (reddit.com/prefs/apps)
- AWS account with free tier active

**Clone and install**
```bash
git clone https://github.com/SreelakshmiTD/techpulse.git
cd techpulse
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Configure environment**
```bash
cp .env.example .env
# Fill in your Reddit API credentials and AWS account ID
```

**Create AWS infrastructure**
```bash
bash infra/setup.sh
```

This creates: S3 buckets, Kinesis stream, SQS DLQ, and IAM roles.

**Deploy Lambda functions**
See Milestone 2 build plan for step-by-step Lambda deployment instructions.

---

## Sample Athena Queries

**Top 10 skills mentioned across all subreddits this month**
```sql
SELECT skill, COUNT(*) as mentions
FROM processed.job_posts
WHERE year = '2026' AND month = '05'
GROUP BY skill
ORDER BY mentions DESC
LIMIT 10;
```

**Skill trend year over year**
```sql
SELECT skill, year, COUNT(*) as mentions
FROM processed.job_posts
WHERE skill IN ('python', 'spark', 'kafka', 'dbt', 'airflow')
GROUP BY skill, year
ORDER BY skill, year;
```

**Remote vs onsite signal over time**
```sql
SELECT year, month,
  SUM(CASE WHEN is_remote = true THEN 1 ELSE 0 END) as remote_mentions,
  SUM(CASE WHEN is_remote = false THEN 1 ELSE 0 END) as onsite_mentions
FROM processed.job_posts
GROUP BY year, month
ORDER BY year, month;
```

**Which subreddit mentions data engineering tools most**
```sql
SELECT subreddit, skill, COUNT(*) as mentions
FROM processed.job_posts
WHERE skill IN ('spark', 'kafka', 'airflow', 'dbt', 'databricks')
GROUP BY subreddit, skill
ORDER BY mentions DESC;
```

---

## Observability

**CloudWatch metrics tracked per Lambda:**
- Records received (producer)
- Records written to S3 (consumer)
- Extraction success rate (aggregator)
- Lambda errors and duration

**SNS alerts fire when:**
- Any Lambda errors in a 5-minute window
- Extraction success rate drops below 70% (indicates Reddit post format changed)
- Kinesis iterator age grows beyond 5 minutes (consumer falling behind)

**SQS DLQ:** Failed Lambda invocations land here for manual inspection and reprocessing.

---

## Architectural Decisions

**Why Kinesis and not writing directly to S3 from the producer?**
Kinesis decouples the producer from the consumer. If the consumer Lambda is slow, throttled, or fails, records buffer in Kinesis for up to 24 hours and can be replayed. Writing directly to S3 from the producer loses this safety net.

**Why Lambda and not Glue ETL for transformation?**
The aggregator does keyword matching and regex extraction on individual records. It does not require distributed compute. Glue ETL charges per DPU-hour with a minimum billing of 10 minutes per job. Lambda handles this workload well within its 15-minute limit at effectively zero cost.

**Why Athena and not Redshift?**
Redshift charges for a running cluster regardless of whether queries are being run. Athena charges only per query at $5 per TB scanned. At this data volume, Athena costs cents per month. There is no cluster to provision, configure, or maintain.

**Why Parquet in the processed layer and not JSON?**
Athena reads columnar format significantly faster than row-based JSON because it only scans the columns referenced in the query. A query filtering by skill reads only the skill column, not the entire record. This directly reduces scan volume and cost.

---

## Status

Pipeline complete. Running in production on AWS.
