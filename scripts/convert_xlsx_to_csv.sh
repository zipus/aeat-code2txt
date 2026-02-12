#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <xlsx_path> <output_dir>"
  exit 1
fi

python3 "$(dirname "$0")/xlsx_to_csv.py" "$1" "$2"
