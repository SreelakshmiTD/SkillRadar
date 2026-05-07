from dotenv import load_dotenv
import os
load_dotenv()
# AWS
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_ACCOUNT_ID = os.getenv('AWS_ACCOUNT_ID')
# Kinesis
KINESIS_STREAM_NAME = os.getenv('KINESIS_STREAM_NAME')
# S3
S3_RAW_BUCKET = os.getenv('S3_RAW_BUCKET')
S3_PROCESSED_BUCKET = os.getenv('S3_PROCESSED_BUCKET')
# SQS
SQS_DLQ_URL = os.getenv('SQS_DLQ_URL')
# IAM
PRODUCER_ROLE_ARN = os.getenv('PRODUCER_ROLE_ARN')
CONSUMER_ROLE_ARN = os.getenv('CONSUMER_ROLE_ARN')
AGGREGATOR_ROLE_ARN = os.getenv('AGGREGATOR_ROLE_ARN')
# Subreddits
SUBREDDITS = os.getenv('SUBREDDITS', '').split(',')
