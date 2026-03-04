# How the Engine Works

Ashlar is a thin orchestration layer over the Claude CLI. It doesn't embed a model, manage API keys, or do anything clever with tokens. It wraps `claude -p --output-format json` in a structured pipeline and adds the scaffolding to make LLM calls reproducible, validatable, and replaceable.

## Pipeline

Every workflow execution follows the same sequence:

```
input_data
  |
  v
[tool_chain: deterministic preprocessing]
  |
  v
[LLM call via Claude CLI (optional)]
  |
  v
[schema validation → fallback if needed]
  |
  v
result (LLM output or tool output)
  |
  v
[logged to logs/<uuid>.json]
```

1. Load workflow config from `workflows/<name>.json`
2. Set up the tool manager — register builtins, then load user tools from `tools/`
3. Run the deterministic tool chain on the input
4. If `task_type` is set, construct a prompt and call the LLM via Claude CLI
5. If a `schema_path` is set, validate the LLM output — check that all required keys are present
6. On validation failure, apply the fallback policy
7. Log the full result to `logs/<uuid>.json`

## Components

**GARInterface** wraps the Claude CLI's headless mode (GAR = Generate, Analyze, Return). It checks that `claude` is on your PATH, calls `claude -p <prompt> --output-format json`, and parses the JSON response. Claude CLI handles its own authentication — Ashlar doesn't manage credentials.

**LocalToolManager** is a registry for deterministic tools and named conditions. Tools and conditions are registered by name (strings), not as lambdas. The workflow JSON references these names, and the manager resolves them at runtime. This is what keeps workflows fully serializable.

**Engine** is the `execute_workflow()` function that ties it together. Both `ashlar run` and `POST /execute` call the same function — there's no separate CLI vs server path.

## Tool resolution order

1. Built-in tools and conditions register first (`normalize_text`, `route_by_length`, `always_true`)
2. User tools from `tools/` register second
3. User tools can override builtins by registering the same name

## Project detection

Ashlar walks up from the current working directory looking for a `.ashlar` marker file, the same way git looks for `.git/`. This means you can run `ashlar run` from any subdirectory of your project.
