"""
Model management commands for Local LLM Stack CLI.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, DownloadColumn
from rich import box

from local_llm.config import Config, get_config
from local_llm.utils import (
    check_command_exists,
    expand_path,
    format_size,
    get_total_ram_gb,
    get_disk_usage,
)

app = typer.Typer(help="Manage models")
console = Console()


@app.command("list")
def list_models(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed information",
    ),
) -> None:
    """
    List all available models in configuration.
    
    Shows model name, size, RAM requirements, and whether the file exists locally.
    
    Examples:
    
        # List all models
        $ llm-stack model list
    
        # Show detailed information
        $ llm-stack model list --verbose
    """
    config = get_config()
    models = config.available_models
    active_model = config.active_model_key
    
    if not models:
        console.print("[yellow]⚠️  No models configured in config.yaml[/yellow]")
        return
    
    table = Table(
        title="📦 Available Models",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )
    
    # Add columns
    table.add_column("Model", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Size", justify="right")
    table.add_column("RAM", justify="right")
    
    if verbose:
        table.add_column("Description", style="dim")
    
    table.add_column("Status", justify="center")
    
    # Add rows
    for model_key in models:
        model_info = config.get_model_info(model_key)
        is_active = model_key == active_model
        exists = os.path.isfile(model_info["path"])
        
        status = "✅" if exists else "❌"
        if is_active:
            status = "⭐ " + status
        
        name = model_info["name"]
        if is_active:
            name = f"[bold green]{name}[/bold green]"
        
        row = [
            model_key,
            name,
            f"{model_info['size_gb']} GB",
            f"{model_info['ram_required_gb']} GB",
        ]
        
        if verbose:
            row.append(model_info["description"][:50] + "..." if len(model_info["description"]) > 50 else model_info["description"])
        
        row.append(status)
        table.add_row(*row)
    
    console.print()
    console.print(table)
    console.print()
    console.print(f"[dim]⭐ = Active model | ✅ = Downloaded | ❌ = Not downloaded[/dim]")


@app.command("info")
def model_info(
    model_key: Optional[str] = typer.Argument(
        None,
        help="Model key (uses active model if not specified)",
    ),
) -> None:
    """
    Show detailed information about a model.
    
    Examples:
    
        # Show active model info
        $ llm-stack model info
    
        # Show specific model info
        $ llm-stack model info llama-3-70b
    """
    config = get_config()
    
    if model_key is None:
        model_key = config.active_model_key
    
    try:
        info = config.get_model_info(model_key)
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)
    
    exists = os.path.isfile(info["path"])
    total_ram = get_total_ram_gb()
    ram_sufficient = total_ram >= info["ram_required_gb"]
    
    console.print()
    console.print(f"[bold cyan]📦 Model: {model_key}[/bold cyan]")
    console.print()
    console.print(f"[bold]Name:[/bold]        {info['name']}")
    console.print(f"[bold]Path:[/bold]        {info['path']}")
    console.print(f"[bold]Status:[/bold]      {'✅ Exists' if exists else '❌ Not downloaded'}")
    console.print()
    console.print(f"[bold]Size:[/bold]        {info['size_gb']} GB")
    console.print(f"[bold]RAM Required:[/bold] {info['ram_required_gb']} GB")
    console.print(f"[bold]Your RAM:[/bold]    {total_ram:.1f} GB {'✅' if ram_sufficient else '⚠️  Insufficient'}")
    console.print()
    console.print(f"[bold]HF Repo:[/bold]     {info['hf_repo']}")
    console.print(f"[bold]HF File:[/bold]     {info['hf_file']}")
    console.print()
    console.print(f"[bold]Description:[/bold]")
    console.print(f"  {info['description']}")


@app.command("download")
def download_model(
    model_key: Optional[str] = typer.Argument(
        None,
        help="Model key (uses active model if not specified)",
    ),
    quantization: Optional[str] = typer.Option(
        None,
        "--quantization",
        "-q",
        help="Quantization type (overrides config)",
    ),
    output_dir: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory (overrides config)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing file",
    ),
) -> None:
    """
    Download a model from Hugging Face.
    
    Uses the huggingface-cli tool if available, otherwise falls back to
    direct download with curl/wget.
    
    Examples:
    
        # Download active model
        $ llm-stack model download
    
        # Download specific model
        $ llm-stack model download llama-3-8b
    
        # Download with different quantization
        $ llm-stack model download -q Q4_K_S
    """
    config = get_config()
    
    if model_key is None:
        model_key = config.active_model_key
    
    try:
        model = config.get_model(model_key)
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)
    
    # Determine output directory
    model_path = expand_path(model.get("path", ""))
    if output_dir:
        model_dir = expand_path(output_dir)
        model_path = os.path.join(model_dir, os.path.basename(model_path))
    else:
        model_dir = os.path.dirname(model_path)
    
    # Create output directory
    Path(model_dir).mkdir(parents=True, exist_ok=True)
    
    # Check if already exists
    if os.path.isfile(model_path) and not force:
        console.print(f"[yellow]⚠️  Model already exists: {model_path}[/yellow]")
        console.print()
        console.print("Use --force to overwrite")
        return
    
    # Check disk space
    _, _, free_gb = get_disk_usage(model_dir)
    size_gb = model.get("size_gb", 0)
    if free_gb < size_gb * 1.2:  # Need 20% extra space
        console.print(f"[red]❌ Insufficient disk space[/red]")
        console.print(f"   Required: ~{size_gb} GB")
        console.print(f"   Available: {free_gb:.1f} GB")
        raise typer.Exit(1)
    
    # Get download URL
    hf_repo = model.get("hf_repo", "")
    hf_file = model.get("hf_file", "")
    
    if not hf_repo or not hf_file:
        console.print("[red]❌ Model configuration missing HF repo/file[/red]")
        raise typer.Exit(1)
    
    console.print(f"[bold green]📥 Downloading model: {model_key}[/bold green]")
    console.print()
    console.print(f"[dim]Repo: {hf_repo}[/dim]")
    console.print(f"[dim]File: {hf_file}[/dim]")
    console.print(f"[dim]Size: ~{size_gb} GB[/dim]")
    console.print(f"[dim]Output: {model_path}[/dim]")
    console.print()
    
    # Try huggingface-cli first
    if check_command_exists("huggingface-cli"):
        console.print("[bold]Using huggingface-cli...[/bold]")
        
        cmd = [
            "huggingface-cli", "download",
            "--resume-download",
            hf_repo,
            "--include", hf_file,
            "--local-dir", model_dir,
        ]
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                DownloadColumn(),
                transient=True,
            ) as progress:
                progress.add_task("Downloading...", total=None)
                
                result = subprocess.run(
                    cmd,
                    check=True,
                    capture_output=False,
                )
            
            console.print()
            console.print(f"[green]✅ Download complete: {model_path}[/green]")
            return
            
        except subprocess.CalledProcessError as e:
            console.print(f"[yellow]⚠️  huggingface-cli failed, trying alternative...[/yellow]")
    
    # Fallback: Use the project's download script if it exists
    project_root = Path(__file__).parent.parent.parent.parent
    download_script = project_root / "bin" / "download-model.sh"
    
    if download_script.exists():
        console.print("[bold]Using download script...[/bold]")
        
        # Set environment variables for the script
        env = os.environ.copy()
        env["MODEL_DIR"] = model_dir
        env["HF_REPO"] = hf_repo
        env["HF_FILE"] = hf_file
        
        if quantization:
            env["QUANTIZATION"] = quantization
        
        try:
            result = subprocess.run(
                ["bash", str(download_script)],
                env=env,
                check=True,
                capture_output=False,
            )
            
            console.print()
            console.print(f"[green]✅ Download complete: {model_path}[/green]")
            return
            
        except subprocess.CalledProcessError:
            pass
    
    # Last resort: Manual download instructions
    console.print("[red]❌ Automatic download failed[/red]")
    console.print()
    console.print("[bold]Manual download:[/bold]")
    console.print()
    console.print(f"1. Visit: https://huggingface.co/{hf_repo}")
    console.print(f"2. Download: {hf_file}")
    console.print(f"3. Move to: {model_path}")
    console.print()
    console.print("Or install huggingface-cli:")
    console.print("  [bold]pip install huggingface_hub[/bold]")
    
    raise typer.Exit(1)


@app.command("delete")
def delete_model(
    model_key: Optional[str] = typer.Argument(
        None,
        help="Model key (uses active model if not specified)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation",
    ),
) -> None:
    """
    Delete a downloaded model file.
    
    ⚠️  This permanently deletes the model file from disk.
    
    Examples:
    
        # Delete active model
        $ llm-stack model delete
    
        # Delete specific model
        $ llm-stack model delete llama-3-8b
    """
    config = get_config()
    
    if model_key is None:
        model_key = config.active_model_key
    
    try:
        info = config.get_model_info(model_key)
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)
    
    model_path = info["path"]
    
    if not os.path.isfile(model_path):
        console.print(f"[yellow]⚠️  Model file not found: {model_path}[/yellow]")
        return
    
    # Confirm deletion
    if not force:
        console.print()
        console.print(f"[bold red]⚠️  Warning: This will permanently delete:[/bold red]")
        console.print(f"   {model_path}")
        console.print()
        
        if not typer.confirm("Are you sure?"):
            console.print("[yellow]Cancelled[/yellow]")
            return
    
    # Delete file
    try:
        file_size = os.path.getsize(model_path)
        os.remove(model_path)
        
        console.print(f"[green]✅ Deleted: {model_path}[/green]")
        console.print(f"[dim]   Freed: {format_size(file_size)}[/dim]")
        
    except OSError as e:
        console.print(f"[red]❌ Error deleting file: {e}[/red]")
        raise typer.Exit(1)


@app.command("validate")
def validate_model(
    model_key: Optional[str] = typer.Argument(
        None,
        help="Model key (uses active model if not specified)",
    ),
) -> None:
    """
    Validate a model file.
    
    Checks file existence, size, and GGUF format integrity.
    
    Examples:
    
        # Validate active model
        $ llm-stack model validate
    
        # Validate specific model
        $ llm-stack model validate llama-3-8b
    """
    config = get_config()
    
    if model_key is None:
        model_key = config.active_model_key
    
    try:
        info = config.get_model_info(model_key)
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)
    
    model_path = info["path"]
    
    console.print(f"[bold]Validating model: {model_key}[/bold]")
    console.print(f"Path: {model_path}")
    console.print()
    
    # Check existence
    if not os.path.isfile(model_path):
        console.print(f"[red]❌ File not found: {model_path}[/red]")
        raise typer.Exit(1)
    
    console.print(f"[green]✅ File exists[/green]")
    
    # Check size
    file_size = os.path.getsize(model_path)
    expected_size = info["size_gb"] * 1024 * 1024 * 1024
    size_diff = abs(file_size - expected_size) / expected_size * 100
    
    console.print(f"[green]✅ Size: {format_size(file_size)}[/green]")
    
    if size_diff > 5:
        console.print(f"[yellow]⚠️  Size differs from expected by {size_diff:.1f}%[/yellow]")
    
    # Check GGUF format
    if check_command_exists("llama-gguf"):
        console.print("[bold]Checking GGUF format...[/bold]")
        
        try:
            result = subprocess.run(
                ["llama-gguf", "info", model_path],
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            if result.returncode == 0:
                console.print(f"[green]✅ Valid GGUF format[/green]")
                
                # Show model info
                if result.stdout.strip():
                    console.print()
                    console.print("[dim]" + result.stdout[:500])
                    if len(result.stdout) > 500:
                        console.print("[dim]... (truncated)[/dim]")
            else:
                console.print(f"[red]❌ Invalid GGUF format[/red]")
                if result.stderr:
                    console.print(f"[dim]{result.stderr}[/dim]")
                    
        except subprocess.TimeoutExpired:
            console.print("[yellow]⚠️  Validation timed out (large file)[/yellow]")
        except Exception as e:
            console.print(f"[yellow]⚠️  Could not validate GGUF: {e}[/yellow]")
    else:
        console.print("[dim]Install llama.cpp for GGUF validation[/dim]")
    
    console.print()
    console.print(f"[bold green]✅ Model validation complete[/bold green]")
