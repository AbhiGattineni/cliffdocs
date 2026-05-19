import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

INBOX_DIR = Path("reports/inbox")
OUTPUT_DIR = Path(os.getenv("REPORT_OUTPUT_DIR", "reports/output"))


@dataclass
class SavedReports:
    vitel: Path | None = None
    linkedin: Path | None = None
    combined: Path | None = None


def resolve_vitel_csv_path(
    cli_path: str | None = None,
    *,
    interactive: bool = True,
    use_picker: bool = False,
) -> Path | None:
    if cli_path:
        return _require_path(cli_path, (".csv",))
    if path := os.getenv("VITEL_CSV"):
        return _require_path(path, (".csv",))
    found = _latest_in_inbox(
        r".*callrecords.*\.csv$", r"vitel.*\.csv$", r"vitel\d+.*\.csv$", r".*\.csv$"
    )
    if found:
        return found
    if not interactive:
        return None
    if use_picker:
        return _pick_or_prompt(
            label="Vitel Global weekly CDR (.csv)",
            extensions=(".csv",),
            skippable=False,
            force_picker=True,
        )
    return _prompt_file(
        label="Vitel Global weekly CDR (.csv)",
        extensions=(".csv",),
        skippable=False,
    )


def resolve_linkedin_xlsx_path(
    cli_path: str | None = None,
    *,
    interactive: bool = True,
    use_picker: bool = False,
) -> Path | None:
    if cli_path:
        return _require_path(cli_path, (".xlsx", ".xls"))
    if path := os.getenv("LINKEDIN_XLSX"):
        return _require_path(path, (".xlsx", ".xls"))
    found = _latest_in_inbox(
        r".*inmail.*\.xlsx$", r"linkedin.*\.xlsx$", r"linkedin\d+.*\.xlsx$", r".*\.xlsx$"
    )
    if found:
        return found
    if not interactive:
        return None
    if use_picker:
        return _pick_or_prompt(
            label="LinkedIn InMail report (.xlsx)",
            extensions=(".xlsx", ".xls"),
            skippable=True,
            force_picker=True,
        )
    return _prompt_file(
        label="LinkedIn InMail report (.xlsx)",
        extensions=(".xlsx", ".xls"),
        skippable=True,
    )


def save_reports(
    vitel_text: str | None,
    linkedin_text: str | None,
    combined_text: str | None,
) -> SavedReports:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    saved = SavedReports()

    if vitel_text:
        saved.vitel = _write(OUTPUT_DIR / f"vitel_report_{stamp}.txt", vitel_text)
    if linkedin_text:
        saved.linkedin = _write(OUTPUT_DIR / f"linkedin_report_{stamp}.txt", linkedin_text)
    if combined_text:
        saved.combined = _write(OUTPUT_DIR / f"combined_report_{stamp}.txt", combined_text)

    return saved


def _write(path: Path, body: str) -> Path:
    path.write_text(body, encoding="utf-8")
    return path


def _pick_or_prompt(
    *,
    label: str,
    extensions: tuple[str, ...],
    skippable: bool,
    force_picker: bool,
) -> Path | None:
    from file_picker import pick_file

    print(f"\n{label}")
    print("  Opening file picker...")
    path = pick_file(
        title=label,
        extensions=extensions,
        initial_dir=Path.home() / "Downloads",
    )
    if path:
        return path
    print("  No file selected — you can type a path instead.")
    return _prompt_file(label=label, extensions=extensions, skippable=skippable)


def _prompt_file(
    *,
    label: str,
    extensions: tuple[str, ...],
    skippable: bool,
) -> Path | None:
    from file_picker import pick_file

    downloads = Path.home() / "Downloads"
    print(f"\n{label}")
    print(f"  Options:")
    print(f"    • Press Enter or type 'browse' — choose file from folder")
    print(f"    • Type a path (e.g. vitel519 or Downloads/vitel519)")
    print(f"    • Copy file into {INBOX_DIR.resolve()}/")
    if skippable:
        print("    • Type 'q' to skip")
    while True:
        raw = input("Path: ").strip().strip('"')
        if skippable and raw.lower() in ("q", "quit", "skip"):
            return None
        if raw.lower() in ("browse", "b", "pick", "file") or raw == "":
            path = pick_file(
                title=label,
                extensions=extensions,
                initial_dir=downloads,
            )
            if path:
                print(f"  Selected: {path}")
                return path
            print("  No file selected — try again or type a path.")
            if not skippable:
                continue
            return None
        resolved = _resolve_upload_path(raw, extensions)
        if resolved:
            return resolved
        print(
            f"  Not found (need {', '.join(extensions)}). "
            f"Tried under project folder and {downloads}"
        )


def _require_path(path: str, extensions: tuple[str, ...] = (".csv", ".xlsx", ".xls")) -> Path:
    resolved = _resolve_upload_path(path, extensions)
    if resolved:
        return resolved
    raise FileNotFoundError(f"Report file not found: {path}")


def _resolve_upload_path(raw: str, extensions: tuple[str, ...]) -> Path | None:
    """Resolve shorthand paths like Downloads/vitel519 or vitel519.csv."""
    text = raw.strip().strip('"')
    p = Path(text).expanduser()

    candidates: list[Path] = []
    if p.is_absolute():
        candidates.append(p)
    else:
        downloads = Path.home() / "Downloads"
        candidates.extend([
            Path.cwd() / p,
            downloads / p,
            downloads / p.name,
            Path.home() / p,
            p,
        ])
        # "Downloads/file" -> ~/Downloads/file
        parts = p.parts
        if parts and parts[0].lower() == "downloads":
            rest = Path(*parts[1:]) if len(parts) > 1 else Path()
            candidates.append(downloads / rest)

    seen: set[Path] = set()
    for base in candidates:
        for path in _expand_path_candidates(base, extensions):
            key = path.resolve()
            if key in seen:
                continue
            seen.add(key)
            if path.is_file() and path.suffix.lower() in extensions:
                return path

    # Last resort: match by stem in ~/Downloads (e.g. vitel519 -> vitel519.csv)
    stem = p.stem or p.name
    downloads = Path.home() / "Downloads"
    if downloads.is_dir() and stem:
        for ext in extensions:
            for match in downloads.glob(f"{stem}*{ext}"):
                if match.is_file():
                    return match
    return None


def _expand_path_candidates(base: Path, extensions: tuple[str, ...]) -> list[Path]:
    out = [base]
    if base.suffix == "":
        out.extend(base.with_suffix(ext) for ext in extensions)
    return out


def _latest_in_inbox(*patterns: str) -> Path | None:
    if not INBOX_DIR.is_dir():
        return None
    candidates: list[Path] = []
    for path in INBOX_DIR.iterdir():
        if not path.is_file():
            continue
        name = path.name.lower()
        if any(re.search(pat, name, re.IGNORECASE) for pat in patterns):
            candidates.append(path)
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)
