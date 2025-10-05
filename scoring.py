from typing import List
from backend_client import Report
import time

def score_report(r: Report, now:int|None=None) -> float:
    now = now or int(time.time())
    age_min = max(1, (now - r.timestamp) / 60)  # świeżość (minuty)
    vote_balance = r.likes - r.dislikes
    verified_boost = {"verified": 2.0, "needs_review": 1.0, "unverified": 0.7, "spam": 0.1}.get(r.verified, 1.0)
    return (1 + vote_balance*0.2) * verified_boost / (1 + age_min*0.02)

def top_reports(reports: List[Report], k: int = 5) -> List[Report]:
    return sorted(reports, key=score_report, reverse=True)[:k]