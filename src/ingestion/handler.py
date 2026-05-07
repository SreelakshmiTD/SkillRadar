import json
import logging
import os

from github_client import GitHubClient
from skill_extractor import extract_skills
from s3_writer import S3Writer

logger = logging.getLogger()
logger.setLevel(logging.INFO)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
S3_RAW_BUCKET = os.environ.get("S3_RAW_BUCKET")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
SKILLS = os.environ.get("SKILLS", "").split(",")


def lambda_handler(event, context):
    logger.info(f"Starting SkillRadar ingestion for {len(SKILLS)} skills")

    github = GitHubClient(token=GITHUB_TOKEN)
    writer = S3Writer(bucket=S3_RAW_BUCKET, region=AWS_REGION)

    all_records = []

    for skill in SKILLS:
        if not skill.strip():
            continue

        repos = github.fetch_repos_for_skill(skill.strip(), days_back=30)

        for repo in repos:
            matched_skills = extract_skills(repo)
            record = {
                **repo,
                "matched_skills": matched_skills
            }
            all_records.append(record)

    total_written = writer.write_records(all_records)
    logger.info(f"Ingestion complete. Total records written: {total_written}")

    return {
        "statusCode": 200,
        "records_written": total_written,
        "skills_processed": len(SKILLS)
    }


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="../../.env")

    # Reload env vars after dotenv loads
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
    S3_RAW_BUCKET = os.environ.get("S3_RAW_BUCKET")
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
    SKILLS = os.environ.get("SKILLS", "").split(",")

    result = lambda_handler({}, {})
    print(json.dumps(result, indent=2))
