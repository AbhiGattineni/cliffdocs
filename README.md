# Team Usage Report Agent

A **local** Python agent that reads weekly reports you upload manually, extracts the stats you need, and writes **separate formatted reports** to disk.

No Zapier, no Gmail, no LLM — only deterministic parsing of your source files.

## Supported inputs

| Source | File | What we extract |
|--------|------|-----------------|
| **Vitel Global** | `.csv` (CDR weekly call records) | Per-extension calls: outbound, inbound, total, duration |
| **LinkedIn Recruiter** | `.xlsx` (InMail Status Report) | Per-seat InMails sent, responses, accepts |

## Outputs

Each run creates timestamped files under `reports/output/`:

- `vitel_report_YYYY-MM-DD_HHMM.txt` — phone / extension usage only  
- `linkedin_report_YYYY-MM-DD_HHMM.txt` — seats & InMail usage only  
- `combined_report_YYYY-MM-DD_HHMM.txt` — both sections + summary (unless `--no-combined`)

## Setup

```bash
uv venv && .venv\Scripts\activate
uv sync
cp .env.example .env   # optional local paths only
```

Optional `.env` (never commit `.env` — it is gitignored):

```env
VITEL_CSV=C:\path\to\weekly_callrecords.csv
LINKEDIN_XLSX=C:\path\to\Inmail_Report.xlsx
REPORT_OUTPUT_DIR=reports/output
```

## Ways to provide files

| Method | How |
|--------|-----|
| **File picker** | `python main.py --pick` — Windows/macOS dialog |
| **Browse at prompt** | Run `python main.py`, press **Enter** or type `browse` |
| **Short path** | `vitel519` or `Downloads/vitel519` (auto-finds in your Downloads folder) |
| **Full path** | `C:\Users\you\Downloads\vitel519.csv` |
| **CLI flags** | `--vitel path.csv --linkedin path.xlsx` |
| **Inbox folder** | Copy files into `reports/inbox/`, then `python main.py --no-prompt` |
| **`.env`** | `VITEL_CSV=...` and `LINKEDIN_XLSX=...` |

## Usage

**Easiest — pick files from a dialog:**

```bash
python main.py --pick
```

**Interactive (Enter = browse, or type a path):**

```bash
python main.py
```

**Command line paths:**

```bash
python main.py --vitel vitel519 --linkedin linkedin519
```

**Inbox only (no prompts):**

```bash
python main.py --no-prompt
```

## Project layout

```
main.py           # CLI entry
agent.py          # orchestration
parsers/          # Vitel CSV + LinkedIn Seats sheet
summary.py        # report formatting
report_paths.py   # inbox, prompts, save outputs
reports/inbox/    # put weekly source files here
reports/output/   # generated reports
```

---

Copyright©️ Codebasics Inc. All rights reserved.
# cliffdocs
