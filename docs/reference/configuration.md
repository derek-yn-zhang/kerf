# Configuration

## `ashlar.toml`

Optional project-level config file created by `ashlar init`.

```toml
[server]
host = "0.0.0.0"
port = 8000

[defaults]
fallback = "retry"
```

### `[server]`

| Key | Type | Default | Description |
|---|---|---|---|
| `host` | string | `"0.0.0.0"` | Server bind address |
| `port` | int | `8000` | Server port |

### `[defaults]`

| Key | Type | Default | Description |
|---|---|---|---|
| `fallback` | string | `"retry"` | Default fallback policy for workflows that don't specify one |

If `ashlar.toml` is missing, all defaults apply. If it has a parse error, Ashlar warns and falls back to defaults.

!!! note "Python 3.10"
    Python 3.10 needs the `tomli` package to parse TOML (included automatically as a dependency). Python 3.11+ uses the built-in `tomllib`.

## `mcp.json`

Optional MCP server configuration. When present, Ashlar passes `--mcp-config mcp.json` to Claude CLI calls, giving the LLM access to external tools during reasoning.

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/mydb"],
      "env": {}
    }
  }
}
```

Manage entries with `ashlar add mcp <name>`. See [Using MCP Servers](../guides/mcp.md) for details.

## Project detection

Ashlar finds your project root by walking up from the current directory looking for a `.ashlar` marker file. This works the same way git finds `.git/` — you can run `ashlar` commands from any subdirectory.

If no `.ashlar` file is found, Ashlar uses the current directory as the project root.
