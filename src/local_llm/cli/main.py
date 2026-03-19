"""
Local LLM Stack CLI - Main Entry Point

A unified command-line interface for managing local LLM inference.
"""

import typer
from typing import Optional

from local_llm import __version__
from local_llm.cli.commands import server, model, chat, benchmark, config, status, run


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
    
    # Register run command directly
    app.command("run")(run.run_model)
    
    # Add alias: models -> model (for convenience)
    app.add_typer(model.app, name="models", help="Manage models (alias)", hidden=True)

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
    Supports Qwen, Llama, Mistral, Gemma, Phi and 10+ other models.
    
    Auto-detects hardware and optimizes settings for your GPU.

    [bold]Quick Start:[/bold]

      # Download and run any model (recommended)
      $ llm-stack run llama-3-8b --chat

      # Run with HuggingFace reference
      $ llm-stack run unsloth/Qwen3.5-9B-GGUF:Q4_K_M --webui

      # Check system status
      $ llm-stack status

      # Get model recommendations
      $ llm-stack model recommend

    Use [bold]llm-stack [command] --help[/bold] for more information.
    """
    pass


if __name__ == "__main__":
    app()
