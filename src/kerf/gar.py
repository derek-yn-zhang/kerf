import json
import logging
import os
import re
import shutil
import subprocess
from typing import Any, Dict, Optional

logger = logging.getLogger("kerf")


class GARInterface:
    def __init__(self, project_dir: str = None):
        self.project_dir = project_dir or os.getcwd()
        if not shutil.which("claude"):
            raise FileNotFoundError(
                "Claude CLI not found on PATH. Install it and run 'claude login'."
            )

    def _strip_ansi(self, text: str) -> str:
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        return ansi_escape.sub("", text).strip()

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from Claude's response text.

        Handles both raw JSON and JSON wrapped in markdown code blocks.
        """
        text = text.strip()
        # Try raw JSON first
        if text.startswith("{"):
            return json.loads(text)
        # Extract from markdown code block
        match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
        if match:
            return json.loads(match.group(1).strip())
        raise ValueError(f"No JSON found in response: {text[:200]}")

    def _has_configured_servers(self, mcp_config_path: str) -> bool:
        """Check if MCP config has any servers with non-empty commands."""
        try:
            with open(mcp_config_path, "r") as f:
                config = json.load(f)
            servers = config.get("mcpServers", {})
            return any(s.get("command") for s in servers.values())
        except (json.JSONDecodeError, OSError):
            return False

    def call_gar(
        self,
        prompt: str,
        schema_path: Optional[str] = None,
        mcp_config_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        cmd = [
            "claude",
            "-p",
            prompt,
            "--output-format",
            "json",
        ]
        if schema_path:
            cmd.extend(["--json-schema", schema_path])
        if mcp_config_path and os.path.exists(mcp_config_path):
            if self._has_configured_servers(mcp_config_path):
                cmd.extend(["--mcp-config", mcp_config_path])
                logger.debug("Using MCP config: %s", mcp_config_path)
            else:
                logger.debug("Skipping MCP config (no servers with commands configured)")
        try:
            logger.debug("Running: %s", " ".join(cmd[:4]) + " ...")
            process = subprocess.run(
                cmd, cwd=self.project_dir, capture_output=True, text=True, check=True
            )
            clean_stdout = self._strip_ansi(process.stdout)
            raw = json.loads(clean_stdout)

            # --output-format json returns a session object with a result field
            if isinstance(raw, dict) and "result" in raw:
                result_text = raw["result"]
                if raw.get("is_error"):
                    raise Exception(f"Claude returned an error: {result_text}")
                return self._extract_json(result_text)

            return raw
        except subprocess.CalledProcessError as e:
            error_msg = self._strip_ansi(e.stderr)
            raise Exception(f"Claude CLI error: {error_msg}") from e
        except json.JSONDecodeError as e:
            raise Exception(
                "Failed to parse Claude CLI output as JSON. "
                "Raw output may contain non-JSON content."
            ) from e
