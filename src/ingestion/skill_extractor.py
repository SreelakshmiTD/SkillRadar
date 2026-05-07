from typing import List, Dict


SKILLS = [
    "spark", "pyspark", "kafka", "flink", "airflow", "prefect", "dagster",
    "dbt", "iceberg", "hudi", "delta", "snowflake", "databricks", "redshift",
    "bigquery", "trino", "duckdb", "polars", "kubernetes", "terraform",
    "docker", "python", "scala", "sql", "elasticsearch", "clickhouse",
    "pinot", "mlflow", "datahub", "openmetadata", "great_expectations"
]


def extract_skills(repo: Dict) -> List[str]:
    """
    Extract which skills from our dictionary appear in a repo.
    Checks: topics, description, and repo name.
    Returns list of matched skills.
    """
    matched = set()

    # Check topics — most reliable signal
    topics = [t.lower() for t in repo.get("topics", [])]
    for skill in SKILLS:
        if skill.lower() in topics:
            matched.add(skill)

    # Check description
    description = repo.get("description", "").lower()
    for skill in SKILLS:
        if skill.lower() in description:
            matched.add(skill)

    # Check repo name
    repo_name = repo.get("repo_name", "").lower()
    for skill in SKILLS:
        if skill.lower() in repo_name:
            matched.add(skill)

    return list(matched)
