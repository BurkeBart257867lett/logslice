"""Tests for logslice.reader — NDJSON stream reading utilities."""

import io
import pytest
from logslice.reader import iter_entries, ReaderError


class TestIterEntries:
    def _stream(self, text: str) -> io.StringIO:
        return io.StringIO(text)

    def test_single_valid_entry(self):
        stream = self._stream('{"level": "info", "msg": "ok"}\n')
        entries = list(iter_entries(stream))
        assert entries == [{"level": "info", "msg": "ok"}]

    def test_multiple_entries(self):
        data = '{"a": 1}\n{"a": 2}\n{"a": 3}\n'
        entries = list(iter_entries(self._stream(data)))
        assert len(entries) == 3
        assert entries[1] == {"a": 2}

    def test_blank_lines_are_skipped(self):
        data = '{"x": 1}\n\n\n{"x": 2}\n'
        entries = list(iter_entries(self._stream(data)))
        assert len(entries) == 2

    def test_invalid_json_skipped_by_default(self):
        data = 'not-json\n{"ok": true}\n'
        entries = list(iter_entries(self._stream(data)))
        assert entries == [{"ok": True}]

    def test_invalid_json_raises_when_skip_false(self):
        data = 'bad line\n{"ok": true}\n'
        with pytest.raises(ReaderError, match="Line 1"):
            list(iter_entries(self._stream(data), skip_invalid=False))

    def test_non_object_json_skipped_by_default(self):
        data = '[1, 2, 3]\n{"valid": 1}\n'
        entries = list(iter_entries(self._stream(data)))
        assert entries == [{"valid": 1}]

    def test_non_object_json_raises_when_skip_false(self):
        data = '"just a string"\n'
        with pytest.raises(ReaderError, match="expected a JSON object"):
            list(iter_entries(self._stream(data), skip_invalid=False))

    def test_empty_stream_yields_nothing(self):
        entries = list(iter_entries(self._stream("")))
        assert entries == []

    def test_whitespace_only_stream_yields_nothing(self):
        entries = list(iter_entries(self._stream("   \n  \n")))
        assert entries == []

    def test_trailing_whitespace_on_valid_line(self):
        data = '{"k": "v"}   \n'
        entries = list(iter_entries(self._stream(data)))
        assert entries == [{"k": "v"}]

    def test_nested_json_object(self):
        data = '{"http": {"status": 200, "method": "GET"}}\n'
        entries = list(iter_entries(self._stream(data)))
        assert entries[0]["http"]["status"] == 200
