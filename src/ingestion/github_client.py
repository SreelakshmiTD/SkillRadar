import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict

import requests

logger = logging.getLogger()

GITHUB_API_URL = "https://api.github.com/search/repositories"
RESULTS_PER_PAGE = 30


class GitHubClient:
    """Fetches repositories from GitHub search API by skill keyword."""

    def __init__(self, token: str):
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    def fetch_repos_for_skill(self, skill: str, days_back: int = 30) -> List[Dict]:
        """
        Search GitHub for repos mentioning a skill in name, description or topics,
        created in the last N days.
        Stores total_count as the real demand signal.
        Returns a list of structured repo records.
        """
        since_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        query = f"{skill} in:name,description,topics created:>{since_date}"

        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": RESULTS_PER_PAGE
        }

        try:
            response = requests.get(
                GITHUB_API_URL,
                headers=self.headers,
                params=params,
                timeout=10
            )

            if response.status_code == 403:
                logger.error(f"{skill}: rate limited — waiting 60 seconds")
                time.sleep(60)
                return []

            if response.status_code != 200:
                logger.error(f"{skill}: HTTP {response.status_code}")
                return []

            data = response.json()
            total_count = data.get("total_count", 0)
            repos = data.get("items", [])
            logger.info(f"{skill}: total_count={total_count}, fetching top {len(repos)}")

            return [self._parse_repo(repo, skill, total_count) for repo in repos]

        except Exception as e:
            logger.error(f"{skill}: error — {str(e)}")
            return []

    def _parse_repo(self, repo: dict, skill: str, total_count: int) -> Dict:
        """Extract relevant fields from a GitHub repo response."""
        return {
            "repo_name":      repo["full_name"],
            "description":    repo.get("description", "") or "",
            "stars":          repo.get("stargazers_count", 0),
	    "forks":          repo.get("forks_count", 0),           
 	    "language":       repo.get("language", "") or "",
            "topics":         repo.get("topics", []),
            "created_at":     repo.get("created_at", ""),
            "updated_at":     repo.get("updated_at", ""),
            "url":            repo.get("html_url", ""),
            "searched_skill": skill,
            "total_count":    total_count,
            "collected_at":   datetime.utcnow().isoformat()
        }
