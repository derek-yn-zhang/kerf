# CLI Commands

## `ashlar init`

Scaffold a new project in the current directory.

```bash
ashlar init
```

Creates `.ashlar`, `workflows/`, `schemas/`, `tools/`, `logs/`, and `ashlar.toml`. Fails if `.ashlar` already exists.

## `ashlar run`

Execute a workflow.

```bash
ashlar run <workflow> [input] [--debug]
```

| Argument / Option | Description |
|---|---|
| `workflow` | Workflow name (matches `workflows/<name>.json`) |
| `input` | Input text (optional — reads stdin if omitted) |
| `--debug` | Show debug output: tool chain execution, prompts, LLM responses |

```bash
# argument
ashlar run summarize "some text"

# stdin
cat file.txt | ashlar run summarize
echo "some text" | ashlar run summarize

# debug mode — see what's happening under the hood
ashlar run --debug summarize "some text"
```

Prints JSON result to stdout. With `--debug`, also prints the full execution trace to stderr.

Set `ASHLAR_DEBUG=1` to always show tracebacks on errors.

## `ashlar serve`

Start the API server.

```bash
ashlar serve [--host HOST] [--port PORT]
```

| Option | Default | Description |
|---|---|---|
| `--host` | `0.0.0.0` | Server host |
| `--port` | `8000` | Server port |

## `ashlar add`

Scaffold new resources.

```bash
ashlar add workflow <name>    # creates workflows/<name>.json
ashlar add tool <name>        # creates tools/<name>.py
ashlar add mcp <name>         # adds MCP server entry to mcp.json
```

Fails if the resource already exists. `ashlar add mcp` creates or appends to `mcp.json` in Claude CLI's native config format.

## `ashlar list`

Show available workflows and tools in the current project.

```bash
ashlar list
```

## `ashlar logs`

View recent execution logs.

```bash
ashlar logs [--last N] [--workflow NAME]
```

| Option | Default | Description |
|---|---|---|
| `--last` | `10` | Number of recent logs to show |
| `--workflow` | — | Filter by workflow name |
