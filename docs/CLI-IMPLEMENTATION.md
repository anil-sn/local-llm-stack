# Local LLM Stack - Professional CLI Implementation

## Overview

This document describes the professional CLI implementation for Local LLM Stack, following Python best practices and professional naming conventions.

## What Was Created

### 1. Python Package Structure (`src/local_llm/`)

```
src/local_llm/
├── __init__.py              # Package initialization
├── config.py                # Configuration management
├── requirements.txt         # Python dependencies
├── utils/
│   └── __init__.py          # Cross-platform utilities
└── cli/
    ├── main.py              # Typer CLI entry point
    └── commands/
        ├── __init__.py
        ├── server.py        # Server management commands
        ├── model.py         # Model management commands
        ├── chat.py          # Chat and agent commands
        ├── benchmark.py     # Benchmark commands
        ├── config.py        # Configuration commands
        └── status.py        # Status check commands
```

### 2. Cross-Platform Utilities (`src/local_llm/utils/`)

Professional cross-platform system utilities:

- **System Information**: CPU count, RAM, disk usage (macOS/Linux compatible)
- **Process Management**: Port checking, process detection, graceful shutdown
- **File Operations**: Path expansion, directory creation, size formatting
- **Command Detection**: Cross-platform command availability checking

**Key Features:**
- macOS: Uses `sysctl`, `vm_stat` for system info
- Linux: Uses `/proc/meminfo`, `/proc/cpuinfo`
- Graceful fallbacks when tools unavailable
- No hardcoded platform assumptions

### 3. Configuration Management (`src/local_llm/config.py`)

Professional configuration handling:

- **Type-safe access**: Properties with proper type hints
- **Validation**: Checks for required fields and valid values
- **Path resolution**: Handles `$HOME`, `~`, relative paths
- **Active model tracking**: Automatic loading of active model config
- **Error handling**: Clear error messages for configuration issues

### 4. CLI Implementation (`src/local_llm/cli/`)

Built with **Typer** for professional CLI experience:

#### Command Groups

| Command | Description | Key Features |
|---------|-------------|--------------|
| `llm-stack server` | Server management | start/stop/restart/logs/status |
| `llm-stack model` | Model management | list/download/validate/delete |
| `llm-stack chat` | Chat interfaces | interactive/quick/agent |
| `llm-stack benchmark` | Benchmarks | run/compare/clean |
| `llm-stack config` | Configuration | show/edit/validate |
| `llm-stack status` | System status | system/server/model/dependencies |

#### CLI Features

- **Rich output**: Beautiful tables, panels, and formatting
- **Help system**: Comprehensive `--help` for all commands
- **Validation**: Checks dependencies, files, ports before operations
- **Error handling**: Clear error messages with suggestions
- **Progress indicators**: Spinners and progress bars for long operations
- **Cross-platform**: Works on macOS and Linux

### 5. Project Configuration Files

**setup.py**: Traditional Python package setup
**pyproject.toml**: Modern Python project configuration
- Build system specification
- Package metadata
- Development dependencies
- Tool configurations (black, ruff, myypy, pytest)

### 6. Updated Scripts

**bin/install-cli.sh**: Install the Python CLI
**bin/llm-stack**: Wrapper script for CLI
**bin/chat-cli**, **bin/agent**, **bin/start-webui.sh**, etc.: Updated with deprecation notices

### 7. Documentation

**docs/CLI-REFERENCE.md**: Complete CLI command reference
**README.md**: Updated with CLI usage and new project structure

## Professional Naming Conventions

### Python Modules
- **Lowercase with underscores**: `local_llm`, `config.py`, `cli_commands.py`
- **Descriptive names**: `cross_platform_utils.py`, `configuration_manager.py`

### CLI Commands
- **Verb-noun pattern**: `server start`, `model download`, `chat interactive`
- **Consistent terminology**: "server", "model", "chat", "benchmark", "config", "status"
- **Clear action verbs**: start, stop, restart, list, download, delete, validate, run, show, edit

### Variables and Functions
- **snake_case**: `active_model_key`, `get_system_info()`
- **Descriptive**: `get_available_ram_gb()`, `is_port_in_use()`
- **Type hints**: All functions have proper type annotations

### Classes
- **PascalCase**: `Config`, `ToolResult`, `ToolExecutor`
- **Descriptive**: `ConfigError`, `Agent`

## Cross-Platform Compatibility

### macOS Specific
```python
# CPU count
subprocess.run(["sysctl", "-n", "hw.ncpu"])

# Total RAM
subprocess.run(["sysctl", "-n", "hw.memsize"])

# Available RAM
subprocess.run(["vm_stat"])

# Process on port
subprocess.run(["lsof", "-ti", f":{port}"])
```

### Linux Specific
```python
# CPU count
os.cpu_count()  # or nproc command

# Total/Available RAM
with open("/proc/meminfo") as f:
    # Parse MemTotal, MemAvailable

# Process on port
subprocess.run(["ss", "-tlnp"])
```

### Fallbacks
- Always try multiple methods
- Provide safe defaults
- Never crash on missing tools
- Clear error messages

## Installation

```bash
# Install the CLI
./bin/install-cli.sh

# Or manually
pip install -e .

# Test installation
llm-stack --help
llm-stack status
```

## Usage Examples

```bash
# Check system status
llm-stack status system
llm-stack status server
llm-stack status model

# Server management
llm-stack server start
llm-stack server stop
llm-stack server logs --follow

# Model management
llm-stack model list
llm-stack model download
llm-stack model validate

# Chat
llm-stack chat interactive
llm-stack chat quick "Hello!"
llm-stack chat agent

# Configuration
llm-stack config show
llm-stack config show server
llm-stack config edit

# Benchmarks
llm-stack benchmark run
llm-stack benchmark run -t api
llm-stack benchmark compare
```

## Backward Compatibility

All existing scripts continue to work:
- `./bin/chat-cli` → `llm-stack chat interactive`
- `./bin/agent` → `llm-stack chat agent`
- `./bin/start-webui.sh` → `llm-stack server start`

Legacy scripts show deprecation notices but function normally.

## Testing

```bash
# Test CLI
llm-stack --help
llm-stack status
llm-stack config show
llm-stack model list

# Test cross-platform utils
python -c "from local_llm.utils import get_system_info; print(get_system_info())"

# Test config
python -c "from local_llm.config import Config; c = Config(); print(c.active_model_key)"
```

## Dependencies

**Core:**
- typer >= 0.9.0 (CLI framework)
- rich >= 13.0.0 (Terminal formatting)
- pyyaml >= 6.0 (YAML parsing)
- openai >= 1.0.0 (API client)
- requests >= 2.31.0 (HTTP client)

**Optional:**
- psutil >= 5.9.0 (Enhanced system monitoring)

**Development:**
- pytest, black, ruff, mypy

## File Organization Principles

1. **Separation of Concerns**
   - Utils: Low-level system operations
   - Config: Configuration management
   - CLI: User interface

2. **Single Responsibility**
   - Each module has one clear purpose
   - Each function does one thing well

3. **Discoverability**
   - Logical directory structure
   - Clear naming conventions
   - Comprehensive help system

4. **Maintainability**
   - Type hints throughout
   - Docstrings for all public APIs
   - Consistent code style

## Next Steps

1. ✅ Professional CLI structure created
2. ✅ Cross-platform utilities implemented
3. ✅ Configuration management refactored
4. ✅ All command groups implemented
5. ✅ Documentation updated
6. ⏳ Add unit tests
7. ⏳ Add integration tests
8. ⏳ Add CI/CD pipeline
9. ⏳ Add type checking (mypy)
10. ⏳ Add linting (ruff)

## Summary

The new CLI provides:
- **Professional UX**: Beautiful output, clear help, proper error handling
- **Cross-platform**: Works on macOS and Linux without modification
- **Maintainable**: Clean structure, type hints, good naming
- **Extensible**: Easy to add new commands and features
- **Backward compatible**: Existing scripts still work

All following professional Python conventions and naming standards.
