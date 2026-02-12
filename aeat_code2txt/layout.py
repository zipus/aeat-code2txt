from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class Field:
    number: int
    position: int
    length: int
    raw_type: str
    description: str
    validation: str
    content: str
    code: str | None = None
    formula: str | None = None
    decimals: int | None = None
    const_value: str | None = None
    key: str | None = None


@dataclass(frozen=True)
class RecordLayout:
    name: str
    fields: Sequence[Field]

    def length(self) -> int:
        if not self.fields:
            return 0
        return max(field.position + field.length - 1 for field in self.fields)

    def field_by_code(self) -> Mapping[str, Field]:
        return {field.code: field for field in self.fields if field.code}

    def field_by_key(self) -> Mapping[str, Field]:
        return {field.key: field for field in self.fields if field.key}


@dataclass(frozen=True)
class ReportLayout:
    name: str
    records: Sequence[RecordLayout] = field(default_factory=tuple)

    def record_by_name(self) -> Mapping[str, RecordLayout]:
        return {record.name: record for record in self.records}
