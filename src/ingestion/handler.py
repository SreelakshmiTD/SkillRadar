import json
import logging
import os

from github_client import GitHubClient
from adzuna_client import AdzunaClient
from youtube_client import YouTubeClient
from skill_extractor import extract_skills
from scorer import compute_quality_score
from s3_writer import S3Writer

logger = logging.getLogger()
logger.setLevel(logging.INFO)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
ADZUNA_APP_ID = os.environ.get("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.environ.get("ADZUNA_APP_KEY")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
S3_RAW_BUCKET = os.environ.get("S3_RAW_BUCKET")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
SKILLS = os.environ.get("SKILLS", "").split(",")


def lambda_handler(event, context):
    logger.info(f"Starting SkillRadar ingestion for {len(SKILLS)} skills")

    github = GitHubClient(token=GITHUB_TOKEN)
    adzuna = AdzunaClient(app_id=ADZUNA_APP_ID, app_key=ADZUNA_APP_KEY)
    youtube = YouTubeClient(api_key=YOUTUBE_API_KEY)
    writer = S3Writer(bucket=S3_RAW_BUCKET, region=AWS_REGION)

    github_records = []
    adzuna_records = []
    youtube_records = []

    for skill in SKILLS:
        if not skill.strip():
            continue

        skill = skill.strip()

        repos = github.fetch_repos_for_skill(skill, days_back=30)
        for repo in repos:
            matched_skills = extract_skills(repo)
            quality_score = compute_quality_score(repo)
            github_records.append({
                **repo,
                "matched_skills": matched_skills,
                "quality_score": quality_score
            })

        adzuna_records.extend(adzuna.fetch_job_count_for_skill(skill))
        youtube_records.extend(youtube.fetch_video_count_for_skill(skill, days_back=30))

    github_written = writer.write_records(github_records, source="github")
    adzuna_written = writer.write_records(adzuna_records, source="adzuna")
    youtube_written = writer.write_records(youtube_records, source="youtube")

    total_written = github_written + adzuna_written + youtube_written
    logger.info(f"Ingestion complete. Total records written: {total_written}")

    return {
        "statusCode": 200,
        "records_written": {
            "github": github_written,
            "adzuna": adzuna_written,
            "youtube": youtube_written,
            "total": total_written
        },
        "skills_processed": len(SKILLS)
    }


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="../../.env")

    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
    ADZUNA_APP_ID = os.environ.get("ADZUNA_APP_ID")
    ADZUNA_APP_KEY = os.environ.get("ADZUNA_APP_KEY")
    YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
    S3_RAW_BUCKET = os.environ.get("S3_RAW_BUCKET")
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
    SKILLS = os.environ.get("SKILLS", "").split(",")

    result = lambda_handler({}, {})
    print(json.dumps(result, indent=2))
