#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
XLSX="${1:-$ROOT/data/DR303e26v101.xlsx}"
CSV_DIR="$ROOT/csv_x2c"

if [[ ! -f "$XLSX" ]]; then
  echo "XLSX not found: $XLSX"
  exit 1
fi

PYTHONPATH="$ROOT" python3 "$ROOT/scripts/xlsx_to_csv.py" "$XLSX" "$CSV_DIR"
PYTHONPATH="$ROOT" python3 "$ROOT/scripts/export_keys.py" "$CSV_DIR" --output "$ROOT/examples/keys_303.json"
PYTHONPATH="$ROOT" python3 "$ROOT/scripts/export_fields.py" "$CSV_DIR" --output "$ROOT/examples/fields_303.json"
PYTHONPATH="$ROOT" python3 "$ROOT/scripts/merge_data.py" \
  "$ROOT/examples/amounts_303.json" \
  "$ROOT/examples/keys_303.json" \
  "$ROOT/examples/data_303.json"
PYTHONPATH="$ROOT" python3 "$ROOT/scripts/render_report.py" \
  "$CSV_DIR" \
  --data-json "$ROOT/examples/data_303.json" \
  --output "$ROOT/examples/output_303.txt"
