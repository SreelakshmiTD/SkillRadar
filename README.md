# SkillRadar

A data engineering pipeline that tracks which tech skills are trending globally, using three independent signals: GitHub repository activity, job postings, and YouTube tutorial volume.

Instead of relying on surveys or opinion pieces, SkillRadar queries live APIs to measure real developer activity, real hiring demand, and real learning interest — then cross-references them to separate genuine adoption from hype.

## What it does

SkillRadar ingests data for 31 tracked skills across three sources, stores everything in a partitioned S3 data lake, and makes it queryable via Athena. Each daily run captures:

- **GitHub** — how many new repos are being created around each skill (developer adoption signal)
- **Adzuna** — how many job postings mention each skill (hiring demand signal)
- **YouTube** — how many tutorials were published around each skill (learning interest signal)

Sample output (single day):
- PySpark: 4,500 GitHub repos / 3,213 Adzuna jobs / 483 YouTube tutorials
- Kafka: 4,233 GitHub repos / 11,010 Adzuna jobs / 3,058 YouTube tutorials
- dbt: 3,123 GitHub repos / 16,624 Adzuna jobs / 331 YouTube tutorials

## Architecture

    GitHub Search API    Adzuna Jobs API    YouTube Data API v3
            |                   |                   |
            v                   v                   v
                    AWS Lambda (Python 3.11)
              Skill extraction + quality scoring
                            |
                            v
                  Amazon EventBridge
                  Daily schedule trigger
                            |
                            v
                  Amazon S3 (Raw layer)
          Partitioned by source / year / month / day
          github/year=.../month=.../day=.../
          adzuna/year=.../month=.../day=.../
          youtube/year=.../month=.../day=.../
                            |
                            v
                  AWS Glue Data Catalog
                  Auto schema inference
                            |
                            v
                    Amazon Athena
          SQL queries across all three sources

## Tech Stack

- Python 3.11
- AWS Lambda
- Amazon EventBridge
- Amazon S3
- AWS Glue Data Catalog
- Amazon Athena
- GitHub Search API
- Adzuna Jobs API
- YouTube Data API v3

## Build Phases

### Phase 1 (Complete)
GitHub ingestion Lambda writing to S3, Glue catalog, first Athena queries showing real skill demand data. 906 records across 31 skills.

### Phase 2 (Complete)
Weighted quality scoring per repo using log-normalized stars, forks, and recency. EventBridge daily scheduling — Lambda runs automatically every 24 hours, accumulating snapshots for trend comparisons. Week-over-week Athena query saved as named query.

### Phase 3 (Complete)
Multi-source ingestion. Adzuna job postings and YouTube tutorial counts added alongside GitHub. S3 partitioned by source. Three independent Athena tables queryable together to compare signals across sources.

### Phase 4 (Planned)
AI skill dictionary expansion. Automated discovery of emerging skills not in the initial tracked list. Hype vs real adoption classification using cross-source signal analysis.

### Phase 5 (Planned)
Intelligence layer. PySpark aggregations on EMR Serverless. Hype ratio scoring by cross-referencing GitHub, Adzuna, and YouTube signals. Co-occurrence analysis to identify skill clusters and emerging technology pairs.

### Phase 6 (Planned)
Observability. CloudWatch metrics, SNS alerts on skill spikes, ingestion lag monitoring.

### Phase 7 (Planned)
Streamlit dashboard. Skill demand trends visualization over time. Cross-source signal comparison charts. Week-over-week growth rankings.

## Skills Tracked

spark, pyspark, kafka, flink, airflow, prefect, dagster, dbt, iceberg, hudi, delta, snowflake, databricks, redshift, bigquery, trino, duckdb, polars, kubernetes, terraform, docker, python, scala, sql, elasticsearch, clickhouse, pinot, mlflow, datahub, openmetadata, great_expectations

## Running Locally

    git clone https://github.com/SreelakshmiTD/SkillRadar.git
    cd SkillRadar

    python3.11 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

    cp .env.example .env
    # Fill in GITHUB_TOKEN, ADZUNA_APP_ID, ADZUNA_APP_KEY,
    # YOUTUBE_API_KEY, AWS credentials, S3 bucket name

    cd src/ingestion
    python3 handler.py

## Sample Athena Queries

**Top skills by GitHub demand:**

    SELECT searched_skill, MAX(total_count) as total_repos
    FROM skillradar.github
    GROUP BY searched_skill
    ORDER BY total_repos DESC
    LIMIT 15;

**Top skills by job postings:**

    SELECT searched_skill, MAX(total_count) as total_jobs
    FROM skillradar.adzuna
    GROUP BY searched_skill
    ORDER BY total_jobs DESC
    LIMIT 15;

**Cross-source signal comparison:**

    SELECT
        g.searched_skill,
        MAX(g.total_count) AS github_repos,
        MAX(a.total_count) AS adzuna_jobs,
        MAX(y.total_count) AS youtube_videos
    FROM skillradar.github g
    JOIN skillradar.adzuna a ON g.searched_skill = a.searched_skill
    JOIN skillradar.youtube y ON g.searched_skill = y.searched_skill
    GROUP BY g.searched_skill
    ORDER BY adzuna_jobs DESC
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

Phases 1, 2, and 3 complete. Building in public. Follow along as each phase gets added.
