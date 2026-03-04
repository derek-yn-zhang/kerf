# Project Structure

After running `kerf init`, your project looks like this:

```
my-pipeline/
  .kerf                  # project marker
  workflows/
    summarize.json         # summarization example
    classify.json          # classification example
    extract.json           # structured extraction example
  schemas/
  tools/                   # your custom tool files go here
  logs/
  kerf.toml              # project config
```

## Directories

**`workflows/`** — JSON files that define pipelines. Each file is a workflow you can run by name. See [Workflow Format](../reference/workflow-format.md).

**`tools/`** — Python files with deterministic tool functions. Any `.py` file that exports a `register(manager)` function gets auto-loaded. See [Writing Tools](../guides/tools.md).

**`schemas/`** — JSON schema files for validating LLM output. Referenced by `schema_path` in workflow configs.

**`logs/`** — Execution logs. Each run creates a UUID-stamped JSON file with the full input/output record.

## Files

**`.kerf`** — Marker file that identifies the project root. Kerf walks up from your current directory looking for this file (like `.git`), so you can run commands from subdirectories.

**`kerf.toml`** — Optional project-level configuration:

```toml
# [server]
# host = "0.0.0.0"
# port = 8000

# [defaults]
# fallback = "retry"
```
