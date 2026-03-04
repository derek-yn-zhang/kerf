# Server API

The Ashlar server exposes a single endpoint.

## `POST /execute`

Execute a workflow.

### Request

```json
{
  "workflow_name": "summarize",
  "input_data": "text to process",
  "fallback_enabled": true
}
```

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `workflow_name` | string | yes | — | Name matching `workflows/<name>.json` |
| `input_data` | string | yes | — | Input text |
| `fallback_enabled` | boolean | no | `true` | Whether to apply fallback policies |

### Response (200)

If the workflow has a `task_type`, the response is the LLM output:

```json
{
  "summary": "Quarterly revenue grew 15% YoY, driven by enterprise expansion."
}
```

If the workflow is tool-chain-only (no `task_type`), the response wraps the preprocessed output:

```json
{
  "output": "preprocessed text"
}
```

### Error (404)

```json
{
  "detail": "Workflow 'nonexistent' not found at workflows/nonexistent.json"
}
```
