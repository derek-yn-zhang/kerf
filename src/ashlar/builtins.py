from typing import Any, Dict

from ashlar.tools import LocalToolManager


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


def always_true(context: Dict[str, Any]) -> bool:
    return True


def register_builtins(manager: LocalToolManager):
    manager.register_tool("normalize_text", normalize_text)
    manager.register_tool("route_by_length", route_by_length)
    manager.register_condition("always_true", always_true)
