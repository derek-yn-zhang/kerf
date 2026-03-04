# Writing Workflows

Workflows are JSON files in `workflows/`. Each one defines a pipeline — what tools to run, whether to call the LLM, and what to do if it fails.

## Create a workflow

```bash
ashlar add workflow classify
```

This creates a template you can edit:

```json
{
  "task_type": null,
  "schema_path": null,
  "tool_chain": [],
  "fallback": "retry"
}
```

## Example: text classification

```json
{
  "task_type": "classification",
  "template_params": {
    "categories": "bug, feature_request, question, infrastructure"
  },
  "tool_chain": [
    { "tool": "normalize_text", "condition": "always_true" }
  ],
  "fallback": "flag"
}
```

The `template_params` fill in the prompt template — here, `{categories}` gets replaced with the list of categories. This normalizes the input, sends it to Claude for classification, and flags failures for review.

Run it:

```bash
ashlar run classify "urgent: server is down and customers can't log in"
```

```json
{
  "category": "infrastructure",
  "confidence": "high"
}
```

## Tool-chain-only workflows

Omit `task_type` to skip the LLM entirely:

```json
{
  "tool_chain": [
    { "tool": "normalize_text" },
    { "tool": "uppercase" }
  ],
  "fallback": "retry"
}
```

This runs deterministic tools and returns the result. No LLM call, no latency, no cost. Use this for pipelines where you've already figured out the pattern.

## Conditional steps

Each tool chain step can have a condition that controls whether it runs:

```json
{
  "tool_chain": [
    { "tool": "normalize_text", "condition": "always_true" },
    { "tool": "heavy_processing", "condition": "has_long_input" }
  ]
}
```

Conditions are named references to registered Python functions. See [Writing Tools](tools.md) for how to register them.

## Passing parameters to tools

Use the `params` field to pass config to a tool function:

```json
{
  "tool_chain": [
    {
      "tool": "route_by_length",
      "params": {
        "threshold": 500,
        "routes": { "short_text": "summarize_short", "long_text": "summarize_long" }
      }
    }
  ]
}
```

The `params` dict is passed as the second argument to the tool function.
