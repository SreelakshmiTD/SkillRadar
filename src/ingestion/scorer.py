import math
from datetime import datetime, timezone
from typing import Dict

STARS_CAP = 10_000
FORKS_CAP = 5_000
RECENCY_WINDOW_DAYS = 30

WEIGHT_STARS = 0.4
WEIGHT_FORKS = 0.3
WEIGHT_RECENCY = 0.3


def compute_quality_score(repo: Dict) -> float:
    stars = repo.get("stars", 0)
    forks = repo.get("forks", 0)
    created_at_str = repo.get("created_at", "")

    star_score = min(math.log1p(stars) / math.log1p(STARS_CAP), 1.0)
    fork_score = min(math.log1p(forks) / math.log1p(FORKS_CAP), 1.0)
    recency_score = _recency_score(created_at_str)

    return round(
        WEIGHT_STARS * star_score +
        WEIGHT_FORKS * fork_score +
        WEIGHT_RECENCY * recency_score,
        4
    )


def _recency_score(created_at_str: str) -> float:
    if not created_at_str:
        return 0.0
    try:
        created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
        days_old = (datetime.now(timezone.utc) - created_at).days
        return max(0.0, 1.0 - days_old / RECENCY_WINDOW_DAYS)
    except Exception:
        return 0.0
