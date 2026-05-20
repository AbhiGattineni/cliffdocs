"""Shared formatting for CLI stdout and MCP tool responses."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agent import RunResult


def run_result_to_dict(result: RunResult) -> dict[str, Any]:
    """Structured payload for MCP tools."""
    files: dict[str, str] = {}
    if result.saved.vitel:
        files["vitel"] = str(result.saved.vitel.resolve())
    if result.saved.linkedin:
        files["linkedin"] = str(result.saved.linkedin.resolve())
    if result.saved.combined:
        files["combined"] = str(result.saved.combined.resolve())

    reports: dict[str, str] = {}
    if result.vitel_text:
        reports["vitel"] = result.vitel_text
    if result.linkedin_text:
        reports["linkedin"] = result.linkedin_text
    if result.combined_text:
        reports["combined"] = result.combined_text

    return {
        "success": bool(files),
        "files": files,
        "reports": reports,
        "summary": format_run_result_text(result),
    }


def format_run_result_text(result: RunResult) -> str:
    """Human-readable report text (CLI and MCP summary field)."""
    if not result.saved.vitel and not result.saved.linkedin and not result.saved.combined:
        return "No reports generated."

    parts: list[str] = ["Reports generated:", ""]
    if result.saved.vitel and result.vitel_text:
        parts.extend([f"  Vitel:    {result.saved.vitel.resolve()}", "-" * 60, result.vitel_text, ""])
    if result.saved.linkedin and result.linkedin_text:
        parts.extend(
            [f"  LinkedIn: {result.saved.linkedin.resolve()}", "-" * 60, result.linkedin_text, ""]
        )
    if result.saved.combined and result.combined_text:
        parts.extend(
            [f"  Combined: {result.saved.combined.resolve()}", "-" * 60, result.combined_text, ""]
        )
    return "\n".join(parts).rstrip()


def path_listing(paths: list[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for p in paths:
        mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat()
        rows.append({"name": p.name, "path": str(p.resolve()), "modified": mtime})
    return rows
