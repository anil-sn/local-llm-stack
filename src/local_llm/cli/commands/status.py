"""
Status and system information commands for Local LLM Stack CLI.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from local_llm.config import get_config
from local_llm.utils import (
    get_system_info,
    get_total_ram_gb,
    get_available_ram_gb,
    get_cpu_count,
    get_disk_usage,
    is_port_in_use,
    get_process_using_port,
    check_command_exists,
    get_gpu_info,
)

app = typer.Typer(help="Check system and server status")
console = Console()


@app.callback(invoke_without_command=True)
def status_main(
    ctx: typer.Context,
) -> None:
    """
    Show server status.
    
    If no subcommand is given, shows the server status.
    
    Examples:
    
        # Show server status
        $ llm-stack status
        
        # Show system info
        $ llm-stack status system
    """
    if ctx.invoked_subcommand is None:
        # Call server by default
        server()


@app.command()
def system() -> None:
    """
    Show system information.

    Displays CPU, RAM, disk, and platform information.

    Examples:

        # Show system info
        $ llm-stack status system
    """
    info = get_system_info()

    console.print()
    console.print(f"[bold cyan]🖥️  System Information[/bold cyan]")
    console.print()
    
    # Platform info in compact table
    platform_table = Table(box=box.ROUNDED, show_header=False, padding=(0, 1))
    platform_table.add_column("Property", style="bold cyan")
    platform_table.add_column("Value", style="white")
    platform_table.add_row("Platform", f"{info['platform']} ({info['os']})")
    platform_table.add_row("Machine", info['machine'])
    platform_table.add_row("Python", info['python_version'])
    console.print(platform_table)
    console.print()

    # GPU Info
    gpu_info = get_gpu_info()
    gpu_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    gpu_table.add_column("Property", style="bold")
    gpu_table.add_column("Value")
    
    if gpu_info["has_gpu"]:
        gpu_style = "green" if gpu_info["gpu_type"] == "metal" else "cyan"
        gpu_table.add_row("GPU", f"[{gpu_style}]✅ {gpu_info['gpu_name']}[/{gpu_style}]")
        gpu_table.add_row("GPU Type", gpu_info["gpu_type"].upper())
        gpu_table.add_row("Recommended Layers", str(gpu_info["recommended_layers"]))
    else:
        gpu_table.add_row("GPU", "[yellow]⚠️  No GPU detected[/yellow]")
        gpu_table.add_row("GPU Type", "CPU only")
    
    console.print(gpu_table)
    console.print()

    # CPU, RAM, Disk in compact format
    cpu_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    cpu_table.add_column("Property", style="bold")
    cpu_table.add_column("Value")
    cpu_table.add_row("CPU Cores", str(info["cpu_count"]))
    console.print(cpu_table)

    ram_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    ram_table.add_column("Property", style="bold")
    ram_table.add_column("Value")
    ram_table.add_row("Memory Total", f"{info['total_ram_gb']:.1f} GB")
    ram_table.add_row("Memory Available", f"{info['available_ram_gb']:.1f} GB")
    usage = ((info['total_ram_gb'] - info['available_ram_gb']) / info['total_ram_gb'] * 100)
    ram_table.add_row("Memory Usage", f"{usage:.1f}%")
    console.print(ram_table)

    disk_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    disk_table.add_column("Property", style="bold")
    disk_table.add_column("Value")
    disk_table.add_row("Disk Total", f"{info['disk_total_gb']:.1f} GB")
    disk_table.add_row("Disk Used", f"{info['disk_used_gb']:.1f} GB")
    disk_table.add_row("Disk Free", f"{info['disk_free_gb']:.1f} GB")
    disk_usage = (info['disk_used_gb'] / info['disk_total_gb'] * 100) if info['disk_total_gb'] > 0 else 0
    disk_table.add_row("Disk Usage", f"{disk_usage:.1f}%")
    console.print(disk_table)


@app.command()
def server() -> None:
    """
    Check server status.

    Shows whether the server is running and its configuration.

    Examples:

        # Check server status
        $ llm-stack status server
    """
    config = get_config()

    console.print()
    console.print(f"[bold cyan]🔍  Server Status[/bold cyan]")
    console.print()

    # Check if port is in use
    port = config.server_port
    is_running = is_port_in_use(port)

    if is_running:
        pid = get_process_using_port(port)
        
        # Status in compact format
        status_table = Table(box=box.ROUNDED, show_header=False, padding=(0, 1))
        status_table.add_column("Property", style="bold green")
        status_table.add_column("Value", style="white")
        status_table.add_row("Status", "✅ Running")
        status_table.add_row("Port", f"http://localhost:{port}")
        if pid:
            status_table.add_row("PID", str(pid))
            # Try to get uptime
            try:
                result = subprocess.run(
                    ["ps", "-o", "etime=", "-p", str(pid)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0 and result.stdout.strip():
                    status_table.add_row("Uptime", result.stdout.strip())
            except Exception:
                pass
        console.print(status_table)
    else:
        status_table = Table(box=box.ROUNDED, show_header=False, padding=(0, 1))
        status_table.add_column("Property", style="bold red")
        status_table.add_column("Value", style="white")
        status_table.add_row("Status", "❌ Not running")
        status_table.add_row("Start with", "[bold]llm-stack server start[/bold]")
        console.print(status_table)

    console.print()
    
    # Show server configuration
    console.print(f"[bold]Server Configuration[/bold]")
    console.print()

    config_table = Table(box=box.ROUNDED, show_header=False, padding=(0, 1))
    config_table.add_column("Property", style="cyan")
    config_table.add_column("Value", style="white")

    config_table.add_row("Port", str(port))
    config_table.add_row("Host", config.server_host)
    config_table.add_row("Context Size", str(config.context_size))
    config_table.add_row("GPU Layers", str(config.gpu_layers))
    config_table.add_row("Batch Size", str(config.batch_size))
    config_table.add_row("API URL", config.api_base_url)

    console.print(config_table)


@app.command()
def model() -> None:
    """
    Check model status.

    Shows active model information and whether it exists.

    Examples:

        # Check model status
        $ llm-stack status model
    """
    config = get_config()

    console.print()
    console.print(f"[bold cyan]📦  Model Status[/bold cyan]")
    console.print()

    model_key = config.active_model_key
    model_name = config.active_model_name
    model_path = config.model_path

    exists = os.path.isfile(model_path)

    # Get file size if exists
    file_size_str = "N/A"
    if exists:
        size_bytes = os.path.getsize(model_path)
        file_size_str = f"{size_bytes / (1024 ** 3):.2f} GB"

    # Check RAM
    try:
        model_info = config.get_model(model_key)
        ram_required = model_info.get("ram_required_gb", 0)
        total_ram = get_total_ram_gb()
        ram_ok = total_ram >= ram_required
    except Exception:
        ram_required = 0
        ram_ok = True

    # Status table
    status_table = Table(box=box.ROUNDED, show_header=False, padding=(0, 1))
    status_table.add_column("Property", style="bold cyan")
    status_table.add_column("Value", style="white")
    
    status_table.add_row("Model", model_key)
    status_table.add_row("Name", model_name)
    status_table.add_row("Status", "[green]✅ Exists[/green]" if exists else "[red]❌ Not found[/red]")
    
    if exists:
        status_table.add_row("Size", file_size_str)
        status_table.add_row("Path", model_path)
        status_table.add_row("RAM Required", f"{ram_required} GB {'✅' if ram_ok else '⚠️'}")
    
    console.print(status_table)

    if not exists:
        console.print()
        console.print("[dim]Download with:[/dim]")
        console.print("  [bold]llm-stack model download[/bold]")


@app.command()
def dependencies() -> None:
    """
    Check dependencies.
    
    Verifies that required tools and libraries are installed.
    
    Examples:
    
        # Check dependencies
        $ llm-stack status dependencies
    """
    console.print()
    console.print("[bold]🔍 Checking Dependencies[/bold]")
    console.print()
    
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Dependency", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Notes", style="dim")
    
    # Check llama.cpp tools
    llama_tools = [
        ("llama-server", "Required for running the server"),
        ("llama-cli", "Required for interactive chat"),
        ("llama-bench", "Required for benchmarks"),
        ("llama-perplexity", "Required for perplexity tests"),
        ("llama-gguf", "Required for model validation (GGUF info)"),
    ]
    
    for tool, notes in llama_tools:
        if check_command_exists(tool):
            table.add_row(tool, "[green]✅[/green]", notes)
        else:
            table.add_row(tool, "[yellow]❌[/yellow]", f"{notes} - Install llama.cpp")
    
    # Check Python packages (package_name, import_name, notes)
    python_packages = [
        ("openai", "openai", "Required for API client"),
        ("requests", "requests", "Required for web features"),
        ("rich", "rich", "Required for CLI formatting"),
        ("pyyaml", "yaml", "Required for config parsing"),
        ("typer", "typer", "Required for CLI"),
    ]

    for pkg_name, import_name, notes in python_packages:
        try:
            __import__(import_name)
            table.add_row(pkg_name, "[green]✅[/green]", notes)
        except ImportError:
            table.add_row(pkg_name, "[red]❌[/red]", f"{notes} - pip install {pkg_name}")
    
    console.print(table)
    console.print()

    # Summary
    missing = []

    for tool, _ in llama_tools[:2]:  # Only critical tools
        if not check_command_exists(tool):
            missing.append(tool)

    for pkg_name, import_name, _ in python_packages[:3]:  # Only critical packages
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pkg_name)

    if missing:
        console.print(f"[yellow]⚠️  Missing: {', '.join(missing)}[/yellow]")
        console.print()
        console.print("Install missing dependencies:")
        console.print("  [bold]brew install llama.cpp[/bold]  (macOS)")
        console.print("  [bold]pip install -r requirements.txt[/bold]")
    else:
        console.print("[bold green]✅ All dependencies installed[/bold green]")


@app.command()
def all() -> None:
    """
    Show complete status overview.
    
    Combines system, server, model, and dependency status.
    
    Examples:
    
        # Show everything
        $ llm-stack status all
    """
    console.print()
    console.print("[bold]══════════════════════════════════════════════════[/bold]")
    console.print("[bold]       Local LLM Stack - Complete Status         [/bold]")
    console.print("[bold]══════════════════════════════════════════════════[/bold]")
    
    # System
    system()
    
    # Server
    console.print()
    console.print("[bold]──────────────────────────────────────────────────[/bold]")
    server()
    
    # Model
    console.print()
    console.print("[bold]──────────────────────────────────────────────────[/bold]")
    model()
    
    # Dependencies
    console.print()
    console.print("[bold]──────────────────────────────────────────────────[/bold]")
    dependencies()
    
    console.print()
    console.print("[bold]══════════════════════════════════════════════════[/bold]")
