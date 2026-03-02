"""
Chat and agent commands for Local LLM Stack CLI.
"""

import os
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich import box

from local_llm.config import get_config
from local_llm.utils import check_command_exists, get_cpu_count

app = typer.Typer(help="Chat with the LLM")
console = Console()


@app.command("interactive")
def chat_interactive(
    model_path: Optional[str] = typer.Argument(
        None,
        help="Path to model file (uses config.yaml if not specified)",
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
    system_prompt: Optional[str] = typer.Option(
        None,
        "--system-prompt",
        "-s",
        help="System prompt (uses default if not specified)",
    ),
) -> None:
    """
    Interactive chat with the LLM using llama-cli.
    
    Provides a terminal-based interactive chat interface with full
    conversation history and color-coded output.
    
    Examples:
    
        # Start interactive chat
        $ llm-stack chat interactive
    
        # With custom context size
        $ llm-stack chat interactive --context 32768
    
        # With custom system prompt
        $ llm-stack chat interactive -s "You are a coding assistant."
    """
    config = get_config()
    
    # Check if llama-cli is available
    if not check_command_exists("llama-cli"):
        console.print("[red]❌ llama-cli not found[/red]")
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
    
    # Build command
    cmd = [
        "llama-cli",
        "-m", model,
        "--ctx-size", str(context_size or config.context_size),
        "--threads", str(threads or config.threads or get_cpu_count()),
        "--threads-batch", str(threads or config.threads or get_cpu_count()),
        "-n", "2048",
        "--temp", str(config.temperature),
        "--top-p", str(config.top_p),
        "--repeat-penalty", str(config.repeat_penalty),
        "-ngl", str(config.gpu_layers),
        "--flash-attn", config.flash_attn,
        "--interactive-first",
        "--color",
    ]
    
    # Add system prompt
    sys_prompt = system_prompt or config.get(
        "chat", "system_prompt",
        default="You are a helpful, harmless, and honest AI assistant."
    )
    cmd.extend(["--prompt", sys_prompt])
    
    # Show header
    console.print()
    console.print(Panel(
        "[bold]Interactive Chat Mode[/bold]\n\n"
        "Type your message and press Enter\n"
        "Commands: [bold]/exit[/bold], [bold]/quit[/bold], [bold]/clear[/bold]",
        title="💬 Qwen Chat",
        border_style="blue",
        box=box.ROUNDED,
    ))
    console.print()
    console.print(f"[dim]Model: {model}[/dim]")
    console.print(f"[dim]Context: {context_size or config.context_size}[/dim]")
    console.print(f"[dim]Threads: {threads or config.threads or get_cpu_count()}[/dim]")
    console.print()
    console.print("[bold]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold]")
    console.print()
    
    # Run llama-cli
    os.execvp("llama-cli", cmd)


@app.command("quick")
def chat_quick(
    message: str = typer.Argument(
        ...,
        help="Message to send to the LLM",
    ),
    model_path: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="Path to model file (uses config.yaml if not specified)",
    ),
    stream: bool = typer.Option(
        True,
        "--stream/--no-stream",
        "-s",
        help="Stream response",
    ),
) -> None:
    """
    Quick single-turn chat with the LLM.
    
    Sends a single message and prints the response.
    Useful for scripting and quick queries.
    
    Examples:
    
        # Quick question
        $ llm-stack chat quick "What is quantum computing?"
    
        # In a script
        $ response=$(llm-stack chat quick "Explain recursion")
    """
    try:
        from openai import OpenAI
    except ImportError:
        console.print("[red]❌ openai package not installed[/red]")
        console.print()
        console.print("Install with:")
        console.print("  [bold]pip install openai[/bold]")
        raise typer.Exit(1)
    
    config = get_config()
    
    # Check if server is running
    from local_llm.utils import is_port_in_use
    
    if not is_port_in_use(config.server_port):
        console.print("[red]❌ Server is not running[/red]")
        console.print()
        console.print("Start the server:")
        console.print(f"  [bold]llm-stack server start[/bold]")
        raise typer.Exit(1)
    
    # Create client
    client = OpenAI(
        base_url=config.api_base_url,
        api_key=config.api_key,
    )
    
    console.print()
    console.print(f"[bold]📤 Question:[/bold] {message}")
    console.print()
    console.print("[bold]📥 Answer:[/bold]")
    console.print()
    
    try:
        if stream:
            response = client.chat.completions.create(
                model=config.active_model_key,
                messages=[
                    {"role": "user", "content": message},
                ],
                max_tokens=None,
                temperature=config.temperature,
                stream=True,
            )
            
            full_response = ""
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    console.print(content, end="")
                    full_response += content
            
            console.print()
            
        else:
            response = client.chat.completions.create(
                model=config.active_model_key,
                messages=[
                    {"role": "user", "content": message},
                ],
                max_tokens=None,
                temperature=config.temperature,
            )
            
            content = response.choices[0].message.content
            console.print(Markdown(content))
            
            # Show stats
            console.print()
            console.print(f"[dim]Tokens: {response.usage.total_tokens} | ")
            if hasattr(response, 'timings'):
                console.print(f"[dim]Speed: {response.timings.get('predicted_per_second', 'N/A'):.1f} tok/s[/dim]")
    
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("agent")
def agent_chat(
    message: Optional[str] = typer.Argument(
        None,
        help="Message to send (interactive mode if not specified)",
    ),
    model_path: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="Path to model file (uses config.yaml if not specified)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show verbose output",
    ),
) -> None:
    """
    Agent mode with tool calling capabilities.
    
    The agent can execute bash commands, read/write files,
    search the web, and run Python code.
    
    Examples:
    
        # Interactive agent mode
        $ llm-stack chat agent
    
        # Single task
        $ llm-stack chat agent "Find all Python files with TODO comments"
    """
    # Try to import the agent module
    try:
        # Add src/python to path for legacy agent
        project_root = Path(__file__).parent.parent.parent.parent
        legacy_agent_path = project_root / "src" / "python"
        sys.path.insert(0, str(legacy_agent_path))
        
        # Try to import config module from legacy path
        import importlib.util
        config_spec = importlib.util.spec_from_file_location(
            "config",
            project_root / "src" / "python" / "config.py"
        )
        if config_spec and config_spec.loader:
            config_module = importlib.util.module_from_spec(config_spec)
            config_spec.loader.exec_module(config_module)
        
    except Exception:
        pass
    
    # Use the new agent if available
    try:
        from local_llm.agent import Agent
        
        config = get_config()
        agent = Agent(
            base_url=config.api_base_url,
            model=config.active_model_key,
            use_rich=True,
        )
        
        if message:
            # Single task
            console.print()
            console.print(f"[bold]🤖 Agent Task:[/bold] {message}")
            console.print()
            
            result = agent.chat(message, verbose=verbose)
            
            console.print()
            console.print(f"[bold green]✅ Task complete[/bold green]")
        else:
            # Interactive mode
            console.print()
            console.print(Panel(
                "[bold]Agent Mode with Tool Calling[/bold]\n\n"
                "The agent can:\n"
                "  • Execute bash commands\n"
                "  • Read/write files\n"
                "  • Search the web\n"
                "  • Run Python code\n\n"
                "Type [bold]/exit[/bold] to quit",
                title="🤖 Qwen Agent",
                border_style="green",
                box=box.ROUNDED,
            ))
            console.print()
            
            while True:
                try:
                    user_input = console.input("[bold blue]You:[/bold blue] ").strip()
                    
                    if not user_input:
                        continue
                    
                    if user_input.lower() in ["/exit", "/quit", "/q"]:
                        console.print("[yellow]Goodbye![/yellow]")
                        break
                    
                    console.print()
                    result = agent.chat(user_input, verbose=verbose)
                    console.print()
                
                except KeyboardInterrupt:
                    console.print("\n[yellow]Interrupted[/yellow]")
                    break
                except EOFError:
                    break
    
    except ImportError as e:
        console.print("[red]❌ Agent module not available[/red]")
        console.print()
        console.print("The agent requires the legacy qwen-agent.py module.")
        console.print(f"Check: {project_root / 'src' / 'python' / 'qwen-agent.py'}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)
