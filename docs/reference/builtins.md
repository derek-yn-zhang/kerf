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
| `routes.short_text` | string | - | Workflow name for short input |
| `routes.long_text` | string | - | Workflow name for long input |

### `strip_html`

Strip HTML tags and return plain text. Uses Python's stdlib `HTMLParser`.

```python
strip_html("<p>hello <b>world</b></p>", {})  # "hello world"
```

### `extract_json`

Find and extract the first JSON object or array from mixed text. Useful for parsing LLM output that includes prose around the JSON.

```python
extract_json('Here is the result: {"key": "value"} done', {})  # {"key": "value"}
```

Raises `ValueError` if no valid JSON is found.

### `truncate`

Cut input to a maximum number of characters.

```python
truncate("long text here...", {"max_length": 8})  # "long tex"
```

| Param | Type | Default | Description |
|---|---|---|---|
| `max_length` | int | `1000` | Maximum character count |

### `count_tokens`

Approximate token count based on word count (words / 0.75). Returns a dict with the count and original text.

```python
count_tokens("one two three four", {})
# {"token_count": 5, "text": "one two three four"}
```

Note: this tool returns a `dict`, not a `str`. If used mid-chain, the next tool will receive a dict. Best used as the last step or for routing decisions.

### `regex_replace`

Apply a regex substitution.

```python
regex_replace("hello world", {"pattern": "world", "replacement": "earth"})
# "hello earth"
```

| Param | Type | Default | Description |
|---|---|---|---|
| `pattern` | string | **required** | Regex pattern to match |
| `replacement` | string | `""` | Replacement string (supports backreferences like `\1`) |
| `flags` | string | `""` | Flag characters: `i` (case-insensitive), `m` (multiline), `s` (dotall) |

### `lowercase`

Convert input to lowercase.

```python
lowercase("HELLO World", {})  # "hello world"
```

### `uppercase`

Convert input to uppercase.

```python
uppercase("hello World", {})  # "HELLO WORLD"
```

## Conditions

Conditions control whether a tool chain step runs. They receive a `context` dict containing `last_output` (the output of the previous step, or the original input on the first step).

### `always_true`

Always returns `True`. This is the default condition if none is specified in a workflow step.

### `has_long_input`

Returns `True` if `last_output` is longer than 500 characters. The threshold can be overridden by setting `long_input_threshold` in the context.

```json
{
  "tool_chain": [
    { "tool": "normalize_text" },
    { "tool": "truncate", "condition": "has_long_input", "params": { "max_length": 2000 } }
  ]
}
```

### `has_html`

Returns `True` if `last_output` contains HTML tags.

```json
{
  "tool_chain": [
    { "tool": "strip_html", "condition": "has_html" },
    { "tool": "normalize_text" }
  ]
}
```
