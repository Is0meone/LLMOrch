# tools.py
from langchain.tools import tool
from typing import List
from backend_client import (
    get_reports, get_reports_by_route, create_report, vote_report, verify_report, trip,
    ReportRequest, VerifyReportRequest, Report, TripResponse
)
from scoring import top_reports

@tool("get_city_situation", return_direct=False)
async def get_city_situation() -> str:
    """Zwróć syntetyczny opis sytuacji w mieście na podstawie najnowszych i najlepiej ocenionych raportów."""
    reports: List[Report] = await get_reports()
    best = top_reports(reports, k=5)
    lines = []
    for r in best:
        lines.append(f"[{r.route_name}] {r.description} (👍{r.likes}/👎{r.dislikes}, {r.verified})")
    if not lines:
        return "Brak świeżych raportów."
    return "Najważniejsze teraz:\n" + "\n".join(lines)

@tool("get_line_situation", return_direct=False)
async def get_line_situation(route_name: str) -> str:
    """Streszcz sytuację dla danej linii (route_name)."""
    reports = await get_reports_by_route(route_name)
    if not reports:
        return f"Brak raportów dla linii {route_name}."
    best = top_reports(reports, k=5)
    parts = [f"{route_name}: {len(reports)} raportów – najważniejsze:"]
    for r in best:
        parts.append(f"- {r.description} (👍{r.likes}/👎{r.dislikes}, {r.verified})")
    return "\n".join(parts)

@tool("plan_trip", return_direct=False)
async def plan_trip(origin: str, destination: str) -> str:
    """Podaj ETA i opóźnienie dla przejazdu z origin do destination."""
    t: TripResponse = await trip(origin, destination)
    mins = round(t.duration_s/60)
    delay = round(t.delay_s/60)
    return f"Tryb: {t.travel_mode}. Szacowany czas: {mins} min. Opóźnienie: ~{delay} min."

@tool("report_issue", return_direct=False)
async def report_issue(reporting_user_id: int, description: str, lattidude: float, longidute: float, route_name: str) -> str:
    """Utwórz nowe zgłoszenie utrudnienia."""
    r = await create_report(ReportRequest(
        reporting_user_id=reporting_user_id, description=description,
        lattidude=lattidude, longidute=longidute, route_name=route_name
    ))
    return f"Zgłoszono (id={r.id}): {r.route_name} – {r.description}"

@tool("vote_issue", return_direct=False)
async def vote_issue(report_id: int, action: str) -> str:
    """Zagłosuj na zgłoszenie (like/dislike)."""
    r = await vote_report(report_id, action)
    return f"Raport {r.id}: 👍{r.likes}/👎{r.dislikes}"

@tool("verify_issue", return_direct=False)
async def verify_issue(report_id: int, verified: str) -> str:
    """Zmień status weryfikacji (verified/unverified/spam/needs_review)."""
    r = await verify_report(VerifyReportRequest(report_id=report_id, verified=verified))
    return f"Raport {r.id}: status={r.verified}"
