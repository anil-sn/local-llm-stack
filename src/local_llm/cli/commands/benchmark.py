"""
Benchmark commands for Local LLM Stack CLI.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table
from rich import box

from local_llm.config import get_config
from local_llm.utils import check_command_exists, get_cpu_count

app = typer.Typer(help="Run benchmarks")
console = Console()


@app.command("run")
def run_benchmarks(
    benchmark_type: str = typer.Option(
        "all",
        "--type",
        "-t",
        help="Benchmark type: all, native, batched, perplexity, api",
        case_sensitive=False,
    ),
    repetitions: Optional[int] = typer.Option(
        None,
        "--repetitions",
        "-r",
        help="Number of repetitions (uses config if not specified)",
    ),
    output_dir: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory for results",
    ),
) -> None:
    """
    Run benchmark suite.
    
    Runs various benchmarks to measure model performance including
    prompt processing speed, generation speed, and API latency.
    
    Examples:
    
        # Run all benchmarks
        $ llm-stack benchmark run
    
        # Run only native benchmarks
        $ llm-stack benchmark run -t native
    
        # Run API benchmarks with custom repetitions
        $ llm-stack benchmark run -t api -r 5
    """
    config = get_config()

    # Get project root (go up 5 levels from src/local_llm/cli/commands/)
    project_root = Path(__file__).parent.parent.parent.parent.parent
    benchmark_dir = project_root / "tools" / "benchmarks"
    
    if not benchmark_dir.exists():
        console.print("[red]❌ Benchmark directory not found[/red]")
        console.print(f"   Expected: {benchmark_dir}")
        raise typer.Exit(1)
    
    console.print("[bold]🏃 Running Benchmarks[/bold]")
    console.print()
    
    # Map benchmark types to scripts
    benchmarks = {
        "all": ["run-all.sh"],
        "native": ["run-native-benchmark.sh"],
        "batched": ["run-batched-bench.sh"],
        "perplexity": ["run-perplexity.sh"],
        "api": ["run-api-benchmark.sh"],
    }
    
    if benchmark_type not in benchmarks:
        console.print(f"[red]❌ Unknown benchmark type: {benchmark_type}[/red]")
        console.print()
        console.print("Available types: " + ", ".join(benchmarks.keys()))
        raise typer.Exit(1)
    
    scripts_to_run = benchmarks[benchmark_type]
    
    # Set environment variables
    env = os.environ.copy()
    
    if repetitions:
        env["BENCH_REPETITIONS"] = str(repetitions)
    else:
        env["BENCH_REPETITIONS"] = str(config.get("benchmarks", "repetitions", default=3))
    
    if output_dir:
        env["BENCHMARK_DIR"] = output_dir
    else:
        env["BENCHMARK_DIR"] = config.benchmark_dir
    
    # Run benchmarks
    for script_name in scripts_to_run:
        script_path = benchmark_dir / script_name
        
        if not script_path.exists():
            console.print(f"[yellow]⚠️  Script not found: {script_path}[/yellow]")
            continue
        
        console.print(f"[bold]Running: {script_name}[/bold]")
        console.print()
        
        try:
            result = subprocess.run(
                ["bash", str(script_path)],
                env=env,
                check=True,
                capture_output=False,
            )
            
            console.print()
            console.print(f"[green]✅ {script_name} complete[/green]")
            console.print()
            
        except subprocess.CalledProcessError as e:
            console.print(f"[red]❌ {script_name} failed[/red]")
            console.print()
            
            if benchmark_type != "all":
                raise typer.Exit(1)
    
    console.print("[bold green]🎉 Benchmark suite complete[/bold green]")


@app.command("native")
def native_benchmark(
    prompt_length: int = typer.Option(
        512,
        "--prompt",
        "-p",
        help="Prompt length for processing benchmark",
    ),
    gen_length: int = typer.Option(
        128,
        "--gen",
        "-g",
        help="Generation length",
    ),
) -> None:
    """
    Run native llama.cpp benchmarks.
    
    Uses llama-bench to measure prompt processing and generation speed.
    Does not require the server to be running.
    
    Examples:
    
        # Default benchmark
        $ llm-stack benchmark native
    
        # Custom lengths
        $ llm-stack benchmark native -p 1024 -g 256
    """
    config = get_config()
    
    if not check_command_exists("llama-bench"):
        console.print("[red]❌ llama-bench not found[/red]")
        console.print()
        console.print("Install llama.cpp with benchmarks:")
        console.print("  [bold]brew install llama.cpp[/bold]  (macOS)")
        raise typer.Exit(1)
    
    model = config.model_path
    if not os.path.isfile(model):
        console.print(f"[red]❌ Model not found: {model}[/red]")
        raise typer.Exit(1)
    
    console.print("[bold]🏃 Running llama-bench[/bold]")
    console.print()
    
    cmd = [
        "llama-bench",
        "-m", model,
        "-p", str(prompt_length),
        "-n", str(gen_length),
        "-ngl", str(config.gpu_layers),
        "-t", str(get_cpu_count()),
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=False)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Benchmark failed[/red]")
        raise typer.Exit(1)


@app.command("api")
def api_benchmark(
    port: Optional[int] = typer.Option(
        None,
        "--port",
        "-p",
        help="Server port (uses config if not specified)",
    ),
    repetitions: int = typer.Option(
        3,
        "--repetitions",
        "-r",
        help="Number of repetitions",
    ),
) -> None:
    """
    Run API benchmarks.
    
    Measures API response time and throughput.
    Requires the server to be running.
    
    Examples:
    
        # Run API benchmarks
        $ llm-stack benchmark api
    
        # Custom port and repetitions
        $ llm-stack benchmark api -p 9000 -r 5
    """
    config = get_config()
    server_port = port or config.server_port
    
    # Check if server is running
    from local_llm.utils import is_port_in_use
    
    if not is_port_in_use(server_port):
        console.print("[red]❌ Server is not running on port {server_port}[/red]")
        console.print()
        console.print("Start the server:")
        console.print(f"  [bold]llm-stack server start --port {server_port}[/bold]")
        raise typer.Exit(1)
    
    console.print(f"[bold]🏃 Running API benchmarks on port {server_port}[/bold]")
    console.print()
    
    # Get project root (go up 5 levels from src/local_llm/cli/commands/)
    project_root = Path(__file__).parent.parent.parent.parent.parent
    benchmark_script = project_root / "tools" / "benchmarks" / "run-api-benchmark.sh"
    
    if not benchmark_script.exists():
        console.print("[red]❌ Benchmark script not found[/red]")
        console.print(f"   Expected: {benchmark_script}")
        raise typer.Exit(1)
    
    env = os.environ.copy()
    env["SERVER_PORT"] = str(server_port)
    env["BENCH_REPETITIONS"] = str(repetitions)
    
    try:
        subprocess.run(
            ["bash", str(benchmark_script)],
            env=env,
            check=True,
            capture_output=False,
        )
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ API benchmark failed[/red]")
        raise typer.Exit(1)


@app.command("compare")
def compare_results(
    result_files: List[str] = typer.Argument(
        None,
        help="Result files to compare (auto-discovers if not specified)",
    ),
) -> None:
    """
    Compare benchmark results.
    
    Compares results from different benchmark runs side by side.
    
    Examples:
    
        # Compare all recent results
        $ llm-stack benchmark compare
    
        # Compare specific files
        $ llm-stack benchmark compare results1.json results2.json
    """
    config = get_config()
    
    # Get project root (go up 5 levels from src/local_llm/cli/commands/)
    project_root = Path(__file__).parent.parent.parent.parent.parent
    benchmark_script = project_root / "tools" / "benchmarks" / "compare-results.sh"
    
    if not benchmark_script.exists():
        console.print("[red]❌ Compare script not found[/red]")
        console.print(f"   Expected: {benchmark_script}")
        raise typer.Exit(1)
    
    cmd = ["bash", str(benchmark_script)]
    
    if result_files:
        cmd.extend(result_files)
    
    try:
        subprocess.run(cmd, check=True, capture_output=False)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Compare failed[/red]")
        raise typer.Exit(1)


@app.command("clean")
def clean_results() -> None:
    """
    Clean benchmark results.
    
    Removes all benchmark result files from the benchmark directory.
    """
    config = get_config()
    benchmark_dir = Path(config.benchmark_dir)
    
    if not benchmark_dir.exists():
        console.print("[yellow]⚠️  Benchmark directory does not exist[/yellow]")
        return
    
    console.print(f"[bold]Cleaning benchmark results in: {benchmark_dir}[/bold]")
    console.print()
    
    # Count files
    json_files = list(benchmark_dir.glob("*.json"))
    md_files = list(benchmark_dir.glob("*.md"))
    
    if not json_files and not md_files:
        console.print("[yellow]⚠️  No benchmark results found[/yellow]")
        return
    
    console.print(f"Found {len(json_files)} JSON files and {len(md_files)} markdown files")
    console.print()
    
    if not typer.confirm("Are you sure you want to delete all benchmark results?"):
        console.print("[yellow]Cancelled[/yellow]")
        return
    
    # Delete files
    deleted = 0
    for f in json_files + md_files:
        try:
            f.unlink()
            deleted += 1
        except OSError:
            pass
    
    console.print(f"[green]✅ Deleted {deleted} files[/green]")
