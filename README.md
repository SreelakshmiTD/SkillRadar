# SkillRadar

A data engineering pipeline that tracks which tech skills are trending globally, based on real GitHub activity.

Instead of relying on job postings or surveys, SkillRadar queries GitHub's API to measure how many new repositories are being created around each technology — giving a ground-truth signal of what developers are actually building with.

## What it does

SkillRadar ingests GitHub repository data for 31 tracked skills, stores it in a partitioned S3 data lake, and makes it queryable via Athena. Each run captures two signals per skill:

- **total_count** — raw demand volume from GitHub Search API
- **quality_score** — weighted score combining stars (40%), forks (30%), and recency (30%), log-normalized to handle long-tail distributions

Sample output:
- Python: 156,761 new repos in the last 30 days
- Kafka: 4,233 new repos in the last 30 days
- dbt: 3,123 new repos in the last 30 days

## Architecture

    GitHub Search API
            |
            v
    AWS Lambda (Python 3.11)
    Skill extraction + quality scoring
            |
            v
    Amazon EventBridge
    Daily schedule trigger
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
    SQL queries on skill trends and week-over-week growth

## Tech Stack

- Python 3.11
- AWS Lambda
- Amazon EventBridge
- Amazon S3
- AWS Glue Data Catalog
- Amazon Athena
- GitHub Search API

## Build Phases

### Phase 1 (Complete)
GitHub ingestion Lambda writing to S3, Glue catalog, first Athena queries showing real skill demand data. 906 records across 31 skills.

### Phase 2 (Complete)
Weighted quality scoring per repo using log-normalized stars, forks, and recency. EventBridge daily scheduling — Lambda runs automatically every 24 hours, accumulating snapshots for trend comparisons. Week-over-week Athena query saved as named query.

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

## Sample Athena Queries

**Top skills by demand:**

    SELECT searched_skill, MAX(total_count) as total_repos
    FROM skillradar.github
    GROUP BY searched_skill
    ORDER BY total_repos DESC
    LIMIT 15;

**Top skills by quality score:**

    SELECT searched_skill, ROUND(AVG(quality_score), 3) as avg_quality
    FROM skillradar.github
    WHERE year='2026' AND month='05'
    GROUP BY searched_skill
    ORDER BY avg_quality DESC
    LIMIT 15;

**Week-over-week growth:**

    WITH daily AS (
      SELECT searched_skill,
             date(collected_at) AS run_date,
             MAX(total_count) AS total_repos,
             AVG(quality_score) AS avg_quality_score
      FROM skillradar.github
      GROUP BY 1, 2
    ),
    with_lag AS (
      SELECT searched_skill, run_date, total_repos, avg_quality_score,
             LAG(total_repos) OVER (PARTITION BY searched_skill ORDER BY run_date) AS prev_day_repos
      FROM daily
    )
    SELECT searched_skill, run_date, total_repos, prev_day_repos,
           ROUND((total_repos - prev_day_repos) * 100.0 / NULLIF(prev_day_repos, 0), 1) AS pct_change,
           ROUND(avg_quality_score, 3) AS avg_quality_score
    FROM with_lag
    WHERE prev_day_repos IS NOT NULL
    ORDER BY run_date DESC, pct_change DESC;

## Status

Phase 1 and Phase 2 complete. Building in public. Follow along as each phase gets added.
