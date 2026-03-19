"""
Run command - One command to download and run any model.

Usage:
    llm-stack run llama-3-8b --chat
    llm-stack run meta-llama/Llama-3-8B-Instruct --api
    llm-stack run unsloth/Qwen3.5-9B-GGUF:Q4_K_M --webui
"""

import os
import subprocess
import time
import signal
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, DownloadColumn
from rich import box

from local_llm.config import get_config, Config
from local_llm.hardware.detector import get_optimal_config, detect_hardware
from local_llm.hardware.recommender import ModelRecommender
from local_llm.models.resolver import ModelResolver, resolve_model
from local_llm.models.downloader import ModelDownloader
from local_llm.utils import (
    is_port_in_use,
    get_process_using_port,
    check_command_exists,
    get_command_path,
    get_gpu_info,
    is_macos,
)

console = Console()


def run_model(
    ctx: typer.Context,
    model: str = typer.Argument(
        ...,
        help="Model identifier (HF repo, URL, config key, or partial name)",
        show_default=False,
    ),
    chat: bool = typer.Option(
        False,
        "--chat",
        "-c",
        help="Start interactive chat after server starts",
    ),
    api: bool = typer.Option(
        False,
        "--api",
        "-a",
        help="Start API server only",
    ),
    webui: bool = typer.Option(
        False,
        "--webui",
        "-w",
        help="Start server and open WebUI in browser",
    ),
    bg: bool = typer.Option(
        True,
        "--bg",
        "--background",
        help="Run server in background (default)",
    ),
    fg: bool = typer.Option(
        False,
        "--fg",
        "--foreground",
        help="Run server in foreground (overrides --bg)",
    ),
    port: Optional[int] = typer.Option(
        None,
        "--port",
        "-p",
        help="Server port (auto-assigns if not specified)",
    ),
    context: Optional[int] = typer.Option(
        None,
        "--context",
        help="Context size (auto-optimizes based on hardware)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force re-download if model exists",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show verbose output",
    ),
) -> None:
    """
    Download and run any model with one command.
    
    Automatically detects hardware and optimizes settings.
    Runs in background by default.
    
    \b
    Examples:
      # Run config model with chat (background by default)
      $ llm-stack run llama-3-8b --chat
      
      # Run HuggingFace model with API
      $ llm-stack run meta-llama/Llama-3-8B-Instruct --api
      
      # Run GGUF model with WebUI
      $ llm-stack run unsloth/Qwen3.5-9B-GGUF:Q4_K_M --webui
      
      # Run in foreground (for debugging)
      $ llm-stack run qwen-35b-a3b --fg
    """
    
    # Determine mode
    if chat:
        mode = "chat"
    elif webui:
        mode = "webui"
    elif api:
        mode = "api"
    else:
        mode = "api"  # Default to API only
    
    # Background is default, fg overrides
    background = bg and not fg
    
    # Run the model
    runner = ModelRunner(console)
    success = runner.run(
        model=model,
        mode=mode,
        port=port,
        context_size=context,
        force_download=force,
        background=bg,
        verbose=verbose,
    )
    
    if not success:
        raise typer.Exit(1)


class ModelRunner:
    """Handle model download and execution."""
    
    def __init__(self, console: Console):
        self.console = console
        self.config = get_config()
        self.resolver = ModelResolver(self.config)
        self.downloader = ModelDownloader()
    
    def run(
        self,
        model: str,
        mode: str = "api",
        port: Optional[int] = None,
        context_size: Optional[int] = None,
        force_download: bool = False,
        background: bool = False,
        verbose: bool = False,
    ) -> bool:
        """Run a model."""
        self.console.print()
        self.console.print(Panel(
            f"[bold cyan]🚀 Running: {model}[/bold cyan]\n"
            f"[dim]Mode: {mode} | Auto-optimized for your hardware[/dim]",
            title="Local LLM Stack",
            box=box.ROUNDED,
        ))
        self.console.print()
        
        try:
            # Step 1: Resolve model
            self.console.print("[bold]Step 1/4:[/bold] Resolving model...")
            ref = self.resolver.resolve(model)
            
            if ref.ref_type == "unknown":
                self.console.print(f"[red]❌ Could not resolve: {model}[/red]")
                self.console.print()
                self.console.print("Try:")
                self.console.print("  - HuggingFace repo: [bold]user/repo:file[/bold]")
                self.console.print("  - HuggingFace URL: [bold]https://huggingface.co/...[/bold]")
                self.console.print("  - Config key: [bold]llama-3-8b[/bold]")
                return False
            
            self.console.print(f"[green]✅ Resolved:[/green] {ref.ref_type}")
            if ref.hf_repo:
                self.console.print(f"   Repo: [dim]{ref.hf_repo}[/dim]")
            if ref.hf_file:
                self.console.print(f"   File: [dim]{ref.hf_file}[/dim]")
            if ref.model_name:
                self.console.print(f"   Name: [dim]{ref.model_name}[/dim]")
            self.console.print()
            
            # Step 2: Get hardware-optimized config
            self.console.print("[bold]Step 2/4:[/bold] Detecting hardware...")
            hw_info = detect_hardware()
            self.console.print(f"[green]✅ {hw_info.summary()}[/green]")
            
            # Get optimal settings
            optimal = get_optimal_config()
            
            # Override with user settings
            if port:
                optimal["port"] = port
            else:
                optimal["port"] = self.config.server_port
            
            if context_size:
                optimal["context_size"] = context_size
            
            self.console.print()
            self.console.print("[bold]Optimized settings:[/bold]")
            self.console.print(f"   GPU Layers: [cyan]{optimal.get('gpu_layers', 0)}[/cyan]")
            self.console.print(f"   Context: [cyan]{optimal.get('context_size', 131072)}[/cyan]")
            self.console.print(f"   Batch Size: [cyan]{optimal.get('batch_size', 512)}[/cyan]")
            self.console.print(f"   Threads: [cyan]{optimal.get('threads', 4)}[/cyan]")
            self.console.print()
            
            # Step 3: Download if needed
            model_path = None
            if ref.hf_repo and ref.hf_file:
                self.console.print("[bold]Step 3/4:[/bold] Checking model...")
                
                # Check if exists
                test_path = self.downloader.models_dir / ref.hf_file
                if test_path.exists() and not force_download:
                    model_path = str(test_path)
                    self.console.print(f"[green]✅ Model already downloaded[/green]")
                    self.console.print(f"   Path: [dim]{model_path}[/dim]")
                else:
                    # Download
                    self.console.print(f"[yellow]📥 Downloading model...[/yellow]")
                    
                    try:
                        model_path = self.downloader.download(
                            hf_repo=ref.hf_repo,
                            hf_file=ref.hf_file,
                        )
                        self.console.print(f"[green]✅ Download complete[/green]")
                        self.console.print(f"   Path: [dim]{model_path}[/dim]")
                    except Exception as e:
                        self.console.print(f"[red]❌ Download failed: {e}[/red]")
                        return False
            else:
                # Use config path
                model_path = self.config.model_path
                if not os.path.isfile(model_path):
                    self.console.print(f"[red]❌ Model not found: {model_path}[/red]")
                    self.console.print("Download with: [bold]llm-stack model download[/bold]")
                    return False
            
            self.console.print()
            
            # Step 4: Start server
            self.console.print("[bold]Step 4/4:[/bold] Starting server...")
            
            server_started = self._start_server(
                model_path=model_path,
                port=optimal["port"],
                gpu_layers=optimal.get("gpu_layers", 0),
                context_size=optimal.get("context_size", 131072),
                batch_size=optimal.get("batch_size", 512),
                ubatch_size=optimal.get("ubatch_size", 256),
                flash_attn=optimal.get("flash_attn", "auto"),
                threads=optimal.get("threads", 4),
                background=background,
                verbose=verbose,
            )
            
            if not server_started:
                return False
            
            # Post-start actions
            if mode == "webui":
                self._open_webui(optimal["port"])
            elif mode == "chat":
                self._start_chat(optimal["port"])
            elif mode == "api":
                if background:
                    self.console.print()
                    self.console.print(f"[green]✅ Server running in background[/green]")
                    self.console.print(f"   API: http://localhost:{optimal['port']}/v1")
                    self.console.print()
                    self.console.print("Chat with:")
                    self.console.print(f"  [bold]llm-stack run {model} --chat[/bold]")
            
            return True
            
        except Exception as e:
            self.console.print(f"[red]❌ Error: {e}[/red]")
            if verbose:
                import traceback
                traceback.print_exc()
            return False
    
    def _start_server(
        self,
        model_path: str,
        port: int,
        gpu_layers: int,
        context_size: int,
        batch_size: int,
        ubatch_size: int,
        flash_attn: str,
        threads: int,
        background: bool,
        verbose: bool,
    ) -> bool:
        """Start llama.cpp server."""
        # Check if llama-server exists
        if not check_command_exists("llama-server"):
            self.console.print("[red]❌ llama-server not found[/red]")
            self.console.print("Install with: [bold]brew install llama.cpp[/bold] (macOS)")
            return False
        
        # Check if port is in use
        if is_port_in_use(port):
            pid = get_process_using_port(port)
            self.console.print(f"[yellow]⚠️  Port {port} is in use (PID: {pid})[/yellow]")
            
            # Ask to stop existing server
            if typer.confirm("Stop existing server and continue?"):
                os.kill(pid, signal.SIGTERM)
                time.sleep(2)
            else:
                return False
        
        # Build command
        cmd = [
            get_command_path("llama-server"),
            "-m", model_path,
            "--port", str(port),
            "--host", "0.0.0.0",
            "--ctx-size", str(context_size),
            "--threads", str(threads),
            "--threads-batch", str(threads),
            "-ngl", str(gpu_layers),
            "--batch-size", str(batch_size),
            "--ubatch-size", str(ubatch_size),
            "--flash-attn", flash_attn,
        ]
        
        if background:
            # Background mode
            log_file = Path("/tmp/llama-server.log")
            pid_file = Path("/tmp/llama-server.pid")
            
            self.console.print(f"[dim]Starting server in background...[/dim]")
            
            # Set environment for Metal
            env = os.environ.copy()
            if is_macos():
                gpu_info = get_gpu_info()
                if gpu_info["gpu_type"] == "metal":
                    env["GGML_METAL_RESIDENCY_SETS"] = "0"
            
            with open(log_file, "w") as log:
                process = subprocess.Popen(
                    cmd,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                    env=env,
                )
            
            # Write PID
            pid_file.write_text(str(process.pid))
            
            # Wait for server to start
            time.sleep(3)
            
            # Check if running
            if process.poll() is not None:
                self.console.print("[red]❌ Server failed to start[/red]")
                self.console.print(f"Check logs: [bold]{log_file}[/bold]")
                return False
            
            self.console.print(f"[green]✅ Server started (PID: {process.pid})[/green]")
            return True
            
        else:
            # Foreground mode
            self.console.print(f"[dim]Starting server in foreground...[/dim]")
            self.console.print(f"[dim]Press Ctrl+C to stop[/dim]")
            self.console.print()
            
            try:
                subprocess.run(cmd, check=True)
                return True
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Server stopped[/yellow]")
                return True
            except subprocess.CalledProcessError as e:
                self.console.print(f"[red]❌ Server error: {e}[/red]")
                return False
    
    def _open_webui(self, port: int) -> None:
        """Open WebUI in browser."""
        import webbrowser
        url = f"http://localhost:{port}"
        
        self.console.print()
        self.console.print(f"[green]✅ Opening WebUI: {url}[/green]")
        
        webbrowser.open(url)
    
    def _start_chat(self, port: int) -> None:
        """Start interactive chat."""
        from local_llm.cli.commands.chat import chat_interactive
        
        self.console.print()
        self.console.print(f"[green]✅ Starting chat...[/green]")
        self.console.print()
        
        # Call chat command
        chat_interactive(port=port)
