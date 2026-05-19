from datetime import datetime

from parsers import LinkedInReport, VitelReport


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def format_vitel_report(report: VitelReport) -> str:
    lines = [
        "VITEL GLOBAL - WEEKLY PHONE USAGE REPORT",
        f"Generated: {_timestamp()}",
        "",
        *_format_vitel_section(report),
    ]
    return "\n".join(lines)


def format_linkedin_report(report: LinkedInReport) -> str:
    lines = [
        "LINKEDIN RECRUITER - WEEKLY SEATS & INMAIL REPORT",
        f"Generated: {_timestamp()}",
        "",
        *_format_linkedin_section(report),
    ]
    return "\n".join(lines)


def format_combined_report(
    vitel: VitelReport | None,
    linkedin: LinkedInReport | None,
) -> str:
    lines = [
        "WEEKLY TEAM USAGE REPORT (COMBINED)",
        f"Generated: {_timestamp()}",
        "",
    ]

    if vitel:
        lines.extend(_format_vitel_section(vitel))
    else:
        lines.extend(["PHONE - VITEL GLOBAL", "  (not provided)", ""])

    if linkedin:
        lines.extend(_format_linkedin_section(linkedin))
    else:
        lines.extend(["LINKEDIN RECRUITER", "  (not provided)", ""])

    lines.extend(_format_totals(vitel, linkedin))
    return "\n".join(lines)


def _format_vitel_section(report: VitelReport) -> list[str]:
    lines = [
        "PHONE - VITEL GLOBAL (extensions / seats)",
        f"Period: {report.period_label}",
        "",
        f"{'Extension':<12} {'Name':<10} {'Outbound':>10} {'Inbound':>10} {'Total':>8} {'Duration':>12}",
        "-" * 66,
    ]
    for ext in sorted(report.extensions, key=lambda e: e.total_calls, reverse=True):
        lines.append(
            f"{ext.extension:<12} {ext.name:<10} {ext.outbound_calls:>10} "
            f"{ext.inbound_calls:>10} {ext.total_calls:>8} {ext.total_duration:>12}"
        )
    active = len(report.active_extensions)
    lines.extend(
        [
            "",
            f"Extensions with usage: {active} / {len(report.extensions)}",
            f"Total calls (all extensions): {report.total_calls}",
            "",
        ]
    )
    return lines


def _format_linkedin_section(report: LinkedInReport) -> list[str]:
    lines = [
        "LINKEDIN RECRUITER - SEATS & INMAIL USAGE",
        f"Period: {report.period_label}",
        "",
        f"{'Seat holder':<22} {'State':<10} {'Location':<14} {'InMails':>8} {'Responses':>10} {'Accepts':>8}",
        "-" * 76,
    ]
    for seat in sorted(report.seats, key=lambda s: s.inmails_sent, reverse=True):
        lines.append(
            f"{seat.seat_holder:<22} {seat.seat_state:<10} {seat.location:<14} "
            f"{seat.inmails_sent:>8} {seat.responses:>10} {seat.accepts:>8}"
        )
    active = len(report.active_seats)
    lines.extend(
        [
            "",
            f"Seats with InMail activity: {active} / {len(report.seats)}",
            f"Total InMails sent: {report.total_inmails_sent}",
            "",
        ]
    )
    return lines


def _format_totals(
    vitel: VitelReport | None,
    linkedin: LinkedInReport | None,
) -> list[str]:
    lines = ["SUMMARY"]
    if vitel:
        lines.append(
            f"  Vitel: {len(vitel.active_extensions)} active extensions, "
            f"{vitel.total_calls} calls"
        )
    if linkedin:
        lines.append(
            f"  LinkedIn: {len(linkedin.seats)} seat(s), "
            f"{linkedin.total_inmails_sent} InMails sent"
        )
    return lines
