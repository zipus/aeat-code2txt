"""AEAT report rendering from XLSX/CSV layout definitions."""

from .parser import parse_layout_directory, parse_layout_file
from .layout_loader import load_layout, load_layout_json
from .reverse import parse_report, validate_report
from .renderer import (
    PostRecordHook,
    PreRecordHook,
    RenderContext,
    ValueHook,
    render_record,
    render_report,
    validate_data,
)

__all__ = [
    "parse_layout_directory",
    "parse_layout_file",
    "load_layout_json",
    "load_layout",
    "parse_report",
    "validate_report",
    "PostRecordHook",
    "PreRecordHook",
    "RenderContext",
    "ValueHook",
    "render_record",
    "render_report",
    "validate_data",
]
