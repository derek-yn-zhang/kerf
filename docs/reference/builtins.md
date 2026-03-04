# Built-in Tools and Conditions

These ship with Kerf and are available in every project without registration.

## Tools

### `normalize_text`

Collapse all whitespace (newlines, tabs, multiple spaces) into single spaces.

```python
normalize_text("  hello\n  world  ", {})  # "hello world"
```

### `route_by_length`

Return a workflow name based on input length. Used for routing input to different workflows.

```python
route_by_length("short text", {
    "threshold": 500,
    "routes": {"short_text": "summarize_brief", "long_text": "summarize_full"}
})  # "summarize_brief"
```

| Param | Type | Default | Description |
|---|---|---|---|
| `threshold` | int | `500` | Character count cutoff |
| `routes.short_text` | string | — | Workflow name for short input |
| `routes.long_text` | string | — | Workflow name for long input |

## Conditions

### `always_true`

Always returns `True`. This is the default condition if none is specified in a workflow step.
