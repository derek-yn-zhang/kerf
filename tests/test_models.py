import pytest
from pydantic import ValidationError

from kerf.models import KerfConfig, ToolChainStep, WorkflowConfig


class TestWorkflowConfig:
    def test_valid_summarization(self):
        wf = WorkflowConfig(task_type="summarization", fallback="retry")
        assert wf.task_type == "summarization"
        assert wf.fallback == "retry"
        assert wf.tool_chain == []
        assert wf.template_params == {}

    def test_valid_classification_with_params(self):
        wf = WorkflowConfig(
            task_type="classification",
            template_params={"categories": "bug, feature, question"},
            fallback="flag",
        )
        assert wf.template_params["categories"] == "bug, feature, question"

    def test_tool_only_workflow(self):
        wf = WorkflowConfig(
            task_type=None,
            tool_chain=[ToolChainStep(tool="normalize_text")],
        )
        assert wf.task_type is None
        assert len(wf.tool_chain) == 1

    def test_invalid_task_type_rejected(self):
        with pytest.raises(ValidationError, match="Unknown task_type"):
            WorkflowConfig(task_type="typo")

    def test_invalid_fallback_rejected(self):
        with pytest.raises(ValidationError):
            WorkflowConfig(fallback="invalid")

    def test_defaults(self):
        wf = WorkflowConfig()
        assert wf.task_type is None
        assert wf.schema_path is None
        assert wf.tool_chain == []
        assert wf.fallback == "retry"
        assert wf.template_params == {}


class TestToolChainStep:
    def test_defaults(self):
        step = ToolChainStep(tool="my_tool")
        assert step.condition == "always_true"
        assert step.params == {}

    def test_with_params(self):
        step = ToolChainStep(tool="my_tool", condition="check", params={"key": "val"})
        assert step.params["key"] == "val"


class TestKerfConfig:
    def test_defaults(self):
        cfg = KerfConfig()
        assert cfg.server.host == "0.0.0.0"
        assert cfg.server.port == 8000
        assert cfg.defaults.fallback == "retry"

    def test_override(self):
        cfg = KerfConfig(
            server={"host": "localhost", "port": 9000},
            defaults={"fallback": "flag"},
        )
        assert cfg.server.host == "localhost"
        assert cfg.server.port == 9000
        assert cfg.defaults.fallback == "flag"
