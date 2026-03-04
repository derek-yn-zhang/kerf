import pytest

from kerf.builtins import (
    always_true,
    count_tokens,
    extract_json,
    has_html,
    has_long_input,
    lowercase,
    normalize_text,
    regex_replace,
    route_by_length,
    strip_html,
    truncate,
    uppercase,
)


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
        assert route_by_length("short", params) == "quick"


class TestStripHtml:
    def test_strips_tags(self):
        assert strip_html("<p>hello <b>world</b></p>", {}) == "hello world"

    def test_plain_text_unchanged(self):
        assert strip_html("no tags here", {}) == "no tags here"

    def test_self_closing_tags(self):
        assert strip_html("before<br/>after", {}) == "beforeafter"

    def test_nested_tags(self):
        assert strip_html("<div><span>text</span></div>", {}) == "text"

    def test_empty_string(self):
        assert strip_html("", {}) == ""

    def test_entities_preserved(self):
        assert strip_html("<p>a &amp; b</p>", {}) == "a & b"


class TestExtractJson:
    def test_json_object_in_text(self):
        result = extract_json('Here is the result: {"key": "value"} done', {})
        assert result == {"key": "value"}

    def test_json_array_in_text(self):
        result = extract_json("data: [1, 2, 3] end", {})
        assert result == [1, 2, 3]

    def test_bare_json(self):
        result = extract_json('{"a": 1}', {})
        assert result == {"a": 1}

    def test_nested_json(self):
        result = extract_json('prefix {"outer": {"inner": true}} suffix', {})
        assert result == {"outer": {"inner": True}}

    def test_no_json_raises(self):
        with pytest.raises(ValueError, match="No JSON"):
            extract_json("just plain text", {})

    def test_first_json_wins(self):
        result = extract_json('{"a": 1} {"b": 2}', {})
        assert result == {"a": 1}


class TestTruncate:
    def test_under_limit(self):
        assert truncate("short", {}) == "short"

    def test_over_limit(self):
        assert truncate("abcdefghij", {"max_length": 5}) == "abcde"

    def test_exact_limit(self):
        assert truncate("abc", {"max_length": 3}) == "abc"

    def test_default_limit(self):
        text = "x" * 1500
        assert len(truncate(text, {})) == 1000

    def test_empty_string(self):
        assert truncate("", {"max_length": 10}) == ""


class TestCountTokens:
    def test_basic_count(self):
        result = count_tokens("one two three four", {})
        assert result["token_count"] == int(4 / 0.75)
        assert result["text"] == "one two three four"

    def test_empty_string(self):
        result = count_tokens("", {})
        assert result["token_count"] == 0
        assert result["text"] == ""

    def test_single_word(self):
        result = count_tokens("hello", {})
        assert result["token_count"] == int(1 / 0.75)


class TestRegexReplace:
    def test_basic_substitution(self):
        assert regex_replace("hello world", {"pattern": "world", "replacement": "earth"}) == "hello earth"

    def test_case_insensitive(self):
        assert regex_replace("Hello HELLO", {"pattern": "hello", "replacement": "hi", "flags": "i"}) == "hi hi"

    def test_deletion(self):
        assert regex_replace("remove [this] please", {"pattern": r"\[.*?\]"}) == "remove  please"

    def test_missing_pattern_raises(self):
        with pytest.raises(KeyError):
            regex_replace("text", {})

    def test_regex_groups(self):
        result = regex_replace("2025-01-15", {"pattern": r"(\d{4})-(\d{2})-(\d{2})", "replacement": r"\2/\3/\1"})
        assert result == "01/15/2025"


class TestLowercase:
    def test_basic(self):
        assert lowercase("HELLO World", {}) == "hello world"

    def test_already_lower(self):
        assert lowercase("hello", {}) == "hello"

    def test_empty(self):
        assert lowercase("", {}) == ""


class TestUppercase:
    def test_basic(self):
        assert uppercase("hello World", {}) == "HELLO WORLD"

    def test_already_upper(self):
        assert uppercase("HELLO", {}) == "HELLO"

    def test_empty(self):
        assert uppercase("", {}) == ""


class TestAlwaysTrue:
    def test_returns_true(self):
        assert always_true({}) is True

    def test_ignores_context(self):
        assert always_true({"anything": "here"}) is True


class TestHasLongInput:
    def test_short_input(self):
        assert has_long_input({"last_output": "short"}) is False

    def test_long_input(self):
        assert has_long_input({"last_output": "x" * 501}) is True

    def test_exactly_500(self):
        assert has_long_input({"last_output": "x" * 500}) is False

    def test_empty_context(self):
        assert has_long_input({}) is False

    def test_non_string_output(self):
        assert has_long_input({"last_output": {"key": "value"}}) is False

    def test_custom_threshold(self):
        assert has_long_input({"last_output": "x" * 100, "long_input_threshold": 50}) is True


class TestHasHtml:
    def test_has_tags(self):
        assert has_html({"last_output": "<p>hello</p>"}) is True

    def test_no_tags(self):
        assert has_html({"last_output": "just text"}) is False

    def test_empty(self):
        assert has_html({"last_output": ""}) is False

    def test_self_closing(self):
        assert has_html({"last_output": "line<br/>break"}) is True

    def test_angle_brackets_not_html(self):
        assert has_html({"last_output": "5 < 10 > 3"}) is False

    def test_non_string(self):
        assert has_html({"last_output": 42}) is False

    def test_empty_context(self):
        assert has_html({}) is False
