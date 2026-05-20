import argparse
import sys

from dotenv import load_dotenv

load_dotenv()


def _ensure_project_deps() -> None:
    try:
        import openpyxl  # noqa: F401
    except ImportError:
        print(
            "Missing dependency openpyxl. Use the project virtualenv:\n"
            "  uv sync\n"
            "  uv run python main.py --vitel vitel519 --linkedin linkedin519\n"
            "Or: .venv\\Scripts\\python.exe main.py ...",
            file=sys.stderr,
        )
        raise SystemExit(1) from None


_ensure_project_deps()

from agent import ReportAgent
from report_output import format_run_result_text


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Weekly team usage report agent (local files only)",
    )
    parser.add_argument(
        "--vitel",
        metavar="PATH",
        help="Vitel Global weekly CDR .csv",
    )
    parser.add_argument(
        "--linkedin",
        metavar="PATH",
        help="LinkedIn InMail report .xlsx",
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Only use --vitel/--linkedin, env vars, or reports/inbox/ (no prompts)",
    )
    parser.add_argument(
        "--no-combined",
        action="store_true",
        help="Skip combined summary file",
    )
    parser.add_argument(
        "--pick",
        action="store_true",
        help="Choose files with a folder/file dialog (no typing paths)",
    )
    args = parser.parse_args()

    try:
        result = ReportAgent().run(
            vitel_path=args.vitel,
            linkedin_path=args.linkedin,
            interactive=not args.no_prompt,
            use_picker=args.pick,
            write_combined=not args.no_combined,
        )
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print()
    print(format_run_result_text(result))


if __name__ == "__main__":
    main()
