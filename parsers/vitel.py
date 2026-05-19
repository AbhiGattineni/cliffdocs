import csv
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class VitelExtension:
    extension: str
    name: str
    inbound_calls: int
    outbound_calls: int
    total_calls: int
    total_duration: str


@dataclass
class VitelReport:
    period_label: str
    extensions: list[VitelExtension] = field(default_factory=list)

    @property
    def active_extensions(self) -> list[VitelExtension]:
        return [e for e in self.extensions if e.total_calls > 0]

    @property
    def total_calls(self) -> int:
        return sum(e.total_calls for e in self.extensions)


_PERIOD_RE = re.compile(
    r"from\s+'([^']+)'\s+to\s+'([^']+)'",
    re.IGNORECASE,
)


def _to_int(value: str | None) -> int:
    if value is None or str(value).strip() == "":
        return 0
    try:
        return int(float(str(value).strip()))
    except ValueError:
        return 0


def parse_vitel_cdr_csv(path: str | Path) -> VitelReport:
    path = Path(path)
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    period_label = _extract_period(text, path.name)

    extensions: list[VitelExtension] = []
    reader = csv.reader(text.splitlines())
    for row in reader:
        if not row or not row[0].strip().isdigit():
            continue
        if len(row) < 9:
            continue
        extn = row[1].strip()
        if not extn.isdigit():
            continue
        extensions.append(
            VitelExtension(
                extension=extn,
                name=row[2].strip() or extn,
                inbound_calls=_to_int(row[3]),
                outbound_calls=_to_int(row[5]),
                total_calls=_to_int(row[7]),
                total_duration=(row[8].strip() if len(row) > 8 else "00:00:00"),
            )
        )

    return VitelReport(period_label=period_label, extensions=extensions)


def _extract_period(text: str, filename: str) -> str:
    match = _PERIOD_RE.search(text)
    if match:
        start, end = match.group(1), match.group(2)
        return f"{start[:10]} to {end[:10]}"
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
    if date_match:
        return f"Week of {date_match.group(1)}"
    return "Weekly period (see source email)"
