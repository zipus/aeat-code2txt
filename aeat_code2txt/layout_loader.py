from __future__ import annotations

import json
from pathlib import Path
from importlib import resources

from .layout import Field, RecordLayout, ReportLayout


def load_layout_json(path: Path) -> ReportLayout:
    data = json.loads(path.read_text(encoding="utf-8"))
    records = []
    for rec in data.get("records", []):
        fields = [
            Field(
                number=field["number"],
                position=field["position"],
                length=field["length"],
                raw_type=field["raw_type"],
                description=field["description"],
                validation=field.get("validation", ""),
                content=field.get("content", ""),
                code=field.get("code"),
                formula=field.get("formula"),
                decimals=field.get("decimals"),
                const_value=field.get("const_value"),
                key=field.get("key"),
            )
            for field in rec.get("fields", [])
        ]
        records.append(RecordLayout(name=rec["name"], fields=fields))
    return ReportLayout(name=data.get("name", path.stem), records=records)


def load_layout(model: str) -> ReportLayout:
    """
    Load a bundled layout by model code (e.g., "303", "390").
    """
    name = f"layouts_{model}.json"
    with resources.files("aeat_code2txt.layouts").joinpath(name).open("r", encoding="utf-8") as f:
        data = json.load(f)
    records = []
    for rec in data.get("records", []):
        fields = [
            Field(
                number=field["number"],
                position=field["position"],
                length=field["length"],
                raw_type=field["raw_type"],
                description=field["description"],
                validation=field.get("validation", ""),
                content=field.get("content", ""),
                code=field.get("code"),
                formula=field.get("formula"),
                decimals=field.get("decimals"),
                const_value=field.get("const_value"),
                key=field.get("key"),
            )
            for field in rec.get("fields", [])
        ]
        records.append(RecordLayout(name=rec["name"], fields=fields))
    return ReportLayout(name=data.get("name", model), records=records)
