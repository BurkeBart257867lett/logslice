"""Log file reading and NDJSON (newline-delimited JSON) parsing utilities."""

import json
import sys
from typing import Any, Dict, Generator, IO, Optional


class ReaderError(Exception):
    """Raised when a log line cannot be parsed."""
    pass


def iter_entries(
    stream: IO[str],
    skip_invalid: bool = True,
) -> Generator[Dict[str, Any], None, None]:
    """Yield parsed JSON objects from a newline-delimited JSON stream.

    Args:
        stream: A file-like object with text lines.
        skip_invalid: If True, silently skip lines that are not valid JSON
                      objects. If False, raise ReaderError on bad lines.
    """
    for lineno, raw_line in enumerate(stream, start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            if skip_invalid:
                continue
            raise ReaderError(
                f"Line {lineno}: invalid JSON — {exc.msg}"
            ) from exc

        if not isinstance(entry, dict):
            if skip_invalid:
                continue
            raise ReaderError(
                f"Line {lineno}: expected a JSON object, got {type(entry).__name__}"
            )

        yield entry


def read_file(
    path: Optional[str],
    skip_invalid: bool = True,
) -> Generator[Dict[str, Any], None, None]:
    """Open a log file (or stdin if path is None/'-') and yield entries."""
    if path is None or path == "-":
        yield from iter_entries(sys.stdin, skip_invalid=skip_invalid)
    else:
        with open(path, "r", encoding="utf-8") as fh:
            yield from iter_entries(fh, skip_invalid=skip_invalid)
