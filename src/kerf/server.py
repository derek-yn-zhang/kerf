from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from kerf.config import find_project_root, load_project_config
from kerf.engine import execute_workflow

app = FastAPI(title="Kerf")


class WorkflowRequest(BaseModel):
    workflow_name: str
    input_data: str
    fallback_enabled: bool = True


@app.post("/execute")
def run_workflow(request: WorkflowRequest):
    project_dir = find_project_root()
    try:
        return execute_workflow(
            workflow_name=request.workflow_name,
            input_data=request.input_data,
            project_dir=project_dir,
            fallback_enabled=request.fallback_enabled,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


def run_server(host: str = None, port: int = None):
    import uvicorn

    project_dir = find_project_root()
    config = load_project_config(project_dir)
    host = host or config["server"]["host"]
    port = port or config["server"]["port"]
    uvicorn.run(app, host=host, port=port)
