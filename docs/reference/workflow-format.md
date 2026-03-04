# Workflow Format

Workflow files live in `workflows/` and are JSON objects. They're validated with Pydantic on load. Typos in `task_type`, invalid `fallback` values, or malformed `tool_chain` entries fail immediately with clear error messages.

## Schema

```json
{
  "task_type": "classification",
  "template_params": {
    "categories": "bug, feature_request, question, documentation"
  },
  "schema_path": "schemas/category.json",
  "tool_chain": [
    {
      "tool": "normalize_text",
      "condition": "always_true",
      "params": {}
    }
  ],
  "fallback": "flag"
}
```

## Fields

### `task_type`

Type: `string | null`

Which prompt template to use for the LLM step. Built-in types:

| Value | Prompt |
|---|---|
| `"summarization"` | Summarize in 3 sentences, return `{"summary": ...}` |
| `"structured_extraction"` | Extract specified fields, return JSON with exact keys |
| `"classification"` | Classify into given categories, return `{"category": ...}` |

Set to `null` or omit to skip the LLM call entirely (tool-chain-only workflow). Any other value will fail validation.

### `template_params`

Type: `object`

Key-value pairs injected into the prompt template. Some task types require specific params:

| Task type | Required params | Example |
|---|---|---|
| `"summarization"` | (none) | `{}` |
| `"classification"` | `categories` | `{"categories": "bug, feature, question"}` |
| `"structured_extraction"` | `fields` | `{"fields": "name, email, company"}` |

If a template has placeholder variables (like `{categories}`) and you don't provide the matching param, the workflow will fail with a `KeyError`.

### `schema_path`

Type: `string | null`

Path to a JSON schema file, relative to the project root. Used to validate LLM output. If required keys are missing, the fallback policy triggers.

### `tool_chain`

Type: `array`

Ordered list of preprocessing steps. Each step is an object:

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `tool` | string | yes | - | Name of a registered tool |
| `condition` | string | no | `"always_true"` | Name of a registered condition |
| `params` | object | no | `{}` | Passed to the tool function as the second argument |

Steps execute in order. Each step's output becomes the next step's input.

### `fallback`

Type: `string`

What to do when the LLM call fails or schema validation fails.

| Value | Behavior |
|---|---|
| `"retry"` | Call the LLM once more. If both attempts fail, returns `{"error": ..., "fallback": "retry_exhausted"}` |
| `"deterministic"` | Return the preprocessed output (skip LLM) |
| `"flag"` | Return the error in the output for manual review |

Defaults to the `fallback` value in `kerf.toml` (which defaults to `"retry"` if not set). Only these three values are accepted.
