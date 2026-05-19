"""Local report agent: parse uploaded Vitel + LinkedIn files and write separate outputs."""

from dataclasses import dataclass
from pathlib import Path

from parsers import LinkedInReport, VitelReport, parse_linkedin_report, parse_vitel_cdr_csv
from report_paths import SavedReports, resolve_linkedin_xlsx_path, resolve_vitel_csv_path, save_reports
from summary import format_combined_report, format_linkedin_report, format_vitel_report


@dataclass
class RunResult:
    vitel: VitelReport | None
    linkedin: LinkedInReport | None
    saved: SavedReports
    vitel_text: str | None
    linkedin_text: str | None
    combined_text: str | None


class ReportAgent:
    """Processes manually provided weekly usage reports."""

    def run(
        self,
        *,
        vitel_path: str | None = None,
        linkedin_path: str | None = None,
        interactive: bool = True,
        use_picker: bool = False,
        write_combined: bool = True,
    ) -> RunResult:
        vitel_file = resolve_vitel_csv_path(
            vitel_path, interactive=interactive, use_picker=use_picker
        )
        linkedin_file = resolve_linkedin_xlsx_path(
            linkedin_path, interactive=interactive, use_picker=use_picker
        )

        if not vitel_file and not linkedin_file:
            raise FileNotFoundError(
                "No input reports. Provide --vitel and/or --linkedin, "
                f"place files in reports/inbox/, or enter paths when prompted."
            )

        vitel = parse_vitel_cdr_csv(vitel_file) if vitel_file else None
        linkedin = parse_linkedin_report(linkedin_file) if linkedin_file else None

        vitel_text = format_vitel_report(vitel) if vitel else None
        linkedin_text = format_linkedin_report(linkedin) if linkedin else None
        combined_text = None
        if write_combined and (vitel or linkedin):
            combined_text = format_combined_report(vitel, linkedin)

        saved = save_reports(vitel_text, linkedin_text, combined_text)

        return RunResult(
            vitel=vitel,
            linkedin=linkedin,
            saved=saved,
            vitel_text=vitel_text,
            linkedin_text=linkedin_text,
            combined_text=combined_text,
        )
