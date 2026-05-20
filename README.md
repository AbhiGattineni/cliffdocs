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
uv venv && uv sync
cp .env.example .env   # optional local paths only
```

**Important:** Use the project venv or `uv run` — system `python` often lacks `openpyxl`:

```bash
uv run python main.py --vitel vitel519 --linkedin linkedin519
# or (Git Bash / PowerShell)
./run.sh --vitel vitel519 --linkedin linkedin519
.\run.ps1 --vitel vitel519 --linkedin linkedin519
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

## MCP tool (Cursor & Claude Desktop)

The same `ReportAgent` logic powers the CLI and an MCP server.

**1. Install and sync**

```bash
uv venv && .venv\Scripts\activate
uv sync
```

**2. Add to Cursor** — merge into `%USERPROFILE%\.cursor\mcp.json` (see `mcp.json.example`):

```json
"team-usage-report": {
  "command": "C:\\Users\\you\\Documents\\Project Source code\\morning-brief-agent-main\\.venv\\Scripts\\python.exe",
  "args": [
    "C:\\Users\\you\\Documents\\Project Source code\\morning-brief-agent-main\\mcp_server.py",
    "--stdio"
  ],
  "cwd": "C:\\Users\\you\\Documents\\Project Source code\\morning-brief-agent-main"
}
```

Restart Cursor (or reload MCP servers).

**3. Add to Claude Desktop** — edit `%APPDATA%\\Claude\\claude_desktop_config.json` with the same `team-usage-report` block, then restart Claude.

**MCP tools**

| Tool | Purpose |
|------|---------|
| `generate_usage_report` | Build reports from paths, `.env`, or `reports/inbox/` |
| `list_inbox_reports` | List files waiting in the inbox |

Example chat: *“List inbox reports, then generate this week’s combined usage report.”*

Run the MCP server manually (for debugging):

```bash
python mcp_server.py --stdio
```

Or after `uv sync`: `team-usage-report-mcp --stdio`

## Project layout

```
main.py           # CLI entry
mcp_server.py     # MCP entry (Cursor / Claude)
agent.py          # orchestration (shared)
report_output.py  # shared CLI + MCP formatting
parsers/          # Vitel CSV + LinkedIn Seats sheet
summary.py        # report formatting
report_paths.py   # inbox, prompts, save outputs
reports/inbox/    # put weekly source files here
reports/output/   # generated reports
mcp.json.example  # copy paths into Cursor / Claude config
```

---

Copyright©️ Codebasics Inc. All rights reserved.
# cliffdocs
