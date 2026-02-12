from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path
from typing import Iterable

from .layout import Field, RecordLayout, ReportLayout

CODE_RE = re.compile(r"\[(\d+)\]")
FORMULA_RE = re.compile(r"\(([^)]*\[\d+\][^)]*)\)")
CONST_RE = re.compile(r"\"([^\"]*)\"")
DECIMALS_RE = re.compile(r"(\d+)\s*decimales", re.IGNORECASE)


def parse_layout_directory(csv_dir: Path) -> ReportLayout:
    records: list[RecordLayout] = []
    for path in sorted(csv_dir.glob("*.csv")):
        records.append(parse_layout_file(path))
    return ReportLayout(name=csv_dir.name, records=records)


def parse_layout_file(csv_path: Path) -> RecordLayout:
    rows = _read_csv(csv_path)
    header_idx, col_map = _find_header(rows)
    if header_idx is None:
        raise ValueError(f"Header row not found in {csv_path}")

    fields: list[Field] = []
    for row in rows[header_idx + 1 :]:
        number = _to_int(row, col_map.get("Nº"))
        if number is None:
            continue
        position = _to_int(row, col_map.get("Posic."))
        length = _to_int(row, col_map.get("Lon"))
        if position is None or length is None:
            continue
        raw_type = _cell(row, col_map.get("Tipo"))
        description = _cell(row, col_map.get("Descripción"))
        validation = _cell(row, col_map.get("Validación"))
        content = _cell(row, col_map.get("Contenido"))

        codes = CODE_RE.findall(description)
        code = codes[-1] if codes else None
        formula = _extract_formula(description)
        decimals = _extract_decimals(content, description)
        const_value = _extract_const(content, description)
        key = _make_key(code, description)

        fields.append(
            Field(
                number=number,
                position=position,
                length=length,
                raw_type=raw_type,
                description=description,
                validation=validation,
                content=content,
                code=code,
                formula=formula,
                decimals=decimals,
                const_value=const_value,
                key=key,
            )
        )

    return RecordLayout(name=csv_path.stem, fields=fields)


def _read_csv(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8") as f:
        return [row for row in csv.reader(f)]


def _find_header(rows: Iterable[list[str]]):
    for idx, row in enumerate(rows):
        if _row_has_header(row):
            return idx, _column_map(row)
    return None, {}


def _row_has_header(row: list[str]) -> bool:
    normalized = [_norm(cell) for cell in row if cell]
    required = {"no", "posic", "lon", "tipo", "descripcion"}
    return required.issubset(set(normalized))


def _column_map(row: list[str]) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for idx, cell in enumerate(row):
        key = _norm(cell)
        if key == "no":
            mapping["Nº"] = idx
        elif key == "posic":
            mapping["Posic."] = idx
        elif key == "lon":
            mapping["Lon"] = idx
        elif key == "tipo":
            mapping["Tipo"] = idx
        elif key == "descripcion":
            mapping["Descripción"] = idx
        elif key == "validacion":
            mapping["Validación"] = idx
        elif key == "contenido":
            mapping["Contenido"] = idx
    return mapping


def _norm(value: str) -> str:
    if not value:
        return ""
    value = value.strip().lower()
    value = unicodedata.normalize("NFD", value)
    value = "".join(ch for ch in value if unicodedata.category(ch) != "Mn")
    value = value.replace("º", "o")
    value = value.replace(".", "")
    return value


def _cell(row: list[str], idx: int | None) -> str:
    if idx is None or idx >= len(row):
        return ""
    return (row[idx] or "").strip()


def _to_int(row: list[str], idx: int | None) -> int | None:
    if idx is None or idx >= len(row):
        return None
    value = (row[idx] or "").strip()
    if not value.isdigit():
        return None
    return int(value)


def _extract_const(content: str, description: str) -> str | None:
    if not content:
        return None
    if "Constante" in content:
        match = CONST_RE.search(content)
        if match:
            return match.group(1)
    if "Constante" in description:
        match = CONST_RE.search(content)
        if match:
            return match.group(1)
    if "En blanco" in content:
        return ""
    if content.startswith("\"") and content.endswith("\"") and "..." not in content:
        return content.strip("\"")
    return None


def _extract_decimals(content: str, description: str) -> int | None:
    for text in (content, description):
        match = DECIMALS_RE.search(text or "")
        if match:
            return int(match.group(1))
    if "%" in description:
        return 2
    return None


def _extract_formula(description: str) -> str | None:
    match = FORMULA_RE.search(description)
    if match:
        return match.group(1).strip()
    return None


def _make_key(code: str | None, description: str) -> str:
    if code:
        return code
    base = description.strip().lower()
    base = unicodedata.normalize("NFD", base)
    base = "".join(ch for ch in base if unicodedata.category(ch) != "Mn")
    base = re.sub(r"\[[^\]]+\]", "", base)
    base = re.sub(r"[^a-z0-9]+", "_", base)
    base = base.strip("_")
    return base or "field"
