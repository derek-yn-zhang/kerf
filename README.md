<p align="center">
  <strong>Ashlar</strong><br>
  Declarative workflow engine for Claude CLI
</p>

<p align="center">
  <a href="https://pypi.org/project/ashlar/"><img src="https://img.shields.io/pypi/v/ashlar" alt="PyPI"></a>
  <a href="https://pypi.org/project/ashlar/"><img src="https://img.shields.io/pypi/pyversions/ashlar" alt="Python"></a>
  <a href="LICENSE"><img src="https://img.shields.io/pypi/l/ashlar" alt="License"></a>
</p>

---

Ashlar runs deterministic tools first, calls the LLM only when you need reasoning, and logs every result. Pipelines are defined as JSON — no Python required to configure a workflow.

- **Deterministic-first** — preprocessing runs without the LLM until you actually need it
- **JSON workflows** — define tool chains, prompt templates, and fallback policies as config
- **Per-workflow fallback** — `retry` the LLM, degrade to `deterministic` output, or `flag` for review
- **Full execution logging** — every run gets a UUID-stamped log you can audit and learn from
- **Auto-discovered tools** — drop a Python file in `tools/`, it gets picked up

## Install

```bash
uv tool install ashlar
```

Requires Python 3.10+ and Claude CLI (`claude login`).

## Quick Start

```bash
$ ashlar init
Ashlar project initialized.

$ ashlar run summarize "Ashlar is a workflow engine that wraps Claude CLI..."
{
  "deterministic_output": "ashlar is a workflow engine that wraps claude cli...",
  "llm_output": {
    "summary": "Ashlar is a declarative workflow engine..."
  }
}
```

A workflow is a JSON file in `workflows/`:

```json
{
  "task_type": "summarization",
  "tool_chain": [{ "tool": "normalize_text", "condition": "always_true" }],
  "fallback": "retry"
}
```

`tool_chain` runs deterministic preprocessing. `task_type` sends the result to Claude. `fallback` controls what happens when the LLM fails.

Custom tools go in `tools/` as Python files with a `register(manager)` function:

```python
# tools/uppercase.py
def uppercase(input_data, params):
    return input_data.upper()

def register(manager):
    manager.register_tool("uppercase", uppercase)
```

## Documentation

Full docs covering workflows, tools, architecture, and CLI reference at [ashlar.dev](docs/).

## License

MIT
