import logging
import os
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

logger = logging.getLogger("kerf")

KERF_PROJECT_MARKER = ".kerf"


def find_project_root(start: str = None) -> str:
    """Walk up from start directory looking for .kerf marker file.
    Falls back to start directory if not found."""
    current = Path(start or os.getcwd()).resolve()
    for directory in [current, *current.parents]:
        if (directory / KERF_PROJECT_MARKER).exists():
            return str(directory)
    return str(current)


def get_project_paths(project_dir: str) -> dict:
    """Return standard paths for a kerf project."""
    return {
        "workflows": os.path.join(project_dir, "workflows"),
        "schemas": os.path.join(project_dir, "schemas"),
        "tools": os.path.join(project_dir, "tools"),
        "logs": os.path.join(project_dir, "logs"),
        "config": os.path.join(project_dir, "kerf.toml"),
        "mcp": os.path.join(project_dir, "mcp.json"),
    }


def load_project_config(project_dir: str) -> dict:
    """Load and validate kerf.toml. Returns defaults if missing or unparseable."""
    from kerf.models import KerfConfig

    config_path = os.path.join(project_dir, "kerf.toml")
    if not os.path.exists(config_path):
        return KerfConfig().model_dump()
    if tomllib is None:
        logger.warning(
            "kerf.toml found but tomli not installed (Python <3.11). "
            "Install 'tomli' or upgrade to Python 3.11+. Using defaults."
        )
        return KerfConfig().model_dump()
    try:
        with open(config_path, "rb") as f:
            raw = tomllib.load(f)
        return KerfConfig(**raw).model_dump()
    except Exception as e:
        logger.warning("Failed to parse kerf.toml: %s. Using defaults.", e)
        return KerfConfig().model_dump()
