import json
import re
from html.parser import HTMLParser
from io import StringIO
from typing import Any, Dict

from kerf.tools import LocalToolManager


# --- Tools ---


def normalize_text(input_data: str, params: Dict[str, Any]) -> str:
    return " ".join(input_data.split())


def route_by_length(input_data: str, params: Dict[str, Any]) -> str:
    """Returns workflow_name based on input length."""
    routes = params.get("routes", {})
    threshold = params.get("threshold", 500)
    key = "short_text" if len(input_data) < threshold else "long_text"
    result = routes.get(key)
    if result is None:
        raise ValueError(
            f"route_by_length: no route for '{key}'. "
            f"Available routes: {list(routes.keys())}"
        )
    return result


class _HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self._result = StringIO()

    def handle_data(self, data):
        self._result.write(data)

    def get_text(self):
        return self._result.getvalue()


def strip_html(input_data: str, params: Dict[str, Any]) -> str:
    """Strip HTML tags, return plain text."""
    stripper = _HTMLStripper()
    stripper.feed(input_data)
    return stripper.get_text()


def extract_json(input_data: str, params: Dict[str, Any]) -> Any:
    """Find and extract the first JSON object or array from mixed text."""
    decoder = json.JSONDecoder()
    for i, ch in enumerate(input_data):
        if ch in ("{", "["):
            try:
                obj, _ = decoder.raw_decode(input_data, i)
                return obj
            except json.JSONDecodeError:
                continue
    raise ValueError("No JSON object or array found in input")


def truncate(input_data: str, params: Dict[str, Any]) -> str:
    """Cut input to max_length characters."""
    max_length = params.get("max_length", 1000)
    return input_data[:max_length]


def count_tokens(input_data: str, params: Dict[str, Any]) -> dict:
    """Approximate token count (words / 0.75). Returns dict with count and text."""
    words = len(input_data.split())
    token_count = int(words / 0.75) if words else 0
    return {"token_count": token_count, "text": input_data}


def regex_replace(input_data: str, params: Dict[str, Any]) -> str:
    """Apply regex substitution."""
    pattern = params["pattern"]
    replacement = params.get("replacement", "")
    flags_str = params.get("flags", "")
    flags = 0
    flag_map = {"i": re.IGNORECASE, "m": re.MULTILINE, "s": re.DOTALL}
    for ch in flags_str:
        if ch in flag_map:
            flags |= flag_map[ch]
    return re.sub(pattern, replacement, input_data, flags=flags)


def lowercase(input_data: str, params: Dict[str, Any]) -> str:
    return input_data.lower()


def uppercase(input_data: str, params: Dict[str, Any]) -> str:
    return input_data.upper()


# --- Conditions ---


def always_true(context: Dict[str, Any]) -> bool:
    return True


def has_long_input(context: Dict[str, Any]) -> bool:
    """True if last_output is longer than 500 chars (or context threshold)."""
    threshold = context.get("long_input_threshold", 500)
    last_output = context.get("last_output", "")
    if isinstance(last_output, str):
        return len(last_output) > threshold
    return False


def has_html(context: Dict[str, Any]) -> bool:
    """True if last_output contains HTML tags."""
    last_output = context.get("last_output", "")
    if isinstance(last_output, str):
        return bool(re.search(r"<[a-zA-Z][^>]*>", last_output))
    return False


# --- Registration ---


def register_builtins(manager: LocalToolManager):
    manager.register_tool("normalize_text", normalize_text)
    manager.register_tool("route_by_length", route_by_length)
    manager.register_tool("strip_html", strip_html)
    manager.register_tool("extract_json", extract_json)
    manager.register_tool("truncate", truncate)
    manager.register_tool("count_tokens", count_tokens)
    manager.register_tool("regex_replace", regex_replace)
    manager.register_tool("lowercase", lowercase)
    manager.register_tool("uppercase", uppercase)
    manager.register_condition("always_true", always_true)
    manager.register_condition("has_long_input", has_long_input)
    manager.register_condition("has_html", has_html)
