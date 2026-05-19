"""Command-line interface for logslice."""

import argparse
import sys
from typing import List, Optional

from logslice.formatter import format_entries, VALID_FORMATS, FORMAT_JSONL, FormatError
from logslice.matcher import filter_entries, MatchError
from logslice.parser import parse_query, ParseError
from logslice.reader import read_file, iter_entries, ReaderError


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="logslice",
        description="Filter and aggregate structured JSON logs using a simple DSL.",
    )
    p.add_argument("file", nargs="?", default="-", help="Log file to read (default: stdin)")
    p.add_argument("-q", "--query", default="", metavar="QUERY", help="Filter query, e.g. 'level=error status>=400'")
    p.add_argument("-f", "--format", default=FORMAT_JSONL, choices=VALID_FORMATS, help="Output format")
    p.add_argument("--fields", default=None, metavar="FIELDS", help="Comma-separated list of fields to include")
    p.add_argument("--limit", type=int, default=None, metavar="N", help="Maximum number of results to output")
    return p


def run(argv: Optional[List[str]] = None) -> int:
    """Entry point for the CLI. Returns an exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    fields = [f.strip() for f in args.fields.split(",")] if args.fields else None

    try:
        filters = parse_query(args.query)
    except ParseError as exc:
        print(f"logslice: query error: {exc}", file=sys.stderr)
        return 2

    try:
        if args.file == "-":
            entries = iter_entries(sys.stdin)
        else:
            entries = read_file(args.file)
    except ReaderError as exc:
        print(f"logslice: read error: {exc}", file=sys.stderr)
        return 1

    try:
        matched = filter_entries(entries, filters)
        if args.limit is not None:
            import itertools
            matched = itertools.islice(matched, args.limit)
        for line in format_entries(matched, fmt=args.format, fields=fields):
            print(line)
    except (MatchError, FormatError) as exc:
        print(f"logslice: error: {exc}", file=sys.stderr)
        return 1

    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
