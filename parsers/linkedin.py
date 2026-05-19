import re
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd


@dataclass
class LinkedInSeat:
    seat_holder: str
    seat_id: str
    seat_state: str
    location: str
    inmails_sent: int
    responses: int
    accepts: int
    response_rate_pct: float | None


@dataclass
class LinkedInReport:
    period_label: str
    seats: list[LinkedInSeat] = field(default_factory=list)

    @property
    def active_seats(self) -> list[LinkedInSeat]:
        return [s for s in self.seats if s.inmails_sent > 0]

    @property
    def total_inmails_sent(self) -> int:
        return sum(s.inmails_sent for s in self.seats)


def parse_linkedin_report(path: str | Path) -> LinkedInReport:
    path = Path(path)
    period_label = _extract_period_from_overview(path)
    df = pd.read_excel(path, sheet_name="Seats")
    df.columns = [str(c).strip() for c in df.columns]

    seats: list[LinkedInSeat] = []
    for _, row in df.iterrows():
        source = str(row.get("Candidate Source", "")).strip()
        if source and source.lower() != "overall":
            continue
        holder = str(row.get("Seat Holder", "")).strip()
        if not holder or holder.lower() == "seat holder":
            continue
        seats.append(
            LinkedInSeat(
                seat_holder=holder,
                seat_id=str(row.get("Seat Id", "")).strip(),
                seat_state=str(row.get("Seat State", "")).strip(),
                location=str(row.get("Seat Location", "")).strip(),
                inmails_sent=_to_int(row.get("Sends")),
                responses=_to_int(row.get("Responses")),
                accepts=_to_int(row.get("Accepts")),
                response_rate_pct=_to_float(row.get("Response Rate %")),
            )
        )

    return LinkedInReport(period_label=period_label, seats=seats)


def _extract_period_from_overview(path: Path) -> str:
    try:
        overview = pd.read_excel(path, sheet_name="Overview", header=None)
    except (ValueError, KeyError):
        return _period_from_filename(path.name)

    for i in range(len(overview) - 1):
        label = str(overview.iloc[i, 0]).strip().lower()
        if label != "date range":
            continue
        next_row = overview.iloc[i + 1]
        if str(next_row.iloc[0]).strip().upper() == "EQUALS":
            value = str(next_row.iloc[1]).strip()
        else:
            value = str(next_row.iloc[0]).strip()
        if value and value.lower() not in ("equals", "nan"):
            return value
    return _period_from_filename(path.name)


def _period_from_filename(name: str) -> str:
    match = re.search(
        r"(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})",
        name,
    )
    if match:
        return f"{match.group(1)} to {match.group(2)}"
    return "Weekly period (see source email)"


def _to_int(value: object) -> int:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _to_float(value: object) -> float | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
