#!/usr/bin/env python3
"""
Markdown Renderer for Terminal
Supports: rich, glow, mdv, or plain text fallback
"""

import sys
import subprocess
from pathlib import Path


def check_dependencies():
    """Check available markdown renderers."""
    deps = {}
    
    # Check rich
    try:
        from rich.console import Console
        from rich.markdown import Markdown
        deps['rich'] = True
    except ImportError:
        deps['rich'] = False
    
    # Check glow (binary)
    try:
        result = subprocess.run(['glow', '--version'], capture_output=True, text=True, timeout=2)
        deps['glow'] = result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        deps['glow'] = False
    
    # Check mdv
    try:
        import mdv
        deps['mdv'] = True
    except ImportError:
        deps['mdv'] = False
    
    return deps


def render_with_rich(text: str, width: int = None):
    """Render markdown using rich library."""
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.theme import Theme
    
    # Custom theme for better contrast
    custom_theme = Theme({
        "markdown.code": "cyan",
        "markdown.code_block": "dim cyan",
        "markdown.heading": "bold blue",
        "markdown.item": "white",
        "markdown.item.number": "yellow",
        "markdown.bullet": "green",
        "markdown.table": "dim white",
        "markdown.link": "blue underline",
        "markdown.emph": "italic",
        "markdown.strong": "bold",
    })
    
    console = Console(
        width=width,
        theme=custom_theme,
        force_terminal=True
    )
    
    md = Markdown(text)
    console.print(md)


def render_with_glow(text: str):
    """Render markdown using glow (best quality)."""
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(text)
        temp_path = f.name
    
    try:
        # Glow with style
        result = subprocess.run(
            ['glow', '-s', 'dark', '-w', '80', temp_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        print(result.stdout)
    except subprocess.TimeoutExpired:
        print("⚠️  Glow timed out, falling back to plain text")
        print(text)
    finally:
        import os
        os.unlink(temp_path)


def render_with_md(text: str):
    """Render markdown using mdv."""
    import mdv
    
    # Render with color
    rendered = mdv.main(text)
    print(rendered)


def render_markdown(text: str, renderer: str = 'auto', width: int = None):
    """
    Render markdown to terminal.
    
    Args:
        text: Markdown text to render
        renderer: 'rich', 'glow', 'mdv', 'plain', or 'auto'
        width: Terminal width (default: auto-detect)
    """
    deps = check_dependencies()
    
    if renderer == 'auto':
        # Priority: glow > rich > mdv > plain
        if deps['glow']:
            renderer = 'glow'
        elif deps['rich']:
            renderer = 'rich'
        elif deps['mdv']:
            renderer = 'mdv'
        else:
            renderer = 'plain'
    
    if renderer == 'glow':
        if deps['glow']:
            render_with_glow(text)
        else:
            print("⚠️  glow not available, falling back to rich")
            renderer = 'rich'
    
    if renderer == 'rich':
        if deps['rich']:
            render_with_rich(text, width)
        else:
            print("⚠️  rich not available, falling back to plain")
            renderer = 'plain'
    
    if renderer == 'mdv':
        if deps['mdv']:
            render_with_md(text)
        else:
            print("⚠️  mdv not available, falling back to plain")
            renderer = 'plain'
    
    if renderer == 'plain':
        # Simple plain text with basic formatting
        print(text)


def render_file(path: str, renderer: str = 'auto'):
    """Render markdown file to terminal."""
    path = Path(path)
    
    if not path.exists():
        print(f"❌ File not found: {path}")
        sys.exit(1)
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    render_markdown(content, renderer)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Render markdown to terminal')
    parser.add_argument('file', nargs='?', help='Markdown file to render')
    parser.add_argument('--renderer', '-r', choices=['auto', 'rich', 'glow', 'mdv', 'plain'], 
                       default='auto', help='Renderer to use')
    parser.add_argument('--width', '-w', type=int, help='Terminal width')
    parser.add_argument('--check', action='store_true', help='Check available renderers')
    
    args = parser.parse_args()
    
    if args.check:
        deps = check_dependencies()
        print("Available markdown renderers:")
        for name, available in deps.items():
            status = "✅" if available else "❌"
            print(f"  {status} {name}")
        
        best = next((k for k, v in deps.items() if v), 'plain')
        print(f"\nRecommended: {best}")
        return
    
    if args.file:
        render_file(args.file, args.renderer)
    else:
        # Read from stdin
        content = sys.stdin.read()
        render_markdown(content, args.renderer)


if __name__ == '__main__':
    main()
