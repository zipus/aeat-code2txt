from __future__ import annotations

from dataclasses import dataclass
import re
from decimal import Decimal
from typing import Callable, Mapping

from .formulas import evaluate_formula
from .layout import Field, RecordLayout, ReportLayout


@dataclass
class RenderContext:
    amounts: Mapping[str, Decimal]
    values: Mapping[str, str]
    overrides: Mapping[str, str]


PreRecordHook = Callable[[RecordLayout, RenderContext], None]
ValueHook = Callable[[Field, str, RenderContext], str]
PostRecordHook = Callable[[RecordLayout, str, RenderContext], str]

CODE_KEY_RE = re.compile(r"^\d+$")


def render_report(
    report: ReportLayout,
    *,
    amounts: Mapping[str, Decimal] | None = None,
    values: Mapping[str, str] | None = None,
    overrides: Mapping[str, str] | None = None,
    data: Mapping[str, str | int | float | Decimal] | None = None,
    pre_record_hooks: list[PreRecordHook] | None = None,
    value_hooks: list[ValueHook] | None = None,
    post_record_hooks: list[PostRecordHook] | None = None,
) -> str:
    amounts, values = _split_inputs(amounts, values, data)
    records = []
    for record in report.records:
        records.append(
            render_record(
                record,
                amounts=amounts,
                values=values,
                overrides=overrides,
                pre_record_hooks=pre_record_hooks,
                value_hooks=value_hooks,
                post_record_hooks=post_record_hooks,
            )
        )
    return "\r\n".join(records)


def render_record(
    record: RecordLayout,
    *,
    amounts: Mapping[str, Decimal] | None = None,
    values: Mapping[str, str] | None = None,
    overrides: Mapping[str, str] | None = None,
    data: Mapping[str, str | int | float | Decimal] | None = None,
    pre_record_hooks: list[PreRecordHook] | None = None,
    value_hooks: list[ValueHook] | None = None,
    post_record_hooks: list[PostRecordHook] | None = None,
) -> str:
    amounts, values = _split_inputs(amounts, values, data)
    values = values or {}
    overrides = overrides or {}
    context = RenderContext(amounts=amounts, values=values, overrides=overrides)

    if pre_record_hooks:
        for hook in pre_record_hooks:
            hook(record, context)

    computed = _compute_values(record, amounts)
    length = record.length()
    buffer = [" "] * length

    for field in record.fields:
        raw = _resolve_field_value(field, amounts, values, overrides, computed)
        if value_hooks:
            for hook in value_hooks:
                raw = hook(field, raw, context)
        formatted = _format_field(field, raw)
        _write(buffer, field.position, field.length, formatted)

    text = "".join(buffer)
    if post_record_hooks:
        for hook in post_record_hooks:
            text = hook(record, text, context)
    return text


def _split_inputs(
    amounts: Mapping[str, Decimal] | None,
    values: Mapping[str, str] | None,
    data: Mapping[str, str | int | float | Decimal] | None,
) -> tuple[Mapping[str, Decimal], Mapping[str, str]]:
    if data is None:
        return amounts or {}, values or {}
    if amounts or values:
        raise ValueError("Provide either data or amounts/values, not both.")
    amt: dict[str, Decimal] = {}
    vals: dict[str, str] = {}
    for key, value in data.items():
        if CODE_KEY_RE.match(str(key)):
            amt[str(key)] = Decimal(str(value))
        else:
            vals[str(key)] = str(value)
    return amt, vals


def _compute_values(record: RecordLayout, amounts: Mapping[str, Decimal]) -> dict[str, Decimal]:
    computed: dict[str, Decimal] = {}

    def compute(field: Field) -> Decimal:
        if field.code in computed:
            return computed[field.code]
        if not field.formula:
            return amounts.get(field.code, Decimal(0))
        values = {**amounts, **computed}
        result = evaluate_formula(field.formula, values)
        computed[field.code] = result
        return result

    for field in record.fields:
        if field.code and field.formula:
            compute(field)
    return computed


def _resolve_field_value(
    field: Field,
    amounts: Mapping[str, Decimal],
    values: Mapping[str, str],
    overrides: Mapping[str, str],
    computed: Mapping[str, Decimal],
) -> str:
    if field.key in overrides:
        return str(overrides[field.key])
    if field.code and field.code in overrides:
        return str(overrides[field.code])
    if field.const_value is not None:
        return field.const_value
    if field.code:
        if field.code in computed:
            return str(computed[field.code])
        if field.code in amounts:
            return str(amounts[field.code])
    if field.key in values:
        return str(values[field.key])
    return ""


def _format_field(field: Field, raw: str) -> str:
    if raw is None:
        raw = ""
    if field.const_value is not None:
        return _format_text(str(raw), field.length)
    if field.raw_type.strip().startswith("A"):
        return _format_text(str(raw), field.length)
    if field.raw_type.strip().startswith("An"):
        return _format_text(str(raw), field.length)

    decimals = field.decimals if field.decimals is not None else 0
    return _format_number(raw, field.length, decimals, field.raw_type)


def _format_text(value: str, length: int) -> str:
    if len(value) > length:
        return value[:length]
    return value.ljust(length)


def _format_number(value: str, length: int, decimals: int, raw_type: str) -> str:
    num = Decimal(str(value or "0"))
    sign = ""
    if num < 0:
        if raw_type.strip() == "N":
            sign = "N"
        else:
            raise ValueError(f"Negative value not allowed for type {raw_type}")
    num = abs(num)
    text = f"{num:.{decimals}f}".replace(".", "")
    text = text.rjust(length - len(sign), "0")
    return f"{sign}{text}"


def _write(buffer: list[str], position: int, length: int, value: str) -> None:
    start = position - 1
    end = start + length
    if len(value) != length:
        raise ValueError(f"Field length mismatch at pos {position}: {len(value)} != {length}")
    buffer[start:end] = list(value)
