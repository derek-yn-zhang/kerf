# Using the API Server

Ashlar includes a FastAPI server for running workflows over HTTP.

## Start the server

```bash
ashlar serve
```

Custom host and port:

```bash
ashlar serve --host 127.0.0.1 --port 3000
```

## Execute a workflow

```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "summarize",
    "input_data": "Your text here...",
    "fallback_enabled": true
  }'
```

Response:

```json
{
  "summary": "..."
}
```

## Request format

| Field | Type | Required | Description |
|---|---|---|---|
| `workflow_name` | string | yes | Name of the workflow (matches `workflows/<name>.json`) |
| `input_data` | string | yes | Input text to process |
| `fallback_enabled` | boolean | no | Enable fallback policies (default: `true`) |

## Error handling

If the workflow doesn't exist, you get a 404:

```json
{
  "detail": "Workflow 'nonexistent' not found at workflows/nonexistent.json"
}
```

## When to use the server vs CLI

Use `ashlar serve` when you want to call workflows from other services, integrate with existing APIs, or run workflows from non-Python code. Use `ashlar run` for scripting, testing, and one-off executions.

Both call the same engine — results are identical.
