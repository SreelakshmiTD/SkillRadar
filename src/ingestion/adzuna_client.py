import logging
import requests
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger()

ADZUNA_API_URL = "https://api.adzuna.com/v1/api/jobs"


class AdzunaClient:
    """Fetches job posting counts from Adzuna API by skill keyword."""

    def __init__(self, app_id: str, app_key: str, country: str = "us"):
        self.app_id = app_id
        self.app_key = app_key
        self.country = country

    def fetch_job_count_for_skill(self, skill: str) -> List[Dict]:
        """
        Search Adzuna for jobs mentioning a skill.
        Returns a single record with total job count.
        """
        url = f"{ADZUNA_API_URL}/{self.country}/search/1"

        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "what": skill,
            "results_per_page": 1
        }

        try:
            response = requests.get(url, params=params, timeout=10)

            if response.status_code != 200:
                logger.error(f"{skill}: Adzuna HTTP {response.status_code}")
                return []

            data = response.json()
            total_count = data.get("count", 0)
            logger.info(f"{skill}: adzuna total_count={total_count}")

            return [{
                "searched_skill": skill,
                "source": "adzuna",
                "total_count": total_count,
                "collected_at": datetime.utcnow().isoformat()
            }]

        except Exception as e:
            logger.error(f"{skill}: Adzuna error — {str(e)}")
            return []
