import os
import tempfile

import pytest

from ashlar.tools import LocalToolManager


def dummy_tool(input_data, params):
    return input_data.upper()


def bad_tool(input_data):
    """Only one param — should fail registration."""
    return input_data


def add_prefix(input_data, params):
    return params.get("prefix", "") + input_data


class TestLocalToolManager:
    def test_register_and_run(self):
        m = LocalToolManager()
        m.register_tool("upper", dummy_tool)
        m.register_condition("always_true", lambda ctx: True)
        chain = [{"tool": "upper", "condition": "always_true"}]
        assert m.run_tool_chain("hello", chain) == "HELLO"

    def test_register_rejects_bad_signature(self):
        m = LocalToolManager()
        with pytest.raises(TypeError, match="must accept"):
            m.register_tool("bad", bad_tool)

    def test_chain_passes_params(self):
        m = LocalToolManager()
        m.register_tool("prefix", add_prefix)
        m.register_condition("always_true", lambda ctx: True)
        chain = [{"tool": "prefix", "condition": "always_true", "params": {"prefix": ">>>"}}]
        assert m.run_tool_chain("hello", chain) == ">>>hello"

    def test_condition_skips_tool(self):
        m = LocalToolManager()
        m.register_tool("upper", dummy_tool)
        m.register_condition("never", lambda ctx: False)
        chain = [{"tool": "upper", "condition": "never"}]
        assert m.run_tool_chain("hello", chain) == "hello"

    def test_missing_tool_raises(self):
        m = LocalToolManager()
        m.register_condition("always_true", lambda ctx: True)
        chain = [{"tool": "nonexistent", "condition": "always_true"}]
        with pytest.raises(ValueError, match="not registered"):
            m.run_tool_chain("hello", chain)

    def test_missing_condition_raises(self):
        m = LocalToolManager()
        m.register_tool("upper", dummy_tool)
        chain = [{"tool": "upper", "condition": "nonexistent"}]
        with pytest.raises(ValueError, match="not registered"):
            m.run_tool_chain("hello", chain)

    def test_load_project_tools(self):
        m = LocalToolManager()
        m.register_condition("always_true", lambda ctx: True)

        with tempfile.TemporaryDirectory() as d:
            # Write a valid tool file
            tool_file = os.path.join(d, "my_tool.py")
            with open(tool_file, "w") as f:
                f.write(
                    "def my_func(input_data, params):\n"
                    "    return input_data + '!'\n"
                    "def register(manager):\n"
                    "    manager.register_tool('my_tool', my_func)\n"
                )
            m.load_project_tools(d)
            assert "my_tool" in m.tools
            chain = [{"tool": "my_tool", "condition": "always_true"}]
            assert m.run_tool_chain("test", chain) == "test!"

    def test_load_skips_broken_files(self):
        m = LocalToolManager()
        with tempfile.TemporaryDirectory() as d:
            broken = os.path.join(d, "broken.py")
            with open(broken, "w") as f:
                f.write("this is not valid python!!!")
            # Should not raise
            m.load_project_tools(d)

    def test_load_skips_underscored_files(self):
        m = LocalToolManager()
        with tempfile.TemporaryDirectory() as d:
            init = os.path.join(d, "__init__.py")
            with open(init, "w") as f:
                f.write("")
            m.load_project_tools(d)
            assert len(m.tools) == 0

    def test_multi_step_chain(self):
        m = LocalToolManager()
        m.register_tool("upper", dummy_tool)
        m.register_tool("prefix", add_prefix)
        m.register_condition("always_true", lambda ctx: True)
        chain = [
            {"tool": "upper", "condition": "always_true"},
            {"tool": "prefix", "condition": "always_true", "params": {"prefix": ">>>"}},
        ]
        assert m.run_tool_chain("hello", chain) == ">>>HELLO"
