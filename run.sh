#!/usr/bin/env bash
# Run CLI with project dependencies (avoids system Python missing openpyxl).
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT" || exit 1
exec "$ROOT/.venv/Scripts/python.exe" main.py "$@"
