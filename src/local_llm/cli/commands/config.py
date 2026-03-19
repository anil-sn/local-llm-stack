"""
Configuration commands for Local LLM Stack CLI.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table
from rich import box

from local_llm.config import get_config

app = typer.Typer(help="View and edit configuration")
console = Console()


@app.callback(invoke_without_command=True)
def config_main(
    ctx: typer.Context,
) -> None:
    """
    Show current configuration.
    
    If no subcommand is given, shows the full config.
    
    Examples:
    
        # Show all configuration
        $ llm-stack config
        
        # Show server section
        $ llm-stack config show server
    """
    if ctx.invoked_subcommand is None:
        # Call show_config by default
        show_config()


@app.command("show")
def show_config(
    section: Optional[str] = typer.Argument(
        None,
        help="Show specific section (server, models, api, etc.)",
    ),
    raw: bool = typer.Option(
        False,
        "--raw",
        "-r",
        help="Show raw YAML",
    ),
) -> None:
    """
    Show current configuration.
    
    Examples:
    
        # Show all configuration
        $ llm-stack config show
    
        # Show server section only
        $ llm-stack config show server
    
        # Show raw YAML
        $ llm-stack config show --raw
    """
    config = get_config()
    
    if raw:
        # Show raw YAML
        config_path = Path(config._config_path)
        if config_path.exists():
            content = config_path.read_text()
            console.print(Syntax(content, "yaml", theme="monokai", line_numbers=True))
        else:
            console.print("[red]❌ Config file not found[/red]")
            raise typer.Exit(1)
    else:
        # Show formatted configuration
        if section:
            value = config.get(section)
            if value is None:
                console.print(f"[red]❌ Section not found: {section}[/red]")
                raise typer.Exit(1)
            
            console.print(f"[bold]Configuration: {section}[/bold]")
            console.print()
            
            if isinstance(value, dict):
                table = Table(box=box.SIMPLE, show_header=False)
                table.add_column("Key", style="cyan")
                table.add_column("Value", style="white")
                
                for k, v in value.items():
                    table.add_row(k, str(v))
                
                console.print(table)
            else:
                console.print(f"[bold]{section}:[/bold] {value}")
        else:
            # Show summary
            console.print("[bold]📋 Configuration Summary[/bold]")
            console.print()
            
            table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
            table.add_column("Section", style="cyan")
            table.add_column("Key", style="white")
            table.add_column("Value", style="green")
            
            # Active model
            table.add_row("model", "active_model", config.active_model_key)
            table.add_row("model", "model_name", config.active_model_name)
            table.add_row("model", "model_path", config.model_path)
            
            # Server
            table.add_row("server", "port", str(config.server_port))
            table.add_row("server", "host", config.server_host)
            table.add_row("server", "context_size", str(config.context_size))
            table.add_row("server", "gpu_layers", str(config.gpu_layers))
            
            # API
            table.add_row("api", "base_url", config.api_base_url)
            table.add_row("api", "key", config.api_key)
            
            # Advanced
            table.add_row("advanced", "temperature", str(config.temperature))
            table.add_row("advanced", "top_p", str(config.top_p))
            table.add_row("advanced", "repeat_penalty", str(config.repeat_penalty))
            
            console.print(table)
            console.print()
            console.print("[dim]Use 'llm-stack config show <section>' for details[/dim]")


@app.command("edit")
def edit_config() -> None:
    """
    Edit configuration file.
    
    Opens the config.yaml file in your default editor ($EDITOR).
    
    Examples:
    
        # Edit configuration
        $ llm-stack config edit
    """
    config = get_config()
    config_path = Path(config._config_path)
    
    if not config_path.exists():
        console.print("[red]❌ Config file not found[/red]")
        console.print(f"   Expected: {config_path}")
        raise typer.Exit(1)
    
    # Get editor from environment
    editor = os.environ.get("EDITOR", "nano")
    
    console.print(f"[bold]Editing: {config_path}[/bold]")
    console.print(f"[dim]Editor: {editor}[/dim]")
    console.print()
    
    try:
        subprocess.run([editor, str(config_path)], check=True)
        console.print()
        console.print("[green]✅ Configuration saved[/green]")
    except FileNotFoundError:
        console.print(f"[red]❌ Editor not found: {editor}[/red]")
        console.print()
        console.print("Set EDITOR environment variable:")
        console.print("  [bold]export EDITOR=nano[/bold]")
        raise typer.Exit(1)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Editor exited with error: {e}[/red]")
        raise typer.Exit(1)


@app.command("validate")
def validate_config() -> None:
    """
    Validate configuration file.
    
    Checks YAML syntax and validates required fields.
    
    Examples:
    
        # Validate configuration
        $ llm-stack config validate
    """
    config = get_config()
    config_path = Path(config._config_path)
    
    console.print("[bold]🔍 Validating configuration[/bold]")
    console.print(f"Path: {config_path}")
    console.print()
    
    # Check file exists
    if not config_path.exists():
        console.print(f"[red]❌ Config file not found[/red]")
        raise typer.Exit(1)
    
    console.print("[green]✅ File exists[/green]")
    
    # Check YAML syntax
    try:
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
        console.print("[green]✅ Valid YAML syntax[/green]")
    except yaml.YAMLError as e:
        console.print(f"[red]❌ Invalid YAML: {e}[/red]")
        raise typer.Exit(1)
    
    # Check required fields
    required_fields = ["active_model", "models", "server", "api"]
    
    for field in required_fields:
        if field not in data:
            console.print(f"[red]❌ Missing required field: {field}[/red]")
            raise typer.Exit(1)
    
    console.print("[green]✅ All required fields present[/green]")
    
    # Check active model exists
    active_model = data.get("active_model")
    models = data.get("models", {})
    
    if active_model not in models:
        console.print(f"[red]❌ Active model '{active_model}' not found in models[/red]")
        raise typer.Exit(1)
    
    console.print(f"[green]✅ Active model '{active_model}' configured[/green]")
    
    # Check model paths
    console.print()
    console.print("[bold]Model Files:[/bold]")
    
    for model_key, model_config in models.items():
        model_path = model_config.get("path", "")
        if model_path:
            # Expand path
            model_path = os.path.expanduser(model_path)
            model_path = os.path.expandvars(model_path)
            
            exists = os.path.isfile(model_path)
            status = "[green]✅[/green]" if exists else "[yellow]❌[/yellow]"
            console.print(f"  {status} {model_key}: {model_path}")
    
    console.print()
    console.print("[bold green]✅ Configuration is valid[/bold green]")


@app.command("models")
def list_model_configs() -> None:
    """
    List all configured models.
    
    Shows model keys, names, and whether files exist.
    
    Examples:
    
        # List all models
        $ llm-stack config models
    """
    config = get_config()
    
    console.print("[bold]📦 Configured Models[/bold]")
    console.print()
    
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Key", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Size", justify="right")
    table.add_column("RAM", justify="right")
    table.add_column("Exists", justify="center")
    
    for model_key in config.available_models:
        info = config.get_model_info(model_key)
        is_active = model_key == config.active_model_key
        
        name = info["name"]
        if is_active:
            name = f"[bold green]⭐ {name}[/bold green]"
        
        exists = os.path.isfile(info["path"])
        exists_str = "[green]✅[/green]" if exists else "[dim]❌[/dim]"
        
        table.add_row(
            model_key,
            name,
            f"{info['size_gb']} GB",
            f"{info['ram_required_gb']} GB",
            exists_str,
        )
    
    console.print(table)
    console.print()
    console.print(f"[dim]⭐ = Active model[/dim]")
