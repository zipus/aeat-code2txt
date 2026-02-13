#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
XLSX="${1:-$ROOT/data/DR303e26v101.xlsx}"
CSV_DIR="$ROOT/csv_x2c_303"
XLSX_390="${2:-$ROOT/data/dr390e2025.xlsx}"
CSV_DIR_390="$ROOT/csv_x2c_390"

if [[ ! -f "$XLSX" ]]; then
  echo "XLSX not found: $XLSX"
  exit 1
fi

PYTHONPATH="$ROOT" python3 "$ROOT/scripts/xlsx_to_csv.py" "$XLSX" "$CSV_DIR"
PYTHONPATH="$ROOT" python3 "$ROOT/scripts/export_keys.py" "$CSV_DIR" --output "$ROOT/examples/keys_303.json"
PYTHONPATH="$ROOT" python3 "$ROOT/scripts/export_fields.py" "$CSV_DIR" --output "$ROOT/examples/fields_303.json"
PYTHONPATH="$ROOT" python3 "$ROOT/scripts/export_layout_json.py" "$CSV_DIR" "$ROOT/aeat_code2txt/layouts/layouts_303.json"
PYTHONPATH="$ROOT" python3 "$ROOT/scripts/merge_data.py" \
  "$ROOT/examples/amounts_303.json" \
  "$ROOT/examples/keys_303.json" \
  "$ROOT/examples/data_303.json"
PYTHONPATH="$ROOT" python3 "$ROOT/scripts/render_report.py" \
  "$CSV_DIR" \
  --data-json "$ROOT/examples/data_303.json" \
  --output "$ROOT/examples/output_303.txt"

if [[ -f "$XLSX_390" ]]; then
  PYTHONPATH="$ROOT" python3 "$ROOT/scripts/xlsx_to_csv.py" "$XLSX_390" "$CSV_DIR_390"
  PYTHONPATH="$ROOT" python3 "$ROOT/scripts/export_layout_json.py" "$CSV_DIR_390" "$ROOT/aeat_code2txt/layouts/layouts_390.json"
fi
