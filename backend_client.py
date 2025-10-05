from typing import List, Optional, Literal
from pydantic import BaseModel
import httpx, os

BASE = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")

# --- Models odzwierciedlające swagger ---
class Report(BaseModel):
    id: Optional[int] = None
    likes: int
    dislikes: int
    verified: str
    description: str
    lattidude: float
    longidute: float
    route_name: str
    creator_id: int
    timestamp: int

class TripResponse(BaseModel):
    distance_m: int
    duration_s: int
    delay_s: int
    travel_mode: str

class ReportRequest(BaseModel):
    reporting_user_id: int
    description: str
    lattidude: float
    longidute: float
    route_name: str

class VerifyReportRequest(BaseModel):
    report_id: int
    verified: Literal["verified","unverified","spam","needs_review"]

class VoteRequest(BaseModel):
    action: Literal["like","dislike"]

# --- HTTP helpers ---
client = httpx.AsyncClient(base_url=BASE, timeout=10.0)

async def get_reports() -> List[Report]:
    r = await client.get("/reports/")
    r.raise_for_status()
    return [Report(**x) for x in r.json()]

async def get_reports_by_route(route_name: str) -> List[Report]:
    r = await client.get(f"/reports/route/{route_name}")
    r.raise_for_status()
    return [Report(**x) for x in r.json()]

async def create_report(payload: ReportRequest) -> Report:
    r = await client.post("/reports/", json=payload.model_dump())
    r.raise_for_status()
    return Report(**r.json())

async def vote_report(report_id: int, action: str) -> Report:
    r = await client.post(f"/reports/{report_id}/vote", json={"action": action})
    r.raise_for_status()
    return Report(**r.json())

async def verify_report(req: VerifyReportRequest) -> Report:
    r = await client.post("/dispatcher/reports/verify", params={"verified": req.verified}, json=req.model_dump())
    r.raise_for_status()
    return Report(**r.json())

async def trip(origin: str, destination: str) -> TripResponse:
    r = await client.post("/trip", json={"origin": origin, "destination": destination})
    r.raise_for_status()
    return TripResponse(**r.json())