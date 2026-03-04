import os
import tempfile

from ashlar.config import find_project_root, get_project_paths, load_project_config


class TestFindProjectRoot:
    def test_finds_marker(self):
        with tempfile.TemporaryDirectory() as d:
            d = os.path.realpath(d)
            marker = os.path.join(d, ".ashlar")
            open(marker, "w").close()
            assert find_project_root(d) == d

    def test_walks_up(self):
        with tempfile.TemporaryDirectory() as d:
            d = os.path.realpath(d)
            marker = os.path.join(d, ".ashlar")
            open(marker, "w").close()
            subdir = os.path.join(d, "nested", "deep")
            os.makedirs(subdir)
            assert find_project_root(subdir) == d

    def test_falls_back_to_start(self):
        with tempfile.TemporaryDirectory() as d:
            # No .ashlar marker
            result = find_project_root(d)
            assert result == os.path.realpath(d)


class TestGetProjectPaths:
    def test_returns_expected_keys(self):
        paths = get_project_paths("/fake/project")
        assert paths["workflows"] == "/fake/project/workflows"
        assert paths["tools"] == "/fake/project/tools"
        assert paths["logs"] == "/fake/project/logs"
        assert paths["schemas"] == "/fake/project/schemas"
        assert paths["config"] == "/fake/project/ashlar.toml"
        assert paths["mcp"] == "/fake/project/mcp.json"


class TestLoadProjectConfig:
    def test_missing_config_returns_defaults(self):
        with tempfile.TemporaryDirectory() as d:
            config = load_project_config(d)
            assert config["server"]["host"] == "0.0.0.0"
            assert config["server"]["port"] == 8000
            assert config["defaults"]["fallback"] == "retry"

    def test_valid_config(self):
        with tempfile.TemporaryDirectory() as d:
            config_path = os.path.join(d, "ashlar.toml")
            with open(config_path, "w") as f:
                f.write('[server]\nhost = "localhost"\nport = 9000\n')
            config = load_project_config(d)
            assert config["server"]["host"] == "localhost"
            assert config["server"]["port"] == 9000

    def test_invalid_config_returns_defaults(self):
        with tempfile.TemporaryDirectory() as d:
            config_path = os.path.join(d, "ashlar.toml")
            with open(config_path, "w") as f:
                f.write("this is not valid toml [[[")
            config = load_project_config(d)
            assert config["defaults"]["fallback"] == "retry"
