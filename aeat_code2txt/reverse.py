from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Mapping

from .formulas import evaluate_formula
from .layout import Field, ReportLayout


@dataclass
class ValidationIssue:
    record: str
    field_number: int
    key: str | None
    code: str | None
    message: str


def parse_report(text: str, report: ReportLayout) -> dict[str, str]:
    """
    Parse a rendered report into a flat dictionary of codes + keys.
    """
    lines = text.splitlines()
    data: dict[str, str] = {}
    for record, line in zip(report.records, lines):
        for field in record.fields:
            raw = _slice(line, field.position, field.length)
            if field.const_value is not None:
                continue
            key = field.code or field.key
            if not key:
                continue
            data[key] = raw.strip()
    return data


def validate_report(text: str, report: ReportLayout) -> list[ValidationIssue]:
    lines = text.splitlines()
    issues: list[ValidationIssue] = []
    values: dict[str, Decimal] = {}

    for record, line in zip(report.records, lines):
        for field in record.fields:
            raw = _slice(line, field.position, field.length)
            if field.const_value is not None:
                if raw != field.const_value.ljust(field.length):
                    issues.append(
                        ValidationIssue(
                            record=record.name,
                            field_number=field.number,
                            key=field.key,
                            code=field.code,
                            message=f"Const mismatch: '{raw}'",
                        )
                    )
                continue
            if field.code and field.raw_type.strip().startswith(("N", "Num")):
                try:
                    values[field.code] = _parse_number(raw, field.decimals)
                except ValueError as exc:
                    issues.append(
                        ValidationIssue(
                            record=record.name,
                            field_number=field.number,
                            key=field.key,
                            code=field.code,
                            message=str(exc),
                        )
                    )

    for record, line in zip(report.records, lines):
        for field in record.fields:
            if field.code and field.formula:
                expected = evaluate_formula(field.formula, values)
                actual = values.get(field.code)
                if actual is None:
                    continue
                if actual != expected:
                    issues.append(
                        ValidationIssue(
                            record=record.name,
                            field_number=field.number,
                            key=field.key,
                            code=field.code,
                            message=f"Formula mismatch: {actual} != {expected}",
                        )
                    )
    return issues


def _slice(line: str, position: int, length: int) -> str:
    start = position - 1
    end = start + length
    return line[start:end]


def _parse_number(raw: str, decimals: int | None) -> Decimal:
    raw = raw.strip()
    if not raw:
        return Decimal(0)
    sign = 1
    if raw.startswith("N"):
        sign = -1
        raw = raw[1:]
    decimals = decimals if decimals is not None else 0
    if decimals:
        value = Decimal(raw[:-decimals] + "." + raw[-decimals:])
    else:
        value = Decimal(raw)
    return value * sign
