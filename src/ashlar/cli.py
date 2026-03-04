import json
import logging
import os
import sys

import click

from ashlar.config import find_project_root, get_project_paths


@click.group()
def cli():
    """Ashlar — declarative workflow engine where the LLM is a pluggable, disposable step."""
    pass


@cli.command()
def init():
    """Scaffold a new ashlar project in the current directory."""
    from ashlar.scaffold import scaffold_project

    try:
        scaffold_project(os.getcwd())
        click.echo("Ashlar project initialized.")
    except FileExistsError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("workflow")
@click.argument("input_data", required=False)
@click.option("--debug", is_flag=True, help="Show debug output")
def run(workflow, input_data, debug):
    """Execute a workflow. Input can be an argument or piped via stdin."""
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.WARNING,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    if input_data is None:
        if not sys.stdin.isatty():
            input_data = sys.stdin.read()
        else:
            click.echo("Error: provide input as an argument or pipe via stdin.", err=True)
            sys.exit(1)

    from ashlar.engine import execute_workflow

    project_dir = find_project_root()
    try:
        result = execute_workflow(
            workflow_name=workflow,
            input_data=input_data,
            project_dir=project_dir,
        )
        click.echo(json.dumps(result, indent=2))
    except (ValueError, FileNotFoundError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        if debug or os.environ.get("ASHLAR_DEBUG"):
            import traceback

            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option("--host", default=None, help="Server host")
@click.option("--port", default=None, type=int, help="Server port")
def serve(host, port):
    """Start the Ashlar API server."""
    from ashlar.server import run_server

    run_server(host=host, port=port)


@cli.group()
def add():
    """Add a new workflow, tool, or MCP config."""
    pass


@add.command("workflow")
@click.argument("name")
def add_workflow(name):
    """Scaffold a new workflow JSON file."""
    from ashlar.scaffold import scaffold_workflow

    project_dir = find_project_root()
    try:
        scaffold_workflow(name, project_dir)
        click.echo(f"Created workflows/{name}.json")
    except FileExistsError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@add.command("tool")
@click.argument("name")
def add_tool(name):
    """Scaffold a new deterministic tool."""
    from ashlar.scaffold import scaffold_tool

    project_dir = find_project_root()
    try:
        scaffold_tool(name, project_dir)
        click.echo(f"Created tools/{name}.py")
    except FileExistsError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@add.command("mcp")
@click.argument("name")
def add_mcp(name):
    """Add an MCP server entry to mcp.json."""
    from ashlar.scaffold import scaffold_mcp

    project_dir = find_project_root()
    try:
        scaffold_mcp(name, project_dir)
        click.echo(f"Added MCP config for '{name}' to mcp.json")
    except FileExistsError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--last", default=10, type=int, help="Number of recent logs to show")
@click.option("--workflow", "wf_filter", default=None, help="Filter by workflow name")
def logs(last, wf_filter):
    """View recent execution logs."""
    project_dir = find_project_root()
    paths = get_project_paths(project_dir)
    logs_dir = paths["logs"]

    if not os.path.isdir(logs_dir):
        click.echo("No logs found.")
        return

    log_files = sorted(
        [f for f in os.listdir(logs_dir) if f.endswith(".json")],
        key=lambda f: os.path.getmtime(os.path.join(logs_dir, f)),
        reverse=True,
    )

    shown = 0
    for filename in log_files:
        if shown >= last:
            break
        filepath = os.path.join(logs_dir, filename)
        with open(filepath, "r") as f:
            entry = json.load(f)
        if wf_filter and entry.get("workflow") != wf_filter:
            continue
        click.echo(f"\n--- {filename} ---")
        click.echo(json.dumps(entry, indent=2))
        shown += 1

    if shown == 0:
        click.echo("No matching logs found.")



@cli.command("list")
def list_resources():
    """List available workflows and tools."""
    project_dir = find_project_root()
    paths = get_project_paths(project_dir)

    # Workflows
    wf_dir = paths["workflows"]
    click.echo("Workflows:")
    if os.path.isdir(wf_dir):
        workflows = [f[:-5] for f in sorted(os.listdir(wf_dir)) if f.endswith(".json")]
        for w in workflows:
            click.echo(f"  {w}")
        if not workflows:
            click.echo("  (none)")
    else:
        click.echo("  (no workflows/ directory)")

    # Tools
    tools_dir = paths["tools"]
    click.echo("\nTools:")
    if os.path.isdir(tools_dir):
        tool_files = [
            f[:-3]
            for f in sorted(os.listdir(tools_dir))
            if f.endswith(".py") and not f.startswith("_")
        ]
        for t in tool_files:
            click.echo(f"  {t}")
        if not tool_files:
            click.echo("  (none)")
    else:
        click.echo("  (no tools/ directory)")
