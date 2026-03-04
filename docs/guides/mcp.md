# Using MCP Servers

MCP (Model Context Protocol) servers give the LLM access to external data during workflow execution — databases, APIs, file systems, anything that helps it produce better output instead of guessing.

## Add an MCP server

```bash
kerf add mcp postgres
```

This creates or appends to `mcp.json` at your project root. Edit the entry with the actual server command:

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

## How it works

When a workflow has a `task_type` (i.e., it calls the LLM), Kerf checks for `mcp.json`. If it exists, `--mcp-config mcp.json` is passed to the Claude CLI call. The LLM can then use MCP tools during its reasoning — querying a database, reading files, calling APIs — before returning its structured output.

No `mcp.json` = no MCP = no change in behavior. It's opt-in.

## When to use MCP

MCP is most valuable when the LLM needs context it can't get from the input alone:

- **Database lookups** — classify a support ticket by looking up the customer's account
- **File system access** — summarize a document by reading related files
- **API calls** — enrich extracted data with live information

Without MCP, the LLM only sees the prompt you construct from the input. With MCP, it can pull in whatever context it needs.

## Multiple servers

Add as many servers as you need:

```bash
kerf add mcp postgres
kerf add mcp filesystem
kerf add mcp slack
```

All servers in `mcp.json` are available to every LLM call. The LLM decides which ones to use based on the task.

## Format

`mcp.json` uses the same format as Claude CLI's `--mcp-config`. See the [Claude CLI docs](https://docs.anthropic.com/en/docs/claude-code) for the full spec.
