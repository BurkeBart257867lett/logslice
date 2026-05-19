"""Filter matching logic for structured log entries."""

from typing import Any, Dict, List
from logslice.parser import Filter


class MatchError(Exception):
    """Raised when a log entry cannot be matched due to invalid structure."""
    pass


def _get_nested(entry: Dict[str, Any], field: str) -> Any:
    """Resolve a potentially dot-notated field path from a log entry dict."""
    parts = field.split(".")
    current = entry
    for part in parts:
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def match_filter(entry: Dict[str, Any], f: Filter) -> bool:
    """Return True if the log entry satisfies the given Filter."""
    value = _get_nested(entry, f.field)

    if f.operator == "=":
        return value == f.value
    elif f.operator == "!=":
        return value != f.value
    elif f.operator == ">":
        if value is None:
            return False
        return value > f.value
    elif f.operator == ">=":
        if value is None:
            return False
        return value >= f.value
    elif f.operator == "<":
        if value is None:
            return False
        return value < f.value
    elif f.operator == "<=":
        if value is None:
            return False
        return value <= f.value
    elif f.operator == "~":
        if value is None:
            return False
        return str(f.value).lower() in str(value).lower()
    else:
        raise MatchError(f"Unsupported operator: {f.operator}")


def match_all(entry: Dict[str, Any], filters: List[Filter]) -> bool:
    """Return True if the log entry satisfies ALL filters (AND semantics)."""
    return all(match_filter(entry, f) for f in filters)


def filter_entries(
    entries: List[Dict[str, Any]], filters: List[Filter]
) -> List[Dict[str, Any]]:
    """Return only the entries that match all given filters."""
    if not filters:
        return list(entries)
    return [e for e in entries if match_all(e, filters)]
