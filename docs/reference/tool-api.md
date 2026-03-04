# Tool API

## Tool function

```python
def my_tool(input_data: Any, params: dict) -> Any:
```

| Parameter | Description |
|---|---|
| `input_data` | Output of the previous step, or raw input for the first step |
| `params` | Dict from the workflow step's `params` field |
| Return | Processed data, becomes `input_data` for the next step |

## Condition function

```python
def my_condition(context: dict) -> bool:
```

| Parameter | Description |
|---|---|
| `context` | Dict containing `last_output` from the previous step |
| Return | `True` to run the step, `False` to skip it |

## Registration

Every tool file must define a `register` function:

```python
def register(manager: LocalToolManager):
    manager.register_tool("tool_name", tool_function)
    manager.register_condition("condition_name", condition_function)
```

### `manager.register_tool(name, func)`

Register a tool function under the given name. The name is what workflow JSON files reference.

### `manager.register_condition(name, func)`

Register a condition function under the given name.

### `manager.run_tool_chain(input_data, chain, context=None)`

Execute a sequence of tool steps. Called internally by the engine. You generally don't call this directly.

### `manager.load_project_tools(tools_dir)`

Discover and load all tool files from a directory. Called internally by the engine.

## File discovery rules

- Scans `tools/` for `.py` files
- Files starting with `_` are skipped
- Files without a `register` function are warned and skipped
- Files with import errors or exceptions during loading are logged and skipped. One bad file doesn't break everything
- Built-in tools load first, then user tools
- User tools can override builtins by registering the same name (logged as a warning)

## Validation

Tool functions must accept at least 2 parameters (`input_data`, `params`). Registration will raise `TypeError` if the signature doesn't match.

Condition and tool names must be registered before the tool chain runs. Missing names raise `ValueError` with a clear message.
