#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from aeat_code2txt import parse_layout_directory


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_dir", type=Path, help="Directory with CSV sheets")
    parser.add_argument("output_json", type=Path, help="Output JSON layout")
    args = parser.parse_args()

    layout = parse_layout_directory(args.csv_dir)
    payload = {
        "name": layout.name,
        "records": [
            {
                "name": record.name,
                "fields": [
                    {
                        "number": field.number,
                        "position": field.position,
                        "length": field.length,
                        "raw_type": field.raw_type,
                        "description": field.description,
                        "validation": field.validation,
                        "content": field.content,
                        "code": field.code,
                        "formula": field.formula,
                        "decimals": field.decimals,
                        "const_value": field.const_value,
                        "key": field.key,
                    }
                    for field in record.fields
                ],
            }
            for record in layout.records
        ],
    }

    args.output_json.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
