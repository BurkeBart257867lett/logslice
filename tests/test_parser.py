"""Tests for logslice.parser — DSL query parsing."""

import pytest
from logslice.parser import Filter, ParseError, parse_query


class TestParseQueryBasic:
    def test_empty_string_returns_empty_list(self):
        assert parse_query("") == []

    def test_whitespace_only_returns_empty_list(self):
        assert parse_query("   ") == []

    def test_single_equality_filter(self):
        result = parse_query("level=error")
        assert result == [Filter(field="level", op="=", value="error")]

    def test_single_not_equal_filter(self):
        result = parse_query("level!=debug")
        assert result == [Filter(field="level", op="!=", value="debug")]

    def test_numeric_value_coerced_to_int(self):
        result = parse_query("status=200")
        assert result[0].value == 200
        assert isinstance(result[0].value, int)

    def test_float_value_coerced(self):
        result = parse_query("latency>=1.5")
        assert result[0].value == 1.5
        assert isinstance(result[0].value, float)

    def test_quoted_string_value(self):
        result = parse_query('message~"connection timeout"')
        assert result[0].value == "connection timeout"
        assert result[0].op == "~"


class TestParseQueryMultipleClauses:
    def test_two_filters(self):
        result = parse_query("level=error service=auth")
        assert len(result) == 2
        assert result[0] == Filter("level", "=", "error")
        assert result[1] == Filter("service", "=", "auth")

    def test_three_filters_mixed_ops(self):
        result = parse_query("status>=400 method=GET service!=payments")
        assert len(result) == 3
        assert result[0] == Filter("status", ">=", 400)
        assert result[1] == Filter("method", "=", "GET")
        assert result[2] == Filter("service", "!=", "payments")

    def test_dotted_field_name(self):
        result = parse_query("http.status=404")
        assert result[0].field == "http.status"


class TestParseQueryErrors:
    def test_invalid_clause_raises_parse_error(self):
        with pytest.raises(ParseError, match="Invalid filter clause"):
            parse_query("justabareword")

    def test_unknown_operator_raises_parse_error(self):
        with pytest.raises(ParseError):
            parse_query("level@error")

    def test_missing_value_raises_parse_error(self):
        with pytest.raises(ParseError):
            parse_query("level=")


class TestFilterRepr:
    def test_repr_format(self):
        f = Filter(field="level", op="=", value="error")
        assert repr(f) == "Filter('level' = 'error')"
