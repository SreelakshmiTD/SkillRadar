# SkillRadar

A data engineering pipeline that tracks which tech skills are trending globally, based on real GitHub activity.

Instead of relying on job postings or surveys, SkillRadar queries GitHub's API to measure how many new repositories are being created around each technology — giving a ground-truth signal of what developers are actually building with.

## What it does

SkillRadar ingests GitHub repository data for 31 tracked skills, stores it in a partitioned S3 data lake, and makes it queryable via Athena. Run a query and get real numbers like:

- Python: 156,761 new repos in the last 30 days
- Kafka: 4,233 new repos in the last 30 days
- dbt: 3,123 new repos in the last 30 days

## Architecture

    GitHub Search API
            |
            v
    AWS Lambda (Python 3.11)
    Skill extraction + data collection
            |
            v
    Amazon S3 (Raw layer)
    Partitioned by year/month/day
            |
            v
    AWS Glue Data Catalog
    Auto schema inference
            |
            v
    Amazon Athena
    SQL queries on skill trends

## Tech Stack

- Python 3.11
- AWS Lambda
- Amazon S3
- AWS Glue Data Catalog
- Amazon Athena
- GitHub Search API

## Build Phases

### Phase 1 (Complete)
GitHub ingestion Lambda writing to S3, Glue catalog, first Athena queries showing real skill demand data.

### Phase 2 (In Progress)
Scheduled ingestion via EventBridge. Daily runs. Week-over-week trend comparisons.

### Phase 3 (Planned)
Multi-source ingestion. Add YouTube tutorial data and job posting signals alongside GitHub data.

### Phase 4 (Planned)
Intelligence layer. PySpark aggregations on EMR Serverless. Emerging skill detection using GitHub topic frequency and co-occurrence analysis. Hype ratio scoring.

### Phase 5 (Planned)
Observability. CloudWatch metrics, SNS alerts on skill spikes, ingestion lag monitoring.

## Skills Tracked

spark, pyspark, kafka, flink, airflow, prefect, dagster, dbt, iceberg, hudi, delta, snowflake, databricks, redshift, bigquery, trino, duckdb, polars, kubernetes, terraform, docker, python, scala, sql, elasticsearch, clickhouse, pinot, mlflow, datahub, openmetadata, great_expectations

## Running Locally

    git clone https://github.com/SreelakshmiTD/SkillRadar.git
    cd SkillRadar

    python3.11 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

    cp .env.example .env
    # Fill in GITHUB_TOKEN, AWS credentials, S3 bucket name

    cd src/ingestion
    python3 handler.py

## Sample Athena Query

    SELECT searched_skill, MAX(total_count) as total_repos
    FROM skillradar.github
    GROUP BY searched_skill
    ORDER BY total_repos DESC
    LIMIT 15;

## Status

Phase 1 complete. Building in public. Follow along as each phase gets added.
