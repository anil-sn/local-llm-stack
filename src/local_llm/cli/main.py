"""
Local LLM Stack CLI - Main Entry Point

A unified command-line interface for managing local LLM inference.
"""

import typer
from typing import Optional

from local_llm import __version__
from local_llm.cli.commands import server, model, chat, benchmark, config, status


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        typer.echo(f"Local LLM Stack CLI version {__version__}")
        raise typer.Exit()


def create_app() -> typer.Typer:
    """Create and configure the CLI application."""
    app = typer.Typer(
        name="llm-stack",
        help="Local LLM Stack - Professional CLI for managing local LLM inference",
        add_completion=True,
        rich_markup_mode="rich",
    )
    
    # Register command groups
    app.add_typer(server.app, name="server", help="Manage the LLM server")
    app.add_typer(model.app, name="model", help="Manage models")
    app.add_typer(chat.app, name="chat", help="Chat with the LLM")
    app.add_typer(benchmark.app, name="benchmark", help="Run benchmarks")
    app.add_typer(config.app, name="config", help="View and edit configuration")
    app.add_typer(status.app, name="status", help="Check system and server status")
    
    return app


app = create_app()


@app.callback()
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """
    [bold]Local LLM Stack CLI[/bold]
    
    A unified command-line interface for managing local LLM inference.
    Supports Qwen, Llama, Mistral, Gemma, Phi and other models.
    
    [bold]Quick Start:[/bold]
    
      # Check system status
      $ llm-stack status
    
      # Start the server
      $ llm-stack server start
    
      # Chat with the model
      $ llm-stack chat
    
      # Run benchmarks
      $ llm-stack benchmark run
    
    Use [bold]llm-stack [command] --help[/bold] for more information on a specific command.
    """
    pass


if __name__ == "__main__":
    app()
