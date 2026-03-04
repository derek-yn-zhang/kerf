from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, field_validator

VALID_TASK_TYPES = {"summarization", "structured_extraction", "classification"}


class ToolChainStep(BaseModel):
    tool: str
    condition: str = "always_true"
    params: Dict[str, Any] = {}


class WorkflowConfig(BaseModel):
    task_type: Optional[str] = None
    schema_path: Optional[str] = None
    tool_chain: List[ToolChainStep] = []
    fallback: Literal["retry", "deterministic", "flag"] = "retry"
    template_params: Dict[str, Any] = {}

    @field_validator("task_type")
    @classmethod
    def validate_task_type(cls, v):
        if v is not None and v not in VALID_TASK_TYPES:
            raise ValueError(
                f"Unknown task_type '{v}'. Valid: {sorted(VALID_TASK_TYPES)}"
            )
        return v


class KerfConfig(BaseModel):
    class ServerConfig(BaseModel):
        host: str = "0.0.0.0"
        port: int = 8000

    class DefaultsConfig(BaseModel):
        fallback: Literal["retry", "deterministic", "flag"] = "retry"

    server: ServerConfig = ServerConfig()
    defaults: DefaultsConfig = DefaultsConfig()
