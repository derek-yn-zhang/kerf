import importlib.util
import inspect
import logging
import os
from typing import Any, Callable, Dict, List

logger = logging.getLogger("ashlar")


class LocalToolManager:
    def __init__(self):
        self.tools: Dict[str, Callable[[Any, Dict[str, Any]], Any]] = {}
        self.conditions: Dict[str, Callable[[Dict[str, Any]], bool]] = {}

    def register_tool(self, name: str, func: Callable[[Any, Dict[str, Any]], Any]):
        sig = inspect.signature(func)
        if len(sig.parameters) < 2:
            raise TypeError(
                f"Tool '{name}' must accept (input_data, params), "
                f"got {len(sig.parameters)} parameter(s)."
            )
        if name in self.tools:
            logger.warning("Tool '%s' already registered; overriding.", name)
        self.tools[name] = func

    def register_condition(self, name: str, func: Callable[[Dict[str, Any]], bool]):
        if name in self.conditions:
            logger.warning("Condition '%s' already registered; overriding.", name)
        self.conditions[name] = func

    def run_tool_chain(
        self,
        input_data: Any,
        chain: List[Dict[str, Any]],
        context: Dict[str, Any] = None,
    ) -> Any:
        context = context or {}
        data = input_data
        for step in chain:
            tool_name = step["tool"]
            condition_name = step.get("condition", "always_true")
            params = step.get("params", {})

            if condition_name not in self.conditions:
                raise ValueError(f"Condition '{condition_name}' not registered.")
            if tool_name not in self.tools:
                raise ValueError(f"Tool '{tool_name}' not registered.")

            if self.conditions[condition_name](context):
                logger.debug("Running tool '%s' (condition: %s)", tool_name, condition_name)
                data = self.tools[tool_name](data, params)
                context.update({"last_output": data})
            else:
                logger.debug("Skipping tool '%s' (condition '%s' was false)", tool_name, condition_name)
        return data

    def load_project_tools(self, tools_dir: str):
        """Load all tools from .py files in the project's tools/ directory.

        Each file that defines a register(manager) function gets loaded.
        The register function receives this LocalToolManager instance.
        Files with errors are logged and skipped.
        """
        if not os.path.isdir(tools_dir):
            return
        for filename in sorted(os.listdir(tools_dir)):
            if not filename.endswith(".py") or filename.startswith("_"):
                continue
            filepath = os.path.join(tools_dir, filename)
            try:
                spec = importlib.util.spec_from_file_location(
                    f"ashlar_user_tools.{filename[:-3]}", filepath
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, "register"):
                    module.register(self)
                    logger.debug("Loaded tools from '%s'", filename)
                else:
                    logger.warning("Tool file '%s' has no register() function; skipping.", filename)
            except Exception as e:
                logger.error("Failed to load tool '%s': %s", filename, e)
