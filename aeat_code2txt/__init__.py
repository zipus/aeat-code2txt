"""AEAT report rendering from XLSX/CSV layout definitions."""

from .parser import parse_layout_directory, parse_layout_file
from .reverse import parse_report, validate_report
from .renderer import (
    PostRecordHook,
    PreRecordHook,
    RenderContext,
    ValueHook,
    render_record,
    render_report,
)

__all__ = [
    "parse_layout_directory",
    "parse_layout_file",
    "parse_report",
    "validate_report",
    "PostRecordHook",
    "PreRecordHook",
    "RenderContext",
    "ValueHook",
    "render_record",
    "render_report",
]
