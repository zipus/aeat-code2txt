#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from aeat_code2txt import parse_layout_directory


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("layout_dir", type=Path, help="Directory with CSV sheets")
    parser.add_argument("--output", type=Path, help="Output JSON file")
    args = parser.parse_args()

    layout = parse_layout_directory(args.layout_dir)
    keys = {}
    for record in layout.records:
        for field in record.fields:
            if field.code:
                continue
            keys[field.key] = ""

    payload = dict(sorted(keys.items()))
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
