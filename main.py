import argparse
import sys

from dotenv import load_dotenv

from agent import ReportAgent

load_dotenv()


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

    print("\nReports generated:\n")
    if result.saved.vitel:
        print(f"  Vitel:    {result.saved.vitel.resolve()}")
        print("-" * 60)
        print(result.vitel_text)
        print()
    if result.saved.linkedin:
        print(f"  LinkedIn: {result.saved.linkedin.resolve()}")
        print("-" * 60)
        print(result.linkedin_text)
        print()
    if result.saved.combined:
        print(f"  Combined: {result.saved.combined.resolve()}")
        print("-" * 60)
        print(result.combined_text)
        print()


if __name__ == "__main__":
    main()
