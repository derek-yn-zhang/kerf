import json
import os
import tempfile

from kerf.stats import aggregate, collect_logs


def _write_log(logs_dir, entry, name="log.json"):
    os.makedirs(logs_dir, exist_ok=True)
    path = os.path.join(logs_dir, name)
    with open(path, "w") as f:
        json.dump(entry, f)


def _base_entry(**overrides):
    entry = {
        "workflow": "summarize",
        "timestamp": "2025-01-01T00:00:00Z",
        "task_type": "summarize",
        "tool_chain": ["normalize_text"],
        "fallback_policy": "retry",
        "fallback_triggered": False,
        "result": {"summary": "ok"},
    }
    entry.update(overrides)
    return entry


class TestCollectLogs:
    def test_empty_dir(self):
        d = tempfile.mkdtemp()
        assert collect_logs(d) == []

    def test_missing_dir(self):
        assert collect_logs("/nonexistent/path") == []

    def test_reads_json_files(self):
        d = tempfile.mkdtemp()
        logs_dir = os.path.join(d, "logs")
        _write_log(logs_dir, _base_entry(), "a.json")
        _write_log(logs_dir, _base_entry(workflow="clean"), "b.json")
        entries = collect_logs(logs_dir)
        assert len(entries) == 2

    def test_ignores_non_json(self):
        d = tempfile.mkdtemp()
        logs_dir = os.path.join(d, "logs")
        _write_log(logs_dir, _base_entry(), "a.json")
        with open(os.path.join(logs_dir, "notes.txt"), "w") as f:
            f.write("not a log")
        assert len(collect_logs(logs_dir)) == 1

    def test_skips_malformed_json(self):
        d = tempfile.mkdtemp()
        logs_dir = os.path.join(d, "logs")
        os.makedirs(logs_dir)
        with open(os.path.join(logs_dir, "bad.json"), "w") as f:
            f.write("{broken")
        _write_log(logs_dir, _base_entry(), "good.json")
        assert len(collect_logs(logs_dir)) == 1

    def test_workflow_filter(self):
        d = tempfile.mkdtemp()
        logs_dir = os.path.join(d, "logs")
        _write_log(logs_dir, _base_entry(workflow="summarize"), "a.json")
        _write_log(logs_dir, _base_entry(workflow="clean"), "b.json")
        assert len(collect_logs(logs_dir, workflow_filter="clean")) == 1


class TestAggregate:
    def test_empty(self):
        result = aggregate([])
        assert result == {"total_runs": 0}

    def test_basic_counts(self):
        entries = [_base_entry(), _base_entry(), _base_entry(workflow="clean")]
        result = aggregate(entries)
        assert result["total_runs"] == 3
        assert result["workflows"]["summarize"] == 2
        assert result["workflows"]["clean"] == 1

    def test_llm_vs_tool_only(self):
        entries = [
            _base_entry(task_type="summarize"),
            _base_entry(task_type=None),
            _base_entry(task_type=None),
        ]
        result = aggregate(entries)
        assert result["llm_runs"] == 1
        assert result["tool_only_runs"] == 2

    def test_fallback_rate(self):
        entries = [
            _base_entry(fallback_triggered=True),
            _base_entry(fallback_triggered=False),
            _base_entry(fallback_triggered=False),
            _base_entry(fallback_triggered=True),
        ]
        result = aggregate(entries)
        assert result["fallback_triggered"] == 2
        assert result["fallback_rate"] == 0.5

    def test_error_count(self):
        entries = [
            _base_entry(result={"summary": "ok"}),
            _base_entry(result={"error": "failed", "fallback": "retry_exhausted"}),
            _base_entry(result={"error": "timeout"}),
        ]
        result = aggregate(entries)
        assert result["error_count"] == 2
        assert result["success_rate"] == round(1 / 3, 3)

    def test_success_rate_all_good(self):
        entries = [_base_entry(), _base_entry()]
        result = aggregate(entries)
        assert result["success_rate"] == 1.0
        assert result["error_count"] == 0
