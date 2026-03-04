import json
import os
import tempfile

from ashlar.gar import GARInterface


class TestExtractJson:
    def setup_method(self):
        self.gar = GARInterface.__new__(GARInterface)
        self.gar.project_dir = "."

    def test_raw_json(self):
        result = self.gar._extract_json('{"key": "value"}')
        assert result == {"key": "value"}

    def test_markdown_code_block(self):
        text = '```json\n{"key": "value"}\n```'
        result = self.gar._extract_json(text)
        assert result == {"key": "value"}

    def test_markdown_without_json_tag(self):
        text = '```\n{"key": "value"}\n```'
        result = self.gar._extract_json(text)
        assert result == {"key": "value"}

    def test_no_json_raises(self):
        import pytest
        with pytest.raises(ValueError, match="No JSON found"):
            self.gar._extract_json("just some text")


class TestStripAnsi:
    def setup_method(self):
        self.gar = GARInterface.__new__(GARInterface)
        self.gar.project_dir = "."

    def test_strips_codes(self):
        text = "\x1b[32mgreen\x1b[0m"
        assert self.gar._strip_ansi(text) == "green"

    def test_clean_text_unchanged(self):
        assert self.gar._strip_ansi("hello") == "hello"


class TestHasConfiguredServers:
    def setup_method(self):
        self.gar = GARInterface.__new__(GARInterface)
        self.gar.project_dir = "."

    def test_empty_command_returns_false(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"mcpServers": {"test": {"command": "", "args": []}}}, f)
            path = f.name
        try:
            assert self.gar._has_configured_servers(path) is False
        finally:
            os.unlink(path)

    def test_valid_command_returns_true(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"mcpServers": {"test": {"command": "npx", "args": ["-y", "server"]}}}, f)
            path = f.name
        try:
            assert self.gar._has_configured_servers(path) is True
        finally:
            os.unlink(path)

    def test_no_servers_returns_false(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"mcpServers": {}}, f)
            path = f.name
        try:
            assert self.gar._has_configured_servers(path) is False
        finally:
            os.unlink(path)

    def test_bad_json_returns_false(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("not json")
            path = f.name
        try:
            assert self.gar._has_configured_servers(path) is False
        finally:
            os.unlink(path)

    def test_missing_file_returns_false(self):
        assert self.gar._has_configured_servers("/nonexistent/path.json") is False
