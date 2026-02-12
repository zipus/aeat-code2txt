#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("amounts_json", type=Path, help="JSON with code -> amount")
    parser.add_argument("keys_json", type=Path, help="JSON with non-code keys")
    parser.add_argument("output_json", type=Path, help="Merged output JSON")
    args = parser.parse_args()

    amounts = json.loads(args.amounts_json.read_text(encoding="utf-8"))
    keys = json.loads(args.keys_json.read_text(encoding="utf-8"))

    merged = dict(keys)
    merged.update(amounts)

    args.output_json.write_text(
        json.dumps(merged, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
