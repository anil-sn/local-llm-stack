#!/usr/bin/env python3
"""
Generic Local LLM Agent with Tool Calling
Features: Multi-step reasoning, tool chaining, result caching, web search, code execution

Usage:
    python agent.py "Find all Python files with TODO comments"
    python agent.py --chat  # Interactive mode
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("⚠️  requests not installed. Web features disabled.")
    print("   Install: pip install requests")

from openai import OpenAI

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.table import Table
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# Load configuration from config.yaml
sys.path.insert(0, str(Path(__file__).parent))
from config import Config
config = Config()


class ToolResult:
    """Structured tool result."""
    def __init__(self, success: bool, data: Any = None, error: str = None, metadata: dict = None):
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata
        }

    def __str__(self) -> str:
        if self.success:
            return f"✅ Success: {json.dumps(self.data, default=str)[:200]}"
        return f"❌ Error: {self.error}"


class ToolExecutor:
    """Execute various tools with caching and logging."""

    def __init__(self, cache_enabled: bool = True):
        self.cache_enabled = cache_enabled
        self.cache: Dict[str, ToolResult] = {}
        self.history: List[Dict] = []
        self.output: List[str] = []

    def log(self, message: str, level: str = "info"):
        """Log tool execution with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        emoji = {"info": "ℹ️", "success": "✅", "error": "❌", "warning": "⚠️"}.get(level, "•")
        log_msg = f"[{timestamp}] {emoji} {message}"
        self.output.append(log_msg)
        print(log_msg)

    def _get_cache_key(self, tool_name: str, **kwargs) -> str:
        """Generate cache key from tool call."""
        key_str = f"{tool_name}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def execute_bash(self, command: str, timeout: int = None, use_cache: bool = False) -> ToolResult:
        """Execute bash command."""
        self.log(f"🔧 Executing: {command}")

        cache_key = self._get_cache_key("execute_bash", command=command) if use_cache else None
        if cache_key and cache_key in self.cache:
            self.log("Cache hit!", "info")
            return self.cache[cache_key]

        try:
            start_time = time.time()
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            elapsed = time.time() - start_time

            output = result.stdout + result.stderr
            exit_code = result.returncode

            self.log(f"Exit code: {exit_code} ({elapsed:.2f}s)", "success" if exit_code == 0 else "error")

            tool_result = ToolResult(
                success=exit_code == 0,
                data={"stdout": result.stdout, "stderr": result.stderr, "combined": output},
                metadata={"exit_code": exit_code, "elapsed": elapsed, "command": command}
            )

            if cache_key and exit_code == 0:
                self.cache[cache_key] = tool_result

            self.history.append({"tool": "execute_bash", "command": command, "result": tool_result.to_dict()})
            return tool_result

        except subprocess.TimeoutExpired:
            self.log("Timeout expired", "error")
            return ToolResult(success=False, error=f"Command timed out after {timeout}s")
        except Exception as e:
            self.log(f"Exception: {e}", "error")
            return ToolResult(success=False, error=str(e))

    def read_file(self, path: str, limit_lines: int = None, limit_chars: int = None) -> ToolResult:
        """Read file contents."""
        self.log(f"📖 Reading: {path}")

        try:
            abs_path = os.path.abspath(path)

            if not os.path.exists(abs_path):
                return ToolResult(success=False, error=f"File not found: {path}")

            with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            original_size = len(content)

            if limit_lines:
                lines = content.split('\n')
                if len(lines) > limit_lines:
                    content = '\n'.join(lines[:limit_lines]) + f"\n\n[... truncated: {len(lines) - limit_lines} more lines ...]"

            if limit_chars and len(content) > limit_chars:
                content = content[:limit_chars] + f"\n\n[... truncated: {original_size - limit_chars} more chars ...]"

            self.log(f"Read {len(content)} chars", "success")

            result = ToolResult(
                success=True,
                data={"content": content, "path": path, "size": original_size},
                metadata={"lines": content.count('\n') + 1, "chars": len(content)}
            )

            self.history.append({"tool": "read_file", "path": path, "result": result.to_dict()})
            return result

        except Exception as e:
            self.log(f"Error: {e}", "error")
            return ToolResult(success=False, error=str(e))

    def write_file(self, path: str, content: str, append: bool = False) -> ToolResult:
        """Write file contents."""
        self.log(f"✏️ Writing: {path} ({'append' if append else 'overwrite'})")

        try:
            abs_path = os.path.abspath(path)
            os.makedirs(os.path.dirname(abs_path) or '.', exist_ok=True)

            mode = 'a' if append else 'w'
            with open(abs_path, mode, encoding='utf-8') as f:
                f.write(content)

            self.log(f"Wrote {len(content)} chars", "success")

            result = ToolResult(
                success=True,
                data={"path": path, "bytes": len(content), "mode": "append" if append else "write"},
                metadata={"absolute_path": abs_path}
            )

            self.history.append({"tool": "write_file", "path": path, "result": result.to_dict()})
            return result

        except Exception as e:
            self.log(f"Error: {e}", "error")
            return ToolResult(success=False, error=str(e))

    def list_dir(self, path: str = ".", show_hidden: bool = False, recursive: bool = False) -> ToolResult:
        """List directory contents."""
        self.log(f"📁 Listing: {path} {'(recursive)' if recursive else ''}")

        try:
            abs_path = os.path.abspath(path)

            if not os.path.isdir(abs_path):
                return ToolResult(success=False, error=f"Not a directory: {path}")

            items = []

            if recursive:
                for root, dirs, files in os.walk(abs_path):
                    rel_root = os.path.relpath(root, abs_path)
                    for d in dirs:
                        if show_hidden or not d.startswith('.'):
                            items.append(f"dir: {os.path.join(rel_root, d) if rel_root != '.' else d}")
                    for f in files:
                        if show_hidden or not f.startswith('.'):
                            items.append(f"file: {os.path.join(rel_root, f) if rel_root != '.' else f}")
            else:
                for item in os.listdir(abs_path):
                    if show_hidden or not item.startswith('.'):
                        item_path = os.path.join(abs_path, item)
                        item_type = "dir" if os.path.isdir(item_path) else "file"
                        items.append(f"{item_type}: {item}")

            items.sort()
            self.log(f"Found {len(items)} items", "success")

            result = ToolResult(
                success=True,
                data={"items": items, "count": len(items)},
                metadata={"path": path, "recursive": recursive, "show_hidden": show_hidden}
            )

            self.history.append({"tool": "list_dir", "path": path, "result": result.to_dict()})
            return result

        except Exception as e:
            self.log(f"Error: {e}", "error")
            return ToolResult(success=False, error=str(e))

    def web_search(self, query: str, num_results: int = 5, safe_search: bool = True) -> ToolResult:
        """Search the web using DuckDuckGo."""
        self.log(f"🔍 Searching: {query}")

        if not HAS_REQUESTS:
            return ToolResult(success=False, error="requests library not installed")

        try:
            from urllib.parse import quote
            url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml"
            }

            start_time = time.time()
            resp = requests.get(url, headers=headers, timeout=15)
            elapsed = time.time() - start_time

            if resp.status_code != 200:
                return ToolResult(success=False, error=f"HTTP {resp.status_code}")

            results = []
            html = resp.text

            # Parse DuckDuckGo results
            result_pattern = r'<a class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]+)</a>'
            snippet_pattern = r'<a class="result__snippet"[^>]*>([^<]*(?:<[^>]*>[^<]*)*)'

            urls = re.findall(result_pattern, html)
            snippets = re.findall(snippet_pattern, html)

            for i, (url, title) in enumerate(urls[:num_results]):
                snippet = snippets[i] if i < len(snippets) else ""
                # Clean HTML from snippet
                snippet = re.sub(r'<[^>]+>', '', snippet).strip()
                results.append({
                    "title": title.strip(),
                    "url": url,
                    "snippet": snippet
                })

            self.log(f"Found {len(results)} results ({elapsed:.2f}s)", "success")

            result = ToolResult(
                success=True,
                data={"results": results, "query": query},
                metadata={"num_results": len(results), "elapsed": elapsed}
            )

            self.history.append({"tool": "web_search", "query": query, "result": result.to_dict()})
            return result

        except Exception as e:
            self.log(f"Error: {e}", "error")
            return ToolResult(success=False, error=str(e))

    def fetch_url(self, url: str, timeout: int = 10) -> ToolResult:
        """Fetch URL content."""
        self.log(f"🌐 Fetching: {url}")

        if not HAS_REQUESTS:
            return ToolResult(success=False, error="requests library not installed")

        try:
            start_time = time.time()
            resp = requests.get(url, timeout=timeout)
            elapsed = time.time() - start_time

            self.log(f"Status: {resp.status_code} ({elapsed:.2f}s)", "success" if resp.ok else "error")

            result = ToolResult(
                success=resp.status_code == 200,
                data={
                    "content": resp.text[:10000],  # Limit content
                    "status_code": resp.status_code,
                    "url": url
                },
                metadata={"elapsed": elapsed, "content_length": len(resp.text)}
            )

            self.history.append({"tool": "fetch_url", "url": url, "result": result.to_dict()})
            return result

        except Exception as e:
            self.log(f"Error: {e}", "error")
            return ToolResult(success=False, error=str(e))

    def execute_python(self, code: str, timeout: int = 30) -> ToolResult:
        """Execute Python code."""
        self.log("🐍 Executing Python code")

        try:
            start_time = time.time()
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            elapsed = time.time() - start_time

            output = result.stdout + result.stderr
            exit_code = result.returncode

            self.log(f"Exit code: {exit_code} ({elapsed:.2f}s)", "success" if exit_code == 0 else "error")

            tool_result = ToolResult(
                success=exit_code == 0,
                data={"stdout": result.stdout, "stderr": result.stderr, "output": output},
                metadata={"exit_code": exit_code, "elapsed": elapsed}
            )

            self.history.append({"tool": "execute_python", "code": code[:200], "result": tool_result.to_dict()})
            return tool_result

        except subprocess.TimeoutExpired:
            self.log("Timeout expired", "error")
            return ToolResult(success=False, error=f"Code execution timed out after {timeout}s")
        except Exception as e:
            self.log(f"Error: {e}", "error")
            return ToolResult(success=False, error=str(e))

    def get_history(self) -> List[Dict]:
        """Get tool execution history."""
        return self.history

    def clear_cache(self):
        """Clear result cache."""
        self.cache.clear()
        self.log("Cache cleared")


# Tool definitions for OpenAI-compatible API
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "execute_bash",
            "description": "Execute a bash command on the system. Use for file operations, running programs, system queries.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The bash command to execute"},
                    "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 30}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file"},
                    "limit_lines": {"type": "integer", "description": "Max lines to read", "default": 100}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file"},
                    "content": {"type": "string", "description": "Content to write"},
                    "append": {"type": "boolean", "description": "Append to file", "default": False}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List contents of a directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to directory", "default": "."},
                    "recursive": {"type": "boolean", "description": "List recursively", "default": False},
                    "show_hidden": {"type": "boolean", "description": "Show hidden files", "default": False}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "num_results": {"type": "integer", "description": "Number of results", "default": 5}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "Fetch content from a URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to fetch"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_python",
            "description": "Execute Python code and return output",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code to execute"}
                },
                "required": ["code"]
            }
        }
    }
]

# Tool execution mapping
TOOL_EXECUTORS = {
    "execute_bash": lambda ex, **kw: ex.execute_bash(kw.get("command"), kw.get("timeout", 30)),
    "read_file": lambda ex, **kw: ex.read_file(kw.get("path"), kw.get("limit_lines", 100)),
    "write_file": lambda ex, **kw: ex.write_file(kw.get("path"), kw.get("content"), kw.get("append", False)),
    "list_dir": lambda ex, **kw: ex.list_dir(kw.get("path", "."), kw.get("show_hidden", False), kw.get("recursive", False)),
    "web_search": lambda ex, **kw: ex.web_search(kw.get("query"), kw.get("num_results", 5)),
    "fetch_url": lambda ex, **kw: ex.fetch_url(kw.get("url")),
    "execute_python": lambda ex, **kw: ex.execute_python(kw.get("code")),
}


class Agent:
    """Advanced LLM Agent with tool calling capabilities."""

    SYSTEM_PROMPT = """You are an advanced AI assistant with powerful tool capabilities.

## Available Tools

You have access to these tools. Use them by outputting XML tags EXACTLY as shown:

1. **execute_bash** - Run shell commands
   Format: `<tool>execute_bash(command="ls -la")</tool>`

2. **read_file** - Read file contents
   Format: `<tool>read_file(path="/etc/hosts")</tool>`

3. **write_file** - Write to files
   Format: `<tool>write_file(path="/tmp/test.py", content="print('hi')")</tool>`

4. **list_dir** - List directory contents
   Format: `<tool>list_dir(path="/tmp")</tool>`

5. **web_search** - Search the web
   Format: `<tool>web_search(query="Python tutorials")</tool>`

6. **fetch_url** - Fetch URL content
   Format: `<tool>fetch_url(url="https://example.com")</tool>`

7. **execute_python** - Run Python code
   Format: `<tool>execute_python(code="print(2+2)")</tool>`

## Guidelines

- **Think step-by-step** before acting
- **Use tools** when they can help answer questions
- **Chain tools** for complex tasks (use multiple in sequence)
- **Verify results** before presenting final answers
- **Be thorough** and comprehensive
- **Handle errors** gracefully and try alternatives

## Response Format

1. First, think through the problem
2. Use tools as needed with `<tool>...</tool>` tags
3. Present final answer clearly after tool results

## Capabilities

- Full filesystem access (read/write anywhere)
- Execute any bash command
- Run Python code
- Search and fetch from the web
- No artificial restrictions"""

    def __init__(self, base_url: str = None,
                 model: str = None,
                 max_turns: int = 15,
                 temperature: float = None,
                 use_rich: bool = True):
        # Use config.yaml values if not provided
        self.base_url = base_url or config.get_api_url()
        self.model = model or config.get_model_key()
        self.temperature = temperature if temperature is not None else config.get('advanced', 'temperature', default=0.7)
        self.client = OpenAI(base_url=self.base_url, api_key="not-needed")
        self.executor = ToolExecutor()
        self.max_turns = max_turns
        self.conversation_history: List[Dict] = []
        self.use_rich = use_rich and HAS_RICH
        self.console = Console() if self.use_rich else None

    def chat(self, message: str, verbose: bool = True, stream: bool = False) -> str:
        """Chat with the agent, allowing tool use."""

        # Initialize conversation if new
        if not self.conversation_history:
            self.conversation_history = [
                {"role": "system", "content": self.SYSTEM_PROMPT}
            ]

        # Add user message
        self.conversation_history.append({"role": "user", "content": message})

        final_response = ""

        for turn in range(self.max_turns):
            if verbose:
                print(f"\n{'='*60}")
                print(f"🔄 Turn {turn + 1}/{self.max_turns}")
                print(f"{'='*60}")

            try:
                # Call the model
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.conversation_history,
                    max_tokens=None,
                    temperature=self.temperature,
                    stream=stream
                )

                assistant_message = response.choices[0].message.content
                final_response = assistant_message

                if verbose:
                    if self.use_rich:
                        # Display with rich markdown rendering
                        self.console.print()
                        self.console.print(Panel(
                            Markdown(assistant_message[:2000] + ('...' if len(assistant_message) > 2000 else '')),
                            title="🤖 Model Output",
                            border_style="blue",
                            box=box.ROUNDED
                        ))
                    else:
                        print(f"\n🤖 Model output:\n{assistant_message[:1000]}{'...' if len(assistant_message) > 1000 else ''}")

                # Parse and execute tool calls
                tool_calls = self._parse_tool_calls(assistant_message)

                if tool_calls:
                    if verbose:
                        print(f"\n🔧 Found {len(tool_calls)} tool call(s)")

                    tool_results = []
                    for tool_name, tool_args in tool_calls:
                        if verbose:
                            if self.use_rich:
                                self.console.print(f"\n[cyan]🔧 Calling: {tool_name}[/cyan]")
                                if tool_args:
                                    self.console.print(f"   [dim]Args: {tool_args}[/dim]")
                            else:
                                print(f"\n   Calling: {tool_name}")
                                if tool_args:
                                    print(f"   Args: {tool_args}")

                        if tool_name in TOOL_EXECUTORS:
                            result = TOOL_EXECUTORS[tool_name](self.executor, **tool_args)
                            tool_results.append((tool_name, result))

                            if verbose:
                                if self.use_rich:
                                    result_str = str(result)[:300]
                                    style = "green" if result.success else "red"
                                    self.console.print(f"   [{style}]Result: {result_str}[/{style}]")
                                else:
                                    print(f"   Result: {str(result)[:300]}")
                        else:
                            if verbose:
                                print(f"   ⚠️  Unknown tool: {tool_name}")

                    # Add tool results to conversation
                    if tool_results:
                        results_text = "\n".join([
                            f"[{name} result]: {json.dumps(r.to_dict(), default=str)}"
                            for name, r in tool_results
                        ])
                        self.conversation_history.append({
                            "role": "assistant",
                            "content": assistant_message
                        })
                        self.conversation_history.append({
                            "role": "user",
                            "content": f"Tool execution results:\n{results_text}"
                        })
                        continue  # Continue to next turn

                # No tool calls - we have final response
                break

            except Exception as e:
                if verbose:
                    print(f"\n❌ Error: {e}")
                self.conversation_history.append({
                    "role": "assistant",
                    "content": f"Error: {e}"
                })
                break

        return final_response

    def _parse_tool_calls(self, content: str) -> List[Tuple[str, Dict]]:
        """Parse tool calls from model output."""
        tool_calls = []

        # Pattern: <tool>name(arg1="val1", arg2=val2)</tool>
        pattern = r'<tool>(\w+)\(([^)]*)\)</tool>'

        for match in re.finditer(pattern, content, re.DOTALL):
            name = match.group(1)
            args_str = match.group(2).strip()
            args = self._parse_args(args_str)
            tool_calls.append((name, args))

        # Fallback: Look for bare tool calls without XML tags
        if not tool_calls:
            # Pattern: name(command="...")
            bare_pattern = r'(execute_bash|read_file|write_file|list_dir|web_search|fetch_url|execute_python)\s*\(\s*(command|path|content|query|url|code)\s*=\s*"([^"]+)"\s*\)'
            for match in re.finditer(bare_pattern, content, re.IGNORECASE):
                name = match.group(1)
                arg_name = match.group(2)
                arg_value = match.group(3)
                tool_calls.append((name, {arg_name: arg_value}))

        return tool_calls

    def _parse_args(self, args_str: str) -> Dict:
        """Parse tool arguments from string."""
        args = {}
        if not args_str.strip():
            return args

        # Match: key="value" or key=value or key=true/false
        patterns = [
            (r'(\w+)="([^"]*)"', lambda m: (m.group(1), m.group(2))),  # key="value"
            (r"(\w+)='([^']*)'", lambda m: (m.group(1), m.group(2))),  # key='value'
            (r'(\w+)=true\b', lambda m: (m.group(1), True)),  # key=true
            (r'(\w+)=false\b', lambda m: (m.group(1), False)),  # key=false
            (r'(\w+)=(-?\d+)\b', lambda m: (m.group(1), int(m.group(2)))),  # key=number
            (r'(\w+)=([^\s,]+)', lambda m: (m.group(1), m.group(2))),  # key=value
        ]

        for pattern, extractor in patterns:
            for match in re.finditer(pattern, args_str, re.IGNORECASE):
                key, value = extractor(match)
                args[key] = value

        return args

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        print("🧹 Conversation history cleared")

    def get_stats(self) -> Dict:
        """Get agent statistics."""
        return {
            "turns": len(self.conversation_history),
            "tool_calls": len(self.executor.get_history()),
            "cache_size": len(self.executor.cache),
            "model": self.model
        }


def main():
    # Get defaults from config.yaml
    default_url = config.get_api_url()
    default_model = config.get_model_key()
    default_temp = config.get('advanced', 'temperature', default=0.7)

    parser = argparse.ArgumentParser(description="Local LLM Agent with Tool Calling")
    parser.add_argument("prompt", nargs="?", help="Prompt to send")
    parser.add_argument("--chat", action="store_true", help="Interactive mode")
    parser.add_argument("--verbose", action="store_true", help="Verbose output", default=True)
    parser.add_argument("--url", type=str, default=default_url, help="API base URL")
    parser.add_argument("--model", type=str, default=default_model, help="Model name")
    parser.add_argument("--max-turns", type=int, default=15, help="Max conversation turns")
    parser.add_argument("--temperature", type=float, default=default_temp, help="Model temperature")
    parser.add_argument("--no-cache", action="store_true", help="Disable result caching")
    args = parser.parse_args()

    agent = Agent(
        base_url=args.url,
        model=args.model,
        max_turns=args.max_turns,
        temperature=args.temperature
    )

    if args.no_cache:
        agent.executor.cache_enabled = False

    print("╔══════════════════════════════════════════════════════════╗")
    print("║     Local LLM Advanced Agent                             ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print(f"Model: {config.get_model_key()}")
    print(f"Server: {config.get_api_url()}")
    print()
    print("🛠️  Available Tools:")
    for tool in TOOLS:
        fn = tool["function"]
        print(f"   • {fn['name']}: {fn['description']}")
    print()
    print("💬 Commands: /quit, /clear, /stats, /history, /cache")
    print()

    if args.chat:
        while True:
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Goodbye!")
                break

            if not user_input:
                continue

            cmd = user_input.lower()
            if cmd in ("/quit", "/exit"):
                print("\n👋 Goodbye!")
                break

            if cmd == "/clear":
                agent.clear_history()
                continue

            if cmd == "/stats":
                stats = agent.get_stats()
                print(f"\n📊 Stats: {json.dumps(stats, indent=2)}")
                continue

            if cmd == "/history":
                history = agent.executor.get_history()
                print(f"\n📜 Tool History ({len(history)} calls):")
                for h in history[-5:]:
                    print(f"   • {h['tool']}: {h.get('command') or h.get('path') or h.get('query') or '...'}")
                continue

            if cmd == "/cache":
                print(f"\n💾 Cache: {len(agent.executor.cache)} entries")
                continue

            response = agent.chat(user_input, verbose=args.verbose)

            # Display final response with rich markdown
            if agent.use_rich:
                agent.console.print()
                agent.console.print(Panel(
                    Markdown(response),
                    title="🤖 Assistant",
                    border_style="green",
                    box=box.ROUNDED
                ))
            else:
                print(f"\n🤖 Assistant: {response}")
            print()

    elif args.prompt:
        response = agent.chat(args.prompt, verbose=True)

        # Display final response with rich markdown
        if agent.use_rich:
            agent.console.print()
            agent.console.print(Panel(
                Markdown(response),
                title="🤖 Assistant",
                border_style="green",
                box=box.ROUNDED
            ))
        else:
            print(f"\n🤖 Assistant: {response}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
