from dotenv import load_dotenv
import os

load_dotenv()

# AWS
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_ACCOUNT_ID = os.getenv('AWS_ACCOUNT_ID')

# S3
S3_RAW_BUCKET = os.getenv('S3_RAW_BUCKET')
S3_PROCESSED_BUCKET = os.getenv('S3_PROCESSED_BUCKET')

# GitHub
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

# Skills
SKILLS = os.getenv('SKILLS', '').split(',')
