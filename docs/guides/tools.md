# Writing Tools

Tools are deterministic Python functions that run before (or instead of) the LLM. They go in your project's `tools/` directory.

## Create a tool

```bash
ashlar add tool strip-html
```

Edit the generated file:

```python
# tools/strip-html.py
import re

def strip_html(input_data, params):
    return re.sub(r"<[^>]+>", "", input_data)

def register(manager):
    manager.register_tool("strip-html", strip_html)
```

The file name can use hyphens, and so can the registered tool name. The Python function name uses underscores (since hyphens aren't valid in Python identifiers). `ashlar add tool` handles this automatically.

Use it in a workflow:

```json
{
  "tool_chain": [
    { "tool": "strip-html" },
    { "tool": "normalize_text" }
  ],
  "task_type": "summarization",
  "fallback": "retry"
}
```

## How discovery works

On every workflow execution, Ashlar scans `tools/` for `.py` files. Any file that defines a `register(manager)` function gets loaded. The function receives a `LocalToolManager` and calls `register_tool()` or `register_condition()` on it.

- Files starting with `_` are skipped (use `_helpers.py` for shared utilities)
- Built-in tools load first, then user tools — you can override builtins (logged as a warning)
- Files without a `register` function are warned and skipped
- Files with syntax errors or import failures are logged and skipped — one broken file won't stop the rest from loading

## Tool function signature

```python
def my_tool(input_data, params):
    # input_data: output of the previous step, or raw input for the first step
    # params: dict from the workflow's tool_chain step config
    return processed_data
```

Tools must accept at least 2 parameters. Registration raises `TypeError` if they don't.

Tools receive data from the previous step and return data for the next step. The chain is sequential — each tool's output becomes the next tool's input.

## Writing conditions

Conditions control whether a tool step runs. Register them alongside tools:

```python
# tools/conditions.py

def is_english(context):
    last = context.get("last_output", "")
    # simple heuristic
    return isinstance(last, str) and last.isascii()

def register(manager):
    manager.register_condition("is_english", is_english)
```

Conditions receive a `context` dict that includes `last_output` from the previous step. Return `True` to run the step, `False` to skip it.

Use in a workflow:

```json
{ "tool": "english_only_processing", "condition": "is_english" }
```

## Using third-party libraries

Tool files can import anything. The only requirement is the `register` function:

```python
# tools/sentiment.py
from textblob import TextBlob

def sentiment_score(input_data, params):
    blob = TextBlob(input_data)
    return {"text": input_data, "polarity": blob.sentiment.polarity}

def register(manager):
    manager.register_tool("sentiment_score", sentiment_score)
```

Make sure the library is installed in the same environment as Ashlar.
