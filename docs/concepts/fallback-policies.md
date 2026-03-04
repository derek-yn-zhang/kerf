# Fallback Policies

Each workflow declares how much it trusts the LLM. The `fallback` field controls what happens when the LLM call fails or returns output that doesn't match the schema.

## Policies

| Policy | What happens | When to use it |
|---|---|---|
| `retry` | Call the LLM again | Tasks like summarization where there's no good deterministic alternative — just try again |
| `deterministic` | Skip the LLM, return the preprocessed output | Tasks like classification where the LLM is flaky — fall back to whatever the tool chain produced |
| `flag` | Return the error in the output | Ambiguous cases — log the failure, deal with it later |

## When fallback triggers

Fallback triggers in two situations:

1. **The LLM call fails** — Claude CLI returns a non-zero exit code, or the output isn't valid JSON
2. **Schema validation fails** — the LLM returned JSON, but it's missing required keys defined in `schema_path`

The schema check is the confidence gate. If you asked the LLM to return `{"category": "..."}` and it returned `{"label": "..."}`, it didn't follow instructions. The fallback kicks in.

## Choosing a policy

The right policy depends on whether a deterministic alternative exists:

- **Summarization** has no good deterministic fallback. If the LLM fails, `retry` is the best option.
- **Classification** often has a rules-based fallback. Use `deterministic` to degrade gracefully.
- **Ambiguous extractions** where you're not sure what the right answer is — use `flag` to log the failure and review manually.

The policy is per-workflow, so you tune trust on a per-task basis. A workflow that's been running reliably for weeks might use `retry`. A new workflow you're still tuning might use `flag` until you've seen enough logs to trust it.
