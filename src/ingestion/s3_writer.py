import json
import logging
from datetime import datetime
from typing import List, Dict

import boto3

logger = logging.getLogger()


class S3Writer:
    """Writes skill trend records to S3 raw layer, partitioned by date."""

    def __init__(self, bucket: str, region: str = "us-east-1"):
        self.bucket = bucket
        self.client = boto3.client("s3", region_name=region)

    def write_records(self, records: List[Dict]) -> int:
        """
        Write records to S3 as newline-delimited JSON.
        Partitioned by year/month/day.
        Returns number of records written.
        """
        if not records:
            logger.info("No records to write")
            return 0

        now = datetime.utcnow()
        partition = f"year={now.year}/month={now.month:02d}/day={now.day:02d}"
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        key = f"github/{partition}/skillradar_{timestamp}.json"

        body = "\n".join(json.dumps(record) for record in records)

        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=body.encode("utf-8"),
                ContentType="application/json"
            )
            logger.info(f"Wrote {len(records)} records to s3://{self.bucket}/{key}")
            return len(records)

        except Exception as e:
            logger.error(f"S3 write failed: {str(e)}")
            return 0
