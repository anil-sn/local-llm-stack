"""
BitNet-specific CLI commands.

Commands for managing and running BitNet b1.58 models.
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from local_llm.config import get_config
from local_llm.models.resolver import ModelResolver
from local_llm.hardware.detector import detect_hardware, get_optimal_config

app = typer.Typer(help="BitNet model management")
console = Console()


@app.command("list")
def list_bitnet_models() -> None:
    """
    List available BitNet models.

    Shows all BitNet b1.58 models configured in config.yaml.
    """
    config = get_config()
    resolver = ModelResolver(config=config)

    console.print()
    console.print(Panel(
        "[bold cyan]🪙 BitNet b1.58 Models[/bold cyan]\n\n"
        "Native 1-bit LLMs with 2-6x faster CPU inference and 80%+ energy reduction",
        title="BitNet Models",
        box=box.ROUNDED,
    ))
    console.print()

    # Get all models and filter for BitNet
    bitnet_models = []
    for model_key in config.available_models:
        model_info = config.get_model_info(model_key)
        model_config = config.get_model(model_key)
        
        # Check if it's a BitNet model
        if model_config.get("model_type") == "bitnet":
            bitnet_models.append((model_key, model_info))

    if not bitnet_models:
        console.print("[yellow]⚠️  No BitNet models configured[/yellow]")
        console.print()
        console.print("Add BitNet models to config.yaml:")
        console.print("  [dim]See docs/BITNET-SUPPORT-ANALYSIS.md[/dim]")
        return

    table = Table(
        title="Available BitNet Models",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )

    table.add_column("Model Key", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Size", justify="right")
    table.add_column("RAM", justify="right")
    table.add_column("Quantization", style="dim")
    table.add_column("Command", style="green")

    for model_key, model_info in bitnet_models:
        model_config = config.get_model(model_key)
        quant = model_config.get("quantization", "i2_s")

        table.add_row(
            model_key,
            model_info["name"],
            f"{model_info['size_gb']} GB",
            f"{model_info['ram_required_gb']} GB",
            quant.upper(),
            f"local-llm run {model_key} --chat",
        )

    console.print(table)
    console.print()
    console.print("[bold]Benefits of BitNet:[/bold]")
    console.print("  ⚡ 2-6x faster CPU inference")
    console.print("  🔋 80%+ energy reduction")
    console.print("  💾 50% smaller model size")
    console.print()


@app.command("info")
def bitnet_info(
    model_key: str = typer.Argument(
        ...,
        help="BitNet model key",
    ),
) -> None:
    """
    Show detailed information about a BitNet model.

    Examples:

        local-llm bitnet info bitnet-2b-4t
    """
    config = get_config()

    try:
        model_info = config.get_model_info(model_key)
        model_config = config.get_model(model_key)
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)

    # Check if it's a BitNet model
    if model_config.get("model_type") != "bitnet":
        console.print(f"[red]❌ '{model_key}' is not a BitNet model[/red]")
        raise typer.Exit(1)

    console.print()
    console.print(f"[bold cyan]🪙 BitNet Model: {model_key}[/bold cyan]")
    console.print()

    # Basic info
    console.print(f"[bold]Name:[/bold]        {model_info['name']}")
    console.print(f"[bold]HF Repo:[/bold]     {model_info['hf_repo']}")
    console.print(f"[bold]HF File:[/bold]     {model_info['hf_file']}")
    console.print(f"[bold]Quantization:[/bold] {model_config.get('quantization', 'i2_s').upper()}")
    console.print()

    # Size info
    console.print(f"[bold]Size:[/bold]        {model_info['size_gb']} GB")
    console.print(f"[bold]RAM Required:[/bold] {model_info['ram_required_gb']} GB")
    console.print()

    # Description
    console.print(f"[bold]Description:[/bold]")
    console.print(f"  {model_info['description']}")
    console.print()

    # Performance expectations
    console.print(f"[bold]Expected Performance (CPU):[/bold]")
    console.print(f"  Prompt Processing: 500+ tok/s")
    console.print(f"  Generation: 100-200 tok/s")
    console.print(f"  Energy: 80% less than standard models")
    console.print()

    # Run command
    console.print(f"[bold green]Run with:[/bold green]")
    console.print(f"  local-llm run {model_key} --chat")


@app.command("recommend")
def recommend_bitnet() -> None:
    """
    Check if BitNet models are recommended for your hardware.

    Analyzes your system and recommends BitNet if beneficial.
    """
    console.print()
    console.print("[bold cyan]🔍 Analyzing your hardware for BitNet...[/bold cyan]")
    console.print()

    # Detect hardware
    hw = detect_hardware()

    # Show hardware summary
    console.print("[bold]Your System:[/bold]")
    if hw.gpu.has_gpu:
        console.print(f"  GPU: {hw.gpu.gpu_name} ({hw.gpu.vram_total_gb:.1f}GB VRAM)")
    else:
        console.print(f"  GPU: [yellow]None (CPU-only)[/yellow]")
    console.print(f"  CPU: {hw.cpu.model} ({hw.cpu.cores} cores)")
    console.print(f"  RAM: {hw.memory.total_gb:.1f}GB total, {hw.memory.available_gb:.1f}GB available")
    console.print()

    # Get BitNet-optimized config
    bitnet_config = get_optimal_config(model_type="bitnet")
    standard_config = get_optimal_config(model_type="standard")

    # Determine if BitNet is recommended
    is_recommended = False
    reasons = []

    # CPU-only systems benefit most
    if not hw.gpu.has_gpu:
        is_recommended = True
        reasons.append("✅ CPU-only system - BitNet excels on CPU")

    # Limited VRAM
    if hw.gpu.has_gpu and hw.gpu.vram_total_gb < 8:
        is_recommended = True
        reasons.append("✅ Limited VRAM - BitNet uses 50% less memory")

    # Energy efficiency
    reasons.append("✅ Energy efficiency - 80%+ reduction")

    # Performance
    reasons.append("✅ Performance - 2-6x faster CPU inference")

    # Show recommendation
    if is_recommended:
        console.print(Panel(
            "[bold green]✅ BitNet is HIGHLY RECOMMENDED for your system![/bold green]\n\n" +
            "\n".join(reasons),
            title="Recommendation",
            border_style="green",
            box=box.ROUNDED,
        ))
    else:
        console.print(Panel(
            "[bold yellow]⚠️  BitNet is optional for your system[/bold yellow]\n\n"
            "You have a powerful GPU, but BitNet can still provide:\n"
            "  • Energy efficiency\n"
            "  • Lower memory usage\n"
            "  • Faster CPU fallback",
            title="Recommendation",
            border_style="yellow",
            box=box.ROUNDED,
        ))

    console.print()

    # Show configuration comparison
    console.print("[bold]Configuration Comparison:[/bold]")
    console.print()

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Setting", style="cyan")
    table.add_column("Standard", justify="right")
    table.add_column("BitNet", justify="right")
    table.add_column("Benefit", style="green")

    table.add_row(
        "Batch Size",
        str(standard_config["batch_size"]),
        f"[green]{bitnet_config['batch_size']}[/green]",
        "Larger batches" if bitnet_config["batch_size"] > standard_config["batch_size"] else "Same",
    )

    table.add_row(
        "Context Size",
        str(standard_config["context_size"]),
        f"[green]{bitnet_config['context_size']}[/green]",
        "More context" if bitnet_config["context_size"] > standard_config["context_size"] else "Same",
    )

    table.add_row(
        "GPU Layers",
        str(standard_config["gpu_layers"]),
        f"[yellow]{bitnet_config['gpu_layers']}[/yellow]",
        "CPU-optimized",
    )

    table.add_row(
        "Kernels",
        "Standard",
        f"[green]BitNet-optimized[/green]",
        "2-6x faster",
    )

    console.print(table)
    console.print()

    # Show available BitNet models
    config = get_config()
    bitnet_models = [
        key for key in config.available_models
        if config.get_model(key).get("model_type") == "bitnet"
    ]

    if bitnet_models:
        console.print(f"[bold]Available BitNet Models:[/bold] {', '.join(bitnet_models)}")
        console.print()
        console.print(f"[bold green]Try it:[/bold green]")
        console.print(f"  local-llm run {bitnet_models[0]} --chat")
    else:
        console.print("[yellow]⚠️  No BitNet models configured yet[/yellow]")
        console.print()
        console.print("Add to config.yaml:")
        console.print("  [dim]See docs/BITNET-SUPPORT-ANALYSIS.md[/dim]")


@app.command("download")
def download_bitnet(
    model_key: str = typer.Argument(
        ...,
        help="BitNet model key to download",
    ),
) -> None:
    """
    Download a BitNet model.

    Examples:

        local-llm bitnet download bitnet-2b-4t
    """
    from local_llm.models.downloader import ModelDownloader

    config = get_config()

    # Validate model key
    try:
        model_info = config.get_model_info(model_key)
        model_config = config.get_model(model_key)
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)

    # Check if it's a BitNet model
    if model_config.get("model_type") != "bitnet":
        console.print(f"[red]❌ '{model_key}' is not a BitNet model[/red]")
        raise typer.Exit(1)

    # Check if already downloaded
    import os
    if os.path.isfile(model_info["path"]):
        console.print(f"[green]✅ Model already downloaded:[/green] {model_info['path']}")
        return

    # Download
    console.print()
    console.print(f"[bold cyan]📥 Downloading BitNet model: {model_key}[/bold cyan]")
    console.print()
    console.print(f"[dim]Repo: {model_info['hf_repo']}[/dim]")
    console.print(f"[dim]File: {model_info['hf_file']}[/dim]")
    console.print(f"[dim]Size: ~{model_info['size_gb']} GB[/dim]")
    console.print()

    downloader = ModelDownloader()

    try:
        model_path = downloader.download(
            hf_repo=model_info["hf_repo"],
            hf_file=model_info["hf_file"],
        )

        console.print()
        console.print(f"[green]✅ Download complete![/green]")
        console.print(f"   Path: {model_path}")
        console.print()
        console.print(f"[bold green]Run with:[/bold green]")
        console.print(f"   local-llm run {model_key} --chat")

    except Exception as e:
        console.print(f"[red]❌ Download failed: {e}[/red]")
        console.print()
        console.print("[dim]Try manual download:[/dim]")
        console.print(f"   huggingface-cli download {model_info['hf_repo']} --include \"{model_info['hf_file']}\"")
        raise typer.Exit(1)
