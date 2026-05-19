"""DSL parser for logslice query expressions."""

import re
from dataclasses import dataclass
from typing import Any, Optional


SUPPORTED_OPS = ("=", "!=", ">", ">=", "<", "<=", "~")


@dataclass
class Filter:
    """Represents a single filter condition parsed from the DSL."""

    field: str
    op: str
    value: Any

    def __repr__(self) -> str:
        return f"Filter({self.field!r} {self.op} {self.value!r})"


class ParseError(Exception):
    """Raised when a query expression cannot be parsed."""


# Matches: field_name OP value
# value can be a quoted string, number, or bare word
_TOKEN_RE = re.compile(
    r'^(?P<field>[\w\.]+)'
    r'\s*(?P<op>!=|>=|<=|=|>|<|~)\s*'
    r'(?P<value>"[^"]*"|\d+(?:\.\d+)?|[\w\.\-]+)$'
)


def _coerce_value(raw: str) -> Any:
    """Convert a raw string token to an appropriate Python type."""
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1]
    try:
        if '.' in raw:
            return float(raw)
        return int(raw)
    except ValueError:
        return raw


def parse_query(query: str) -> list[Filter]:
    """Parse a whitespace-separated query string into a list of Filter objects.

    Each clause must follow the pattern: ``field OP value``
    Multiple clauses are implicitly ANDed together.

    Supported operators: =  !=  >  >=  <  <=  ~  (~ means regex/contains)

    Examples::

        parse_query('level=error service=auth')
        parse_query('status>=400 method=GET')
        parse_query('message~"timeout"')
    """
    if not query or not query.strip():
        return []

    filters: list[Filter] = []
    # Split on whitespace but keep quoted strings intact
    clauses = _split_clauses(query.strip())

    for clause in clauses:
        match = _TOKEN_RE.match(clause.strip())
        if not match:
            raise ParseError(
                f"Invalid filter clause: {clause!r}. "
                f"Expected format: field OP value (ops: {', '.join(SUPPORTED_OPS)})"
            )
        field = match.group('field')
        op = match.group('op')
        value = _coerce_value(match.group('value'))
        filters.append(Filter(field=field, op=op, value=value))

    return filters


def _split_clauses(query: str) -> list[str]:
    """Split query into clauses, respecting quoted strings."""
    clauses = []
    current = []
    in_quotes = False

    for char in query:
        if char == '"':
            in_quotes = not in_quotes
            current.append(char)
        elif char == ' ' and not in_quotes:
            token = ''.join(current).strip()
            if token:
                clauses.append(token)
            current = []
        else:
            current.append(char)

    tail = ''.join(current).strip()
    if tail:
        clauses.append(tail)

    return clauses
