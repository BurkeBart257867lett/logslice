"""Tests for logslice.matcher — filter matching against log entries."""

import pytest
from logslice.parser import Filter
from logslice.matcher import match_filter, match_all, filter_entries, MatchError


ENTRY = {"level": "error", "status": 500, "service": "api", "latency": 120}
NESTED_ENTRY = {"http": {"method": "GET", "status": 200}, "level": "info"}


class TestMatchFilter:
    def test_equality_match(self):
        assert match_filter(ENTRY, Filter("level", "=", "error")) is True

    def test_equality_no_match(self):
        assert match_filter(ENTRY, Filter("level", "=", "info")) is False

    def test_not_equal_match(self):
        assert match_filter(ENTRY, Filter("level", "!=", "info")) is True

    def test_not_equal_no_match(self):
        assert match_filter(ENTRY, Filter("level", "!=", "error")) is False

    def test_greater_than_match(self):
        assert match_filter(ENTRY, Filter("status", ">", 400)) is True

    def test_greater_than_no_match(self):
        assert match_filter(ENTRY, Filter("status", ">", 500)) is False

    def test_greater_than_or_equal_match(self):
        assert match_filter(ENTRY, Filter("status", ">=", 500)) is True

    def test_less_than_match(self):
        assert match_filter(ENTRY, Filter("latency", "<", 200)) is True

    def test_less_than_or_equal_match(self):
        assert match_filter(ENTRY, Filter("latency", "<=", 120)) is True

    def test_contains_match(self):
        assert match_filter(ENTRY, Filter("service", "~", "api")) is True

    def test_contains_case_insensitive(self):
        assert match_filter(ENTRY, Filter("level", "~", "ERR")) is True

    def test_contains_no_match(self):
        assert match_filter(ENTRY, Filter("service", "~", "db")) is False

    def test_missing_field_returns_false_for_gt(self):
        assert match_filter(ENTRY, Filter("missing", ">", 0)) is False

    def test_missing_field_equality_returns_false(self):
        assert match_filter(ENTRY, Filter("missing", "=", "x")) is False

    def test_nested_field_match(self):
        assert match_filter(NESTED_ENTRY, Filter("http.status", "=", 200)) is True

    def test_nested_field_no_match(self):
        assert match_filter(NESTED_ENTRY, Filter("http.method", "=", "POST")) is False

    def test_unsupported_operator_raises(self):
        with pytest.raises(MatchError):
            match_filter(ENTRY, Filter("level", "^", "err"))


class TestMatchAll:
    def test_all_filters_pass(self):
        filters = [Filter("level", "=", "error"), Filter("status", ">", 400)]
        assert match_all(ENTRY, filters) is True

    def test_one_filter_fails(self):
        filters = [Filter("level", "=", "error"), Filter("status", "<", 400)]
        assert match_all(ENTRY, filters) is False

    def test_empty_filters_always_true(self):
        assert match_all(ENTRY, []) is True


class TestFilterEntries:
    ENTRIES = [
        {"level": "info", "status": 200},
        {"level": "error", "status": 500},
        {"level": "warn", "status": 404},
    ]

    def test_no_filters_returns_all(self):
        assert filter_entries(self.ENTRIES, []) == self.ENTRIES

    def test_single_filter(self):
        result = filter_entries(self.ENTRIES, [Filter("level", "=", "error")])
        assert result == [{"level": "error", "status": 500}]

    def test_multiple_filters(self):
        filters = [Filter("status", ">=", 400), Filter("level", "!=", "warn")]
        result = filter_entries(self.ENTRIES, filters)
        assert result == [{"level": "error", "status": 500}]

    def test_no_matches_returns_empty(self):
        result = filter_entries(self.ENTRIES, [Filter("level", "=", "debug")])
        assert result == []
