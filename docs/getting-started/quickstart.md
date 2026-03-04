# Quickstart

This walks through scaffolding a project, running a workflow, and reading the output. Takes about 2 minutes.

## Prerequisites

Kerf calls [Claude Code](https://docs.anthropic.com/en/docs/claude-code) under the hood. Make sure it's installed and authenticated:

```bash
claude --version
```

If that fails, [install Claude Code](https://docs.anthropic.com/en/docs/claude-code) first. Then authenticate:

```bash
claude login
```

If `kerf run` fails with `"Claude CLI not found on PATH"`, you need to install Claude Code first.

## Create a project

```bash
mkdir my-pipeline && cd my-pipeline
kerf init
```

This creates the standard project structure with example workflows. See [Project Structure](project-structure.md) for details.

## Run the example workflows

The scaffolded project includes `summarize`, `classify`, `extract`, `clean`, and `digest` workflows:

```bash
kerf run summarize "The quarterly earnings report showed revenue growth of 15%, driven by enterprise expansion and strong retention."
```

```json
{
  "summary": "Quarterly revenue grew 15% YoY, driven by enterprise expansion and strong retention."
}
```

```bash
kerf run classify "The login page crashes when I enter my email with a + sign"
```

```json
{
  "category": "bug",
  "confidence": "high"
}
```

```bash
kerf run extract "Hi, I'm Sarah Chen (sarah@acme.co), VP of Engineering at Acme Corp."
```

```json
{
  "name": "Sarah Chen",
  "email": "sarah@acme.co",
  "company": "Acme Corp",
  "role": "VP of Engineering"
}
```

The `digest` workflow chains multiple tools before calling the LLM, stripping HTML, normalizing whitespace, and truncating long input before summarizing:

```bash
kerf run digest "<div><h2>Mantis Shrimp</h2><p>Mantis shrimp are   carnivorous marine crustaceans   of the order <em>Stomatopoda</em>,   branching off from other crustaceans   around <strong>400 million years ago</strong>.   Their raptorial claws   can accelerate   at a rate comparable to   a .22 caliber bullet,   delivering around   1,500 newtons of force   per strike.</p><p>They are thought   to have   the most complex eyes   in the animal kingdom,   perceiving wavelengths   from deep ultraviolet   to far-red   with up to   16 distinct photoreceptors.</p></div>"
```

```json
{
  "summary": "Mantis shrimp are 400-million-year-old marine crustaceans with bullet-fast claws delivering 1,500 newtons of force and the most complex eyes in the animal kingdom, with 16 photoreceptors spanning ultraviolet to far-red."
}
```

You can also pipe input from stdin:

```bash
cat article.txt | kerf run summarize
```

## Check the logs

```bash
kerf logs --last 1
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

Every execution is logged with a UUID filename in `logs/`. The user-facing output is just the `result`. The log captures the full pipeline breakdown for debugging and pattern extraction.

## What's next

- [Writing Workflows](../guides/workflows.md): create your own pipelines
- [Writing Tools](../guides/tools.md): add custom preprocessing steps
- [Reading Logs](../guides/logs.md): audit execution results and extract patterns
- [Using the API Server](../guides/server.md): run workflows over HTTP
