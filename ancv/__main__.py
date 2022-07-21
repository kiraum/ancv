"""Render JSON resumes to rich ANSI text for terminal output.

Comes with a server serving either an API or a single file, and a CLI to render files
locally.
"""

import json
from pathlib import Path
from typing import Optional

import typer
from pydantic import ValidationError

import ancv.web.server
from ancv.data.models.resume import ResumeSchema
from ancv.visualization.templates import Template

app = typer.Typer(no_args_is_help=True, help=__doc__)
server_app = typer.Typer(no_args_is_help=True, help="Interacts with the web server.")

app.add_typer(server_app, name="serve")


@server_app.command()
def api(
    host: str = typer.Argument("0.0.0.0", help="Hostname to bind to."),
    port: int = typer.Argument(8080, help="Port to bind to."),
    path: Optional[str] = typer.Argument(
        None, help="File system path for an HTTP server UNIX domain socket."
    ),
) -> None:
    """Starts the web server and serves the API."""

    ancv.web.server.run(host=host, port=port, path=path)


@app.command()
def render(
    path: Path = typer.Argument(
        Path("resume.json"),
        help="File path to the JSON resume file.",
    )
) -> None:
    """Locally renders the JSON resume at the given file path."""

    with open(path, "r", encoding="utf8") as file:
        contents = json.loads(file.read())

    resume = ResumeSchema(**contents)
    template = Template.from_model_config(resume)
    output = template.render()
    print(output)
    return None


@app.command()
def validate(
    path: Path = typer.Argument(
        Path("resume.json"),
        help="File path to the JSON resume file.",
    )
) -> None:
    """Checks the validity of the given JSON resume without rendering."""

    with open(path, "r", encoding="utf8") as file:
        contents = json.loads(file.read())

    try:
        ResumeSchema(**contents)
    except ValidationError as e:
        print(str(e))
        raise typer.Exit(code=1)
    else:
        print("Pass!")


if __name__ == "__main__":
    app()
