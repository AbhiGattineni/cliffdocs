"""MCP server for Cursor / Claude Desktop — same ReportAgent as the CLI."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from agent import ReportAgent
from report_output import path_listing, run_result_to_dict
from report_paths import INBOX_DIR

load_dotenv()

mcp = FastMCP("team-usage-report")

_INBOX_PATTERNS = (
    r".*callrecords.*\.csv$",
    r"vitel.*\.csv$",
    r".*inmail.*\.xlsx$",
    r"linkedin.*\.xlsx$",
)


def _inbox_files() -> list[Path]:
    if not INBOX_DIR.is_dir():
        return []
    out: list[Path] = []
    for path in INBOX_DIR.iterdir():
        if not path.is_file():
            continue
        name = path.name.lower()
        if any(re.search(pat, name, re.IGNORECASE) for pat in _INBOX_PATTERNS):
            out.append(path)
    return sorted(out, key=lambda p: p.stat().st_mtime, reverse=True)


@mcp.tool()
def generate_usage_report(
    vitel_path: str | None = None,
    linkedin_path: str | None = None,
    write_combined: bool = True,
) -> dict[str, Any]:
    """
    Generate weekly Vitel (phone) and/or LinkedIn (InMail) usage reports.

    Provide file paths, or leave blank to use VITEL_CSV / LINKEDIN_XLSX env vars
    or the newest matching files in reports/inbox/.
    """
    result = ReportAgent().run(
        vitel_path=vitel_path,
        linkedin_path=linkedin_path,
        interactive=False,
        use_picker=False,
        write_combined=write_combined,
    )
    return run_result_to_dict(result)


@mcp.tool()
def list_inbox_reports() -> dict[str, Any]:
    """List report source files currently in reports/inbox/."""
    files = _inbox_files()
    return {
        "inbox_dir": str(INBOX_DIR.resolve()),
        "count": len(files),
        "files": path_listing(files),
        "hint": "Copy weekly .csv / .xlsx files here, then call generate_usage_report without paths.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Team usage report MCP server (stdio).")
    parser.add_argument(
        "--stdio",
        action="store_true",
        help="Run as MCP stdio server (default; use in Cursor / Claude Desktop).",
    )
    parser.parse_args()
    mcp.run()


if __name__ == "__main__":
    main()
