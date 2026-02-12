#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from decimal import Decimal
from pathlib import Path

from aeat_code2txt import parse_layout_directory, render_report


def _load_amounts(path: Path) -> dict[str, Decimal]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {str(k): Decimal(str(v)) for k, v in data.items()}


def _load_values(path: Path | None) -> dict[str, str]:
    if not path:
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {str(k): str(v) for k, v in data.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("layout_dir", type=Path, help="Directory with CSV sheets")
    parser.add_argument("--amounts-json", type=Path, help="JSON with code -> amount")
    parser.add_argument("--values-json", type=Path, help="JSON with extra values")
    parser.add_argument("--data-json", type=Path, help="Single JSON for codes + values")
    parser.add_argument("--output", type=Path, help="Output file path")
    args = parser.parse_args()

    layout = parse_layout_directory(args.layout_dir)
    if args.data_json:
        data = json.loads(args.data_json.read_text(encoding="utf-8"))
        text = render_report(layout, data=data)
    else:
        if not args.amounts_json:
            raise SystemExit("--amounts-json is required unless --data-json is provided")
        amounts = _load_amounts(args.amounts_json)
        values = _load_values(args.values_json)
        text = render_report(layout, amounts=amounts, values=values)

    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
