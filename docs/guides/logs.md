# Reading Logs

Every workflow execution creates a log file in `logs/`. Each file is named with a UUID and contains the full execution record.

## View recent logs

```bash
kerf logs
```

```json
{
  "workflow": "summarize",
  "timestamp": "2025-01-15T14:32:01+00:00",
  "input_preview": "The quarterly earnings report showed...",
  "task_type": "summarization",
  "tool_chain": ["normalize_text"],
  "fallback_policy": "retry",
  "fallback_triggered": false,
  "preprocessed": "the quarterly earnings report showed...",
  "result": { "summary": "..." }
}
```

## Filter and limit

```bash
kerf logs --last 5                  # show 5 most recent
kerf logs --workflow summarize      # filter by workflow name
kerf logs --last 3 --workflow classify
```

## Log format

Each log file is a JSON object:

| Field | Description |
|---|---|
| `workflow` | Name of the workflow that ran |
| `timestamp` | ISO 8601 UTC timestamp |
| `input_preview` | First 200 characters of the raw input |
| `task_type` | Prompt template used (or `null` for tool-only workflows) |
| `tool_chain` | List of tool names that ran in the preprocessing step |
| `fallback_policy` | Which fallback policy was configured |
| `fallback_triggered` | `true` if the LLM call failed and fallback was used |
| `preprocessed` | Output after the tool chain ran (before LLM) |
| `result` | The final result returned to the user |

## Why logging matters

Logs are how you move away from LLM dependence. The workflow:

1. Run a workflow against real inputs
2. Read the logs. Look at what the LLM actually returned
3. Spot the pattern. Does it always do the same transformation?
4. Write a tool that does the same thing deterministically
5. Remove the `task_type` from the workflow. No more LLM call

The LLM is scaffolding. The logs are how you learn to remove it.
