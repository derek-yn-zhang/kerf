import pytest

from kerf.builtins import normalize_text, route_by_length


class TestNormalizeText:
    def test_collapses_whitespace(self):
        assert normalize_text("  hello   world  ", {}) == "hello world"

    def test_strips_newlines(self):
        assert normalize_text("line1\n\n  line2\t\tline3", {}) == "line1 line2 line3"

    def test_empty_string(self):
        assert normalize_text("", {}) == ""

    def test_already_clean(self):
        assert normalize_text("hello world", {}) == "hello world"


class TestRouteByLength:
    def test_short_route(self):
        params = {"routes": {"short_text": "quick", "long_text": "full"}, "threshold": 10}
        assert route_by_length("hi", params) == "quick"

    def test_long_route(self):
        params = {"routes": {"short_text": "quick", "long_text": "full"}, "threshold": 5}
        assert route_by_length("this is long enough", params) == "full"

    def test_missing_route_raises(self):
        params = {"routes": {"short_text": "quick"}, "threshold": 5}
        with pytest.raises(ValueError, match="no route for 'long_text'"):
            route_by_length("this is long enough", params)

    def test_default_threshold(self):
        params = {"routes": {"short_text": "quick", "long_text": "full"}}
        # Default threshold is 500
        assert route_by_length("short", params) == "quick"
