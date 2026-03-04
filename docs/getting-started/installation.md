# Installation

## Prerequisites

- Python 3.10+
- [Claude CLI](https://docs.anthropic.com/en/docs/claude-code) — run `claude login` to authenticate
- [uv](https://docs.astral.sh/uv/) (recommended) or pipx

Kerf calls Claude CLI under the hood. If you see `"Claude CLI not found on PATH"`, install [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and run `claude login` to authenticate.

## Install

```bash
uv tool install kerf
```

Or with pipx:

```bash
pipx install kerf
```

Or from source:

```bash
git clone https://github.com/yourusername/kerf.git
cd kerf
uv tool install .
```

Verify the installation:

```bash
kerf --help
```

```
Usage: kerf [OPTIONS] COMMAND [ARGS]...

  Kerf — declarative workflow engine where the LLM is a pluggable,
  disposable step.

Commands:
  add    Add a new workflow, tool, or MCP config.
  init   Scaffold a new kerf project in the current directory.
  list   List available workflows and tools.
  logs   View recent execution logs.
  run    Execute a workflow.
  serve  Start the Kerf API server.
```
