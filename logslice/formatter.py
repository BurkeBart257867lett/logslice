"""Output formatting for logslice query results."""

import json
from typing import Any, Dict, Iterable, List, Optional


FORMAT_JSONL = "jsonl"
FORMAT_TEXT = "text"
FORMAT_TABLE = "table"

VALID_FORMATS = (FORMAT_JSONL, FORMAT_TEXT, FORMAT_TABLE)


class FormatError(Exception):
    """Raised when formatting fails or an invalid format is requested."""


def _format_jsonl(entry: Dict[str, Any]) -> str:
    """Serialize a single entry as a JSON line."""
    return json.dumps(entry, ensure_ascii=False)


def _format_text(entry: Dict[str, Any], fields: Optional[List[str]] = None) -> str:
    """Format an entry as a human-readable key=value line."""
    if fields:
        pairs = [(k, entry[k]) for k in fields if k in entry]
    else:
        pairs = list(entry.items())
    return "  ".join(f"{k}={v}" for k, v in pairs)


def _format_table_row(entry: Dict[str, Any], columns: List[str], widths: List[int]) -> str:
    """Format a single row for table output."""
    cells = [str(entry.get(col, "")).ljust(widths[i]) for i, col in enumerate(columns)]
    return "  ".join(cells)


def format_entries(
    entries: Iterable[Dict[str, Any]],
    fmt: str = FORMAT_JSONL,
    fields: Optional[List[str]] = None,
) -> Iterable[str]:
    """Yield formatted strings for each entry.

    Args:
        entries: Iterable of log entry dicts.
        fmt: One of 'jsonl', 'text', or 'table'.
        fields: Optional list of field names to include (text/table only).

    Raises:
        FormatError: If an unknown format is specified.
    """
    if fmt not in VALID_FORMATS:
        raise FormatError(f"Unknown format {fmt!r}. Choose from: {', '.join(VALID_FORMATS)}")

    if fmt == FORMAT_JSONL:
        for entry in entries:
            yield _format_jsonl(entry)
        return

    if fmt == FORMAT_TEXT:
        for entry in entries:
            yield _format_text(entry, fields)
        return

    if fmt == FORMAT_TABLE:
        rows = list(entries)
        if not rows:
            return
        columns = fields if fields else list(rows[0].keys())
        widths = [max(len(col), max((len(str(r.get(col, ""))) for r in rows), default=0)) for col in columns]
        header = "  ".join(col.ljust(widths[i]) for i, col in enumerate(columns))
        separator = "  ".join("-" * widths[i] for i in range(len(columns)))
        yield header
        yield separator
        for row in rows:
            yield _format_table_row(row, columns, widths)
