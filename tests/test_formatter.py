"""Tests for logslice.formatter."""

import pytest
from logslice.formatter import (
    format_entries,
    FormatError,
    FORMAT_JSONL,
    FORMAT_TEXT,
    FORMAT_TABLE,
)


ENTRIES = [
    {"level": "info", "msg": "started", "pid": 1},
    {"level": "error", "msg": "failed", "pid": 2},
]


class TestFormatEntriesJsonl:
    def test_each_entry_is_valid_json_line(self):
        import json
        lines = list(format_entries(ENTRIES, fmt=FORMAT_JSONL))
        assert len(lines) == 2
        assert json.loads(lines[0]) == ENTRIES[0]
        assert json.loads(lines[1]) == ENTRIES[1]

    def test_empty_entries_yields_nothing(self):
        lines = list(format_entries([], fmt=FORMAT_JSONL))
        assert lines == []


class TestFormatEntriesText:
    def test_key_value_pairs_present(self):
        lines = list(format_entries(ENTRIES, fmt=FORMAT_TEXT))
        assert "level=info" in lines[0]
        assert "msg=started" in lines[0]

    def test_field_filtering(self):
        lines = list(format_entries(ENTRIES, fmt=FORMAT_TEXT, fields=["level", "msg"]))
        assert "pid" not in lines[0]
        assert "level=info" in lines[0]

    def test_missing_field_is_skipped(self):
        lines = list(format_entries(ENTRIES, fmt=FORMAT_TEXT, fields=["level", "nonexistent"]))
        assert "nonexistent" not in lines[0]

    def test_empty_entries_yields_nothing(self):
        lines = list(format_entries([], fmt=FORMAT_TEXT))
        assert lines == []


class TestFormatEntriesTable:
    def test_table_has_header_and_separator(self):
        lines = list(format_entries(ENTRIES, fmt=FORMAT_TABLE))
        assert len(lines) >= 4  # header + separator + 2 rows
        assert "level" in lines[0]
        assert "---" in lines[1]

    def test_table_rows_contain_values(self):
        lines = list(format_entries(ENTRIES, fmt=FORMAT_TABLE))
        assert "info" in lines[2]
        assert "error" in lines[3]

    def test_table_with_fields(self):
        lines = list(format_entries(ENTRIES, fmt=FORMAT_TABLE, fields=["level", "msg"]))
        assert "pid" not in lines[0]
        assert "level" in lines[0]

    def test_empty_entries_yields_nothing(self):
        lines = list(format_entries([], fmt=FORMAT_TABLE))
        assert lines == []


class TestFormatEntriesErrors:
    def test_unknown_format_raises(self):
        with pytest.raises(FormatError, match="Unknown format"):
            list(format_entries(ENTRIES, fmt="csv"))
