"""Aggregate execution logs into summary statistics."""

import json
import os
from collections import Counter
from typing import Any


def collect_logs(logs_dir: str, workflow_filter: str | None = None) -> list[dict[str, Any]]:
    """Read all JSON log files from the logs directory."""
    if not os.path.isdir(logs_dir):
        return []

    entries = []
    for filename in os.listdir(logs_dir):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(logs_dir, filename)
        try:
            with open(filepath, "r") as f:
                entry = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        if workflow_filter and entry.get("workflow") != workflow_filter:
            continue
        entries.append(entry)
    return entries


def aggregate(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute summary statistics from log entries."""
    total = len(entries)
    if total == 0:
        return {"total_runs": 0}

    workflow_counts = Counter(e.get("workflow", "unknown") for e in entries)
    fallback_triggered = sum(1 for e in entries if e.get("fallback_triggered"))
    has_llm = sum(1 for e in entries if e.get("task_type"))
    tool_only = total - has_llm
    errors = sum(
        1 for e in entries
        if isinstance(e.get("result"), dict) and "error" in e["result"]
    )

    return {
        "total_runs": total,
        "workflows": dict(workflow_counts.most_common()),
        "llm_runs": has_llm,
        "tool_only_runs": tool_only,
        "fallback_triggered": fallback_triggered,
        "fallback_rate": round(fallback_triggered / total, 3) if total else 0,
        "error_count": errors,
        "success_rate": round((total - errors) / total, 3) if total else 0,
    }
