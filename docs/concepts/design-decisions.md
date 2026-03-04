# Design Decisions

## Why subprocess, not SDK?

Kerf shells out to the Claude CLI (`claude -p`) rather than using Anthropic's Python SDK. This means:

- It works with whatever authentication the CLI provides, including Max Plan
- No API keys to manage
- No dependency on Anthropic's SDK versioning
- The CLI handles model selection, rate limiting, and context management

The tradeoff is latency. Spawning a subprocess is slower than an HTTP call, but the LLM call itself dominates the total time, so the subprocess overhead is negligible.

## Why sync, not async?

The engine is synchronous. `subprocess.run` and file I/O are blocking operations. There's no benefit to async here. The bottleneck is the LLM call, and you can't parallelize a single CLI invocation.

The FastAPI server handles concurrency at the request level. When you define the endpoint as a regular `def` (not `async def`), FastAPI runs each request in a thread pool automatically.

## Why named conditions instead of expressions?

Workflow files are JSON. If conditions were inline expressions like `"len(input) > 500"`, you'd need either an expression parser or `eval()`. Both are worse than a simple name-to-function registry:

- `eval()` is a security risk
- Expression parsers add complexity for marginal benefit
- Named conditions are explicit, debuggable, and inspectable
- You can set breakpoints in condition functions

The cost is that you have to write a Python function and register it. The benefit is that your workflow files stay data. No code in config.

## Why JSON workflows, not Python?

Python workflow definitions would be more expressive, but JSON workflows are:

- Editable by anyone, even people who don't write Python
- Serializable and transferable: you can store them in a database, send them over HTTP, version them in git
- Inspectable: `kerf list` can read them without importing any code
- Constrained: they can't do anything surprising

The tool chain is where Python lives. The workflow file is where configuration lives. Keeping them separate means you can change pipeline behavior without touching code.
