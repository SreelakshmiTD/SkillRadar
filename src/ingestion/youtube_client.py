import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict

logger = logging.getLogger()

YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/search"


class YouTubeClient:
    """Fetches video counts from YouTube Data API v3 by skill keyword."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch_video_count_for_skill(self, skill: str, days_back: int = 30) -> List[Dict]:
        """
        Search YouTube for videos mentioning a skill published in the last N days.
        Appends 'tutorial data engineering' to reduce noise from generic terms.
        Returns a single record with total video count.
        """
        since_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%SZ")

        params = {
            "key": self.api_key,
            "q": f"{skill} tutorial data engineering",
            "type": "video",
            "part": "id",
            "publishedAfter": since_date,
            "maxResults": 1
        }

        try:
            response = requests.get(YOUTUBE_API_URL, params=params, timeout=10)

            if response.status_code == 403:
                logger.error(f"{skill}: YouTube quota exceeded or API key invalid")
                return []

            if response.status_code != 200:
                logger.error(f"{skill}: YouTube HTTP {response.status_code}")
                return []

            data = response.json()
            total_count = data.get("pageInfo", {}).get("totalResults", 0)
            logger.info(f"{skill}: youtube total_count={total_count}")

            return [{
                "searched_skill": skill,
                "source": "youtube",
                "total_count": total_count,
                "collected_at": datetime.utcnow().isoformat()
            }]

        except Exception as e:
            logger.error(f"{skill}: YouTube error — {str(e)}")
            return []
