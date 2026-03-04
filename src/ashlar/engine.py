import datetime
import json
import logging
import os
import uuid

from ashlar.builtins import register_builtins
from ashlar.config import get_project_paths, load_project_config
from ashlar.gar import GARInterface
from ashlar.models import WorkflowConfig
from ashlar.prompts import construct_prompt
from ashlar.tools import LocalToolManager

logger = logging.getLogger("ashlar")


def execute_workflow(
    workflow_name: str,
    input_data: str,
    project_dir: str,
    fallback_enabled: bool = True,
) -> dict:
    """Core workflow execution. Called by both CLI and server."""
    paths = get_project_paths(project_dir)
    config = load_project_config(project_dir)

    # Load and validate workflow config
    workflow_file = os.path.join(paths["workflows"], f"{workflow_name}.json")
    if not os.path.exists(workflow_file):
        raise FileNotFoundError(f"Workflow '{workflow_name}' not found at {workflow_file}")

    try:
        with open(workflow_file, "r") as f:
            raw = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Workflow '{workflow_name}' has invalid JSON: {e}") from e

    # Apply project defaults before validation
    if "fallback" not in raw:
        raw["fallback"] = config["defaults"]["fallback"]

    wf = WorkflowConfig(**raw)
    logger.info("Loaded workflow '%s' from %s", workflow_name, workflow_file)

    task_type = wf.task_type
    schema_path = wf.schema_path
    tool_chain = [step.model_dump() for step in wf.tool_chain]
    fallback_policy = wf.fallback
    template_params = wf.template_params

    # Resolve schema path relative to project
    if schema_path:
        schema_path = os.path.join(project_dir, schema_path)

    # Set up tools
    manager = LocalToolManager()
    register_builtins(manager)
    manager.load_project_tools(paths["tools"])

    # Step 1: deterministic preprocessing
    logger.debug("Running tool chain: %s", [s["tool"] for s in tool_chain])
    processed_input = manager.run_tool_chain(input_data, tool_chain)

    # Step 2: optional LLM reasoning
    mcp_config_path = paths["mcp"]
    llm_result = None
    fallback_triggered = False
    if task_type:
        gar = GARInterface(project_dir)
        prompt = construct_prompt(task_type, processed_input, template_params)
        logger.info("Calling LLM with task_type='%s'", task_type)
        logger.debug("Prompt:\n%s", prompt[:500])
        try:
            llm_result = gar.call_gar(prompt, schema_path, mcp_config_path)
            # Confidence check: keys must match schema if provided
            if fallback_enabled and schema_path:
                with open(schema_path, "r") as f:
                    schema = json.load(f)
                required_keys = schema.get("required", [])
                if not all(k in llm_result for k in required_keys):
                    raise ValueError("LLM output missing required keys")
            logger.debug("LLM returned %d keys", len(llm_result) if isinstance(llm_result, dict) else 0)
        except Exception as e:
            fallback_triggered = True
            logger.warning("LLM failed (%s), applying fallback '%s'", e, fallback_policy)
            if fallback_policy == "retry":
                try:
                    llm_result = gar.call_gar(prompt, schema_path, mcp_config_path)
                except Exception as retry_err:
                    logger.error("Retry also failed: %s", retry_err)
                    llm_result = {"error": str(retry_err), "fallback": "retry_exhausted"}
            elif fallback_policy == "deterministic":
                llm_result = {"fallback_output": processed_input}
            elif fallback_policy == "flag":
                llm_result = {"error": str(e), "flagged": True}

    # Step 3: build result
    # User-facing: the final useful answer
    # If LLM ran, that's the result. If tool-only, the preprocessed output is.
    if llm_result is not None:
        result = llm_result
    else:
        result = {"output": processed_input}

    # Step 4: log (full breakdown for debugging)
    logs_dir = paths["logs"]
    os.makedirs(logs_dir, exist_ok=True)
    log_file = os.path.join(logs_dir, f"{uuid.uuid4()}.json")
    log_entry = {
        "workflow": workflow_name,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "input_preview": input_data[:200],
        "task_type": task_type,
        "tool_chain": [s["tool"] for s in tool_chain],
        "fallback_policy": fallback_policy,
        "fallback_triggered": fallback_triggered,
        "preprocessed": processed_input,
        "result": result,
    }
    with open(log_file, "w") as f:
        json.dump(log_entry, f, indent=2)
    logger.debug("Log written to %s", log_file)

    return result
