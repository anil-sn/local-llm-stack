"""
Server management commands for Local LLM Stack CLI.
"""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from local_llm.config import Config, get_config
from local_llm.utils import (
    check_command_exists,
    get_command_path,
    get_cpu_count,
    get_process_using_port,
    is_port_in_use,
    kill_process,
    is_macos,
    get_gpu_info,
)

app = typer.Typer(help="Manage the LLM server")
console = Console()


@app.command("start")
def start_server(
    model_path: Optional[str] = typer.Argument(
        None,
        help="Path to model file (uses config.yaml if not specified)",
    ),
    port: Optional[int] = typer.Option(
        None,
        "--port",
        "-p",
        help="Server port (overrides config.yaml)",
    ),
    context_size: Optional[int] = typer.Option(
        None,
        "--context",
        "-c",
        help="Context size (overrides config.yaml)",
    ),
    threads: Optional[int] = typer.Option(
        None,
        "--threads",
        "-t",
        help="Number of threads (auto-detects if not specified)",
    ),
    gpu_layers: Optional[int] = typer.Option(
        None,
        "--gpu-layers",
        "-gl",
        help="Number of layers to offload to GPU",
    ),
    background: bool = typer.Option(
        True,
        "--background/--foreground",
        "-b/-f",
        help="Run in background (default) or foreground",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show verbose output",
    ),
) -> None:
    """
    Start the LLM server.
    
    The server provides an OpenAI-compatible API for chat completions.
    By default, runs in the background and logs to /tmp/llama-server.log.
    
    Examples:
    
        # Start with default settings from config.yaml
        $ llm-stack server start
    
        # Start in foreground for debugging
        $ llm-stack server start --foreground
    
        # Start with custom port and context size
        $ llm-stack server start --port 9000 --context 32768
    """
    config = get_config()
    
    # Check if llama-server is available
    if not check_command_exists("llama-server"):
        console.print("[red]❌ llama-server not found[/red]")
        console.print()
        console.print("Install llama.cpp:")
        console.print("  [bold]brew install llama.cpp[/bold]  (macOS)")
        console.print("  [bold]sudo apt install llama.cpp[/bold]  (Ubuntu/Debian)")
        raise typer.Exit(1)
    
    # Determine model path
    model = model_path or config.model_path
    if not os.path.isfile(model):
        console.print(f"[red]❌ Model not found: {model}[/red]")
        console.print()
        console.print("Download with:")
        console.print(f"  [bold]llm-stack model download[/bold]")
        raise typer.Exit(1)
    
    # Check if port is already in use
    server_port = port or config.server_port
    if is_port_in_use(server_port):
        pid = get_process_using_port(server_port)
        console.print(f"[yellow]⚠️  Port {server_port} is already in use[/yellow]")
        if pid:
            console.print(f"   Process ID: {pid}")
            console.print()
            console.print("Stop existing server:")
            console.print(f"  [bold]llm-stack server stop[/bold]")
        raise typer.Exit(1)
    
    # Build command
    llama_path = get_command_path("llama-server")
    cmd = [
        llama_path,
        "-m", model,
        "--port", str(server_port),
        "--host", config.server_host,
        "--ctx-size", str(context_size or config.context_size),
        "--threads", str(threads or config.threads or get_cpu_count()),
        "--threads-batch", str(threads or config.threads or get_cpu_count()),
        "-ngl", str(gpu_layers if gpu_layers is not None else config.gpu_layers),
        "--batch-size", str(config.batch_size),
        "--ubatch-size", str(config.ubatch_size),
        "--flash-attn", config.flash_attn,
        "--temp", str(config.temperature),
        "--top-p", str(config.top_p),
        "--repeat-penalty", str(config.repeat_penalty),
    ]
    
    # Add reasoning options if enabled
    if config.reasoning_format != "none":
        cmd.extend(["--reasoning-format", config.reasoning_format])
    if config.reasoning_budget > 0:
        cmd.extend(["--reasoning-budget", str(config.reasoning_budget)])
    
    if background:
        # Run in background
        log_file = Path(config.log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        pid_file = Path(config.pid_file)
        pid_file.parent.mkdir(parents=True, exist_ok=True)
        
        console.print("[bold green]🚀 Starting LLM server in background...[/bold green]")
        console.print()
        
        # Set environment variables for Metal crash workaround (macOS)
        env = os.environ.copy()
        if is_macos():
            gpu_info = get_gpu_info()
            if gpu_info["gpu_type"] == "metal":
                # Fix for Metal crash on pre-M5 chips
                env["GGML_METAL_RESIDENCY_SETS"] = "0"
                console.print("[dim]   GPU: Metal (workaround enabled)[/dim]")

        with open(log_file, "w") as log:
            process = subprocess.Popen(
                cmd,
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
                env=env,
            )
        
        # Write PID file
        with open(pid_file, "w") as f:
            f.write(str(process.pid))
        
        console.print(f"[green]✅ Server started (PID: {process.pid})[/green]")
        console.print(f"[dim]   Port: http://localhost:{server_port}[/dim]")
        console.print(f"[dim]   Log: {log_file}[/dim]")
        console.print()
        console.print("Check status:")
        console.print(f"  [bold]llm-stack status[/bold]")
        console.print()
        console.print("Stop server:")
        console.print(f"  [bold]llm-stack server stop[/bold]")
        
    else:
        # Run in foreground
        console.print("[bold green]🚀 Starting LLM server in foreground...[/bold green]")
        console.print(f"[dim]Model: {model}[/dim]")
        console.print(f"[dim]Port: {server_port}[/dim]")
        console.print(f"[dim]Context: {context_size or config.context_size}[/dim]")
        
        # Set environment variables for Metal crash workaround (macOS)
        env = os.environ.copy()
        if is_macos():
            gpu_info = get_gpu_info()
            if gpu_info["gpu_type"] == "metal":
                env["GGML_METAL_RESIDENCY_SETS"] = "0"
                console.print("[dim]   GPU: Metal (workaround enabled)[/dim]")
        
        console.print()

        try:
            subprocess.run(cmd, check=True, env=env)
        except KeyboardInterrupt:
            console.print("\n[yellow]Server stopped[/yellow]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]❌ Server exited with error: {e}[/red]")
            raise typer.Exit(1)


@app.command("stop")
def stop_server(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force kill (SIGKILL instead of SIGTERM)",
    ),
) -> None:
    """
    Stop the LLM server.
    
    Examples:
    
        # Graceful shutdown
        $ llm-stack server stop
    
        # Force kill
        $ llm-stack server stop --force
    """
    config = get_config()
    pid_file = Path(config.pid_file)
    
    # Try to get PID from file
    pid = None
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
        except (ValueError, IOError):
            pass
    
    # If no PID file, check port
    if pid is None:
        pid = get_process_using_port(config.server_port)
    
    if pid is None:
        console.print("[yellow]⚠️  No running server found[/yellow]")
        return
    
    # Check if process exists
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        console.print("[yellow]⚠️  Server process not found (may have already stopped)[/yellow]")
        if pid_file.exists():
            pid_file.unlink()
        return
    
    # Kill the process
    sig = signal.SIGKILL if force else signal.SIGTERM
    sig_name = "SIGKILL" if force else "SIGTERM"
    
    console.print(f"[bold]Stopping server (PID: {pid}) with {sig_name}...[/bold]")
    
    if kill_process(pid, sig):
        # Wait for process to stop
        for _ in range(10):
            try:
                os.kill(pid, 0)
                time.sleep(0.5)
            except ProcessLookupError:
                break
        else:
            # Process still running after timeout
            if not force:
                console.print("[yellow]Graceful shutdown timed out, forcing...[/yellow]")
                kill_process(pid, signal.SIGKILL)
        
        console.print("[green]✅ Server stopped[/green]")
        
        # Clean up PID file
        if pid_file.exists():
            pid_file.unlink()
    else:
        console.print("[red]❌ Failed to stop server[/red]")
        raise typer.Exit(1)


@app.command("restart")
def restart_server(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force kill when stopping",
    ),
) -> None:
    """
    Restart the LLM server.
    
    Equivalent to running 'stop' followed by 'start'.
    """
    console.print("[bold]Restarting server...[/bold]")
    console.print()
    
    # Stop
    stop_server(force=force)
    
    # Brief pause
    time.sleep(1)
    
    # Start
    console.print()
    start_server(background=True)


@app.command("status")
def server_status() -> None:
    """
    Check server status.
    
    Shows whether the server is running, its PID, port, and uptime.
    """
    config = get_config()
    pid_file = Path(config.pid_file)
    
    # Get PID
    pid = None
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
        except (ValueError, IOError):
            pass
    
    # If no PID file, check port
    if pid is None:
        pid = get_process_using_port(config.server_port)
    
    if pid is None:
        console.print(Panel(
            "[red]Server is not running[/red]\n\n"
            "Start with: [bold]llm-stack server start[/bold]",
            title="🔴 Server Status",
            border_style="red",
        ))
        return
    
    # Check if process exists
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        console.print(Panel(
            "[yellow]Server process not found (stale PID file)[/yellow]\n\n"
            "Cleaning up PID file...",
            title="⚠️ Server Status",
            border_style="yellow",
        ))
        if pid_file.exists():
            pid_file.unlink()
        return
    
    # Get process info
    port = config.server_port
    uptime = "unknown"
    
    # Try to get uptime (macOS/Linux)
    try:
        if sys.platform != "win32":
            result = subprocess.run(
                ["ps", "-o", "etime=", "-p", str(pid)],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                uptime = result.stdout.strip()
    except Exception:
        pass
    
    console.print(Panel(
        f"[green]✅ Server is running[/green]\n\n"
        f"[bold]PID:[/bold]     {pid}\n"
        f"[bold]Port:[/bold]    http://localhost:{port}\n"
        f"[bold]Uptime:[/bold]  {uptime}\n"
        f"[bold]Log:[/bold]     {config.log_file}",
        title="🟢 Server Status",
        border_style="green",
    ))


@app.command("logs")
def server_logs(
    lines: int = typer.Option(
        50,
        "--lines",
        "-n",
        help="Number of lines to show",
    ),
    follow: bool = typer.Option(
        False,
        "--follow",
        "-f",
        help="Follow log output (like tail -f)",
    ),
) -> None:
    """
    Show server logs.
    
    Examples:
    
        # Show last 50 lines
        $ llm-stack server logs
    
        # Show last 100 lines
        $ llm-stack server logs --lines 100
    
        # Follow logs in real-time
        $ llm-stack server logs --follow
    """
    config = get_config()
    log_file = Path(config.log_file)
    
    if not log_file.exists():
        console.print("[yellow]⚠️  Log file not found[/yellow]")
        console.print(f"   Path: {log_file}")
        return
    
    if follow:
        # Follow mode
        console.print(f"[bold]Following logs: {log_file}[/bold]")
        console.print("[dim]Press Ctrl+C to stop[/dim]")
        console.print()
        
        try:
            subprocess.run(["tail", "-f", str(log_file)], check=True)
        except KeyboardInterrupt:
            console.print("\n[yellow]Stopped following logs[/yellow]")
    else:
        # Show last N lines
        try:
            result = subprocess.run(
                ["tail", "-n", str(lines), str(log_file)],
                capture_output=True,
                text=True,
                check=True,
            )
            console.print(result.stdout)
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error reading logs: {e}[/red]")
