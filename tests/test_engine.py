import json
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from kerf.engine import execute_workflow


def _setup_project(tmpdir, workflow_name, workflow_config):
    """Create a minimal kerf project with one workflow."""
    os.makedirs(os.path.join(tmpdir, "workflows"))
    os.makedirs(os.path.join(tmpdir, "tools"))
    os.makedirs(os.path.join(tmpdir, "logs"))
    os.makedirs(os.path.join(tmpdir, "schemas"))

    # .kerf marker
    open(os.path.join(tmpdir, ".kerf"), "w").close()

    # kerf.toml
    with open(os.path.join(tmpdir, "kerf.toml"), "w") as f:
        f.write('[defaults]\nfallback = "retry"\n')

    # Workflow
    wf_path = os.path.join(tmpdir, "workflows", f"{workflow_name}.json")
    with open(wf_path, "w") as f:
        json.dump(workflow_config, f)


class TestExecuteWorkflow:
    def test_tool_only_workflow(self):
        """Workflow with no task_type runs tools and returns output."""
        with tempfile.TemporaryDirectory() as d:
            _setup_project(d, "clean", {
                "task_type": None,
                "tool_chain": [
                    {"tool": "normalize_text", "condition": "always_true"}
                ],
            })
            result = execute_workflow("clean", "  hello   world  ", d)
            assert result == {"output": "hello world"}

    def test_tool_only_no_chain(self):
        """Workflow with no tools and no LLM returns raw input."""
        with tempfile.TemporaryDirectory() as d:
            _setup_project(d, "passthrough", {
                "task_type": None,
                "tool_chain": [],
            })
            result = execute_workflow("passthrough", "raw input", d)
            assert result == {"output": "raw input"}

    @patch("kerf.engine.GARInterface")
    def test_llm_workflow(self, mock_gar_cls):
        """Workflow with task_type calls the LLM."""
        mock_gar = MagicMock()
        mock_gar.call_gar.return_value = {"summary": "test summary"}
        mock_gar_cls.return_value = mock_gar

        with tempfile.TemporaryDirectory() as d:
            _setup_project(d, "summarize", {
                "task_type": "summarization",
                "tool_chain": [
                    {"tool": "normalize_text", "condition": "always_true"}
                ],
            })
            result = execute_workflow("summarize", "some long text", d)
            assert result == {"summary": "test summary"}
            mock_gar.call_gar.assert_called_once()

    @patch("kerf.engine.GARInterface")
    def test_template_params_passed(self, mock_gar_cls):
        """template_params are forwarded to construct_prompt."""
        mock_gar = MagicMock()
        mock_gar.call_gar.return_value = {"category": "bug", "confidence": "high"}
        mock_gar_cls.return_value = mock_gar

        with tempfile.TemporaryDirectory() as d:
            _setup_project(d, "classify", {
                "task_type": "classification",
                "template_params": {"categories": "bug, feature"},
                "tool_chain": [],
            })
            result = execute_workflow("classify", "it crashes", d)
            assert result["category"] == "bug"
            # Verify the prompt contains the categories
            prompt_arg = mock_gar.call_gar.call_args[0][0]
            assert "bug, feature" in prompt_arg

    @patch("kerf.engine.GARInterface")
    def test_retry_fallback(self, mock_gar_cls):
        """Retry fallback retries once then returns error."""
        mock_gar = MagicMock()
        mock_gar.call_gar.side_effect = Exception("LLM down")
        mock_gar_cls.return_value = mock_gar

        with tempfile.TemporaryDirectory() as d:
            _setup_project(d, "summarize", {
                "task_type": "summarization",
                "tool_chain": [],
                "fallback": "retry",
            })
            result = execute_workflow("summarize", "test", d)
            assert result["fallback"] == "retry_exhausted"
            assert "LLM down" in result["error"]
            assert mock_gar.call_gar.call_count == 2

    @patch("kerf.engine.GARInterface")
    def test_deterministic_fallback(self, mock_gar_cls):
        """Deterministic fallback returns preprocessed input."""
        mock_gar = MagicMock()
        mock_gar.call_gar.side_effect = Exception("fail")
        mock_gar_cls.return_value = mock_gar

        with tempfile.TemporaryDirectory() as d:
            _setup_project(d, "summarize", {
                "task_type": "summarization",
                "tool_chain": [
                    {"tool": "normalize_text", "condition": "always_true"}
                ],
                "fallback": "deterministic",
            })
            result = execute_workflow("summarize", "  raw  input  ", d)
            assert result == {"fallback_output": "raw input"}

    @patch("kerf.engine.GARInterface")
    def test_flag_fallback(self, mock_gar_cls):
        """Flag fallback returns error with flagged=True."""
        mock_gar = MagicMock()
        mock_gar.call_gar.side_effect = Exception("fail")
        mock_gar_cls.return_value = mock_gar

        with tempfile.TemporaryDirectory() as d:
            _setup_project(d, "classify", {
                "task_type": "classification",
                "template_params": {"categories": "bug, feature"},
                "tool_chain": [],
                "fallback": "flag",
            })
            result = execute_workflow("classify", "test", d)
            assert result["flagged"] is True

    def test_missing_workflow_raises(self):
        with tempfile.TemporaryDirectory() as d:
            _setup_project(d, "exists", {"task_type": None, "tool_chain": []})
            with pytest.raises(FileNotFoundError, match="not found"):
                execute_workflow("nonexistent", "test", d)

    def test_invalid_json_raises(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "workflows"))
            os.makedirs(os.path.join(d, "logs"))
            open(os.path.join(d, ".kerf"), "w").close()
            with open(os.path.join(d, "kerf.toml"), "w") as f:
                f.write('[defaults]\nfallback = "retry"\n')
            with open(os.path.join(d, "workflows", "bad.json"), "w") as f:
                f.write("not json{{{")
            with pytest.raises(ValueError, match="invalid JSON"):
                execute_workflow("bad", "test", d)

    def test_invalid_task_type_raises(self):
        with tempfile.TemporaryDirectory() as d:
            _setup_project(d, "bad", {"task_type": "typo", "tool_chain": []})
            with pytest.raises(ValueError, match="Unknown task_type"):
                execute_workflow("bad", "test", d)

    @patch("kerf.engine.GARInterface")
    def test_log_written(self, mock_gar_cls):
        """Every execution writes a log file."""
        mock_gar = MagicMock()
        mock_gar.call_gar.return_value = {"summary": "ok"}
        mock_gar_cls.return_value = mock_gar

        with tempfile.TemporaryDirectory() as d:
            _setup_project(d, "summarize", {
                "task_type": "summarization",
                "tool_chain": [],
            })
            execute_workflow("summarize", "test input", d)
            log_files = os.listdir(os.path.join(d, "logs"))
            assert len(log_files) == 1
            with open(os.path.join(d, "logs", log_files[0])) as f:
                log = json.load(f)
            assert log["workflow"] == "summarize"
            assert log["task_type"] == "summarization"
            assert log["input_preview"] == "test input"
            assert log["result"] == {"summary": "ok"}

    def test_project_default_fallback_applied(self):
        """Workflow without fallback inherits from kerf.toml."""
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "workflows"))
            os.makedirs(os.path.join(d, "tools"))
            os.makedirs(os.path.join(d, "logs"))
            open(os.path.join(d, ".kerf"), "w").close()
            with open(os.path.join(d, "kerf.toml"), "w") as f:
                f.write('[defaults]\nfallback = "flag"\n')
            # Workflow omits fallback
            with open(os.path.join(d, "workflows", "test.json"), "w") as f:
                json.dump({"task_type": None, "tool_chain": []}, f)

            result = execute_workflow("test", "input", d)
            # Check the log to see what fallback was used
            log_files = os.listdir(os.path.join(d, "logs"))
            with open(os.path.join(d, "logs", log_files[0])) as f:
                log = json.load(f)
            assert log["fallback_policy"] == "flag"
