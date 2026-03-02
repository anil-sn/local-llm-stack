# Local LLM Stack - CLI Quick Reference

## Installation

```bash
# Install the CLI
./bin/install-cli.sh

# Or manually
pip install -e .
```

## Quick Start

```bash
# Check system status
llm-stack status

# Check server status
llm-stack status server

# Check model status
llm-stack status model

# Start the server
llm-stack server start

# Stop the server
llm-stack server stop

# Chat interactively
llm-stack chat interactive

# Quick question
llm-stack chat quick "What is quantum computing?"

# Run agent mode
llm-stack chat agent

# Run benchmarks
llm-stack benchmark run

# View configuration
llm-stack config show
```

## Command Groups

### `llm-stack server` - Server Management

| Command | Description |
|---------|-------------|
| `start` | Start the LLM server |
| `stop` | Stop the server |
| `restart` | Restart the server |
| `status` | Check server status |
| `logs` | View server logs |

**Examples:**

```bash
# Start in background (default)
llm-stack server start

# Start in foreground for debugging
llm-stack server start --foreground

# Start with custom port
llm-stack server start --port 9000

# Stop gracefully
llm-stack server stop

# Force kill
llm-stack server stop --force

# View last 100 log lines
llm-stack server logs --lines 100

# Follow logs in real-time
llm-stack server logs --follow
```

### `llm-stack model` - Model Management

| Command | Description |
|---------|-------------|
| `list` | List all configured models |
| `info` | Show model details |
| `download` | Download a model |
| `delete` | Delete a model |
| `validate` | Validate model file |

**Examples:**

```bash
# List all models
llm-stack model list

# Show detailed info
llm-stack model list --verbose

# Show active model info
llm-stack model info

# Show specific model info
llm-stack model info llama-3-70b

# Download active model
llm-stack model download

# Download specific model
llm-stack model download llama-3-8b

# Delete a model
llm-stack model delete llama-3-8b

# Validate model
llm-stack model validate
```

### `llm-stack chat` - Chat & Agent

| Command | Description |
|---------|-------------|
| `interactive` | Interactive terminal chat |
| `quick` | Quick single-turn chat |
| `agent` | Agent mode with tools |

**Examples:**

```bash
# Interactive chat
llm-stack chat interactive

# With custom context
llm-stack chat interactive --context 32768

# Quick question
llm-stack chat quick "Explain quantum entanglement"

# Agent mode (interactive)
llm-stack chat agent

# Agent task
llm-stack chat agent "Find all Python files with TODO"
```

### `llm-stack benchmark` - Benchmarks

| Command | Description |
|---------|-------------|
| `run` | Run benchmark suite |
| `native` | Run native llama.cpp benchmarks |
| `api` | Run API benchmarks |
| `compare` | Compare results |
| `clean` | Clean results |

**Examples:**

```bash
# Run all benchmarks
llm-stack benchmark run

# Run specific type
llm-stack benchmark run -t native
llm-stack benchmark run -t api

# Custom repetitions
llm-stack benchmark run -r 5

# Compare results
llm-stack benchmark compare
```

### `llm-stack config` - Configuration

| Command | Description |
|---------|-------------|
| `show` | Show configuration |
| `edit` | Edit config file |
| `validate` | Validate config |
| `models` | List model configs |

**Examples:**

```bash
# Show all config
llm-stack config show

# Show specific section
llm-stack config show server
llm-stack config show models

# Show raw YAML
llm-stack config show --raw

# Edit configuration
llm-stack config edit

# Validate config
llm-stack config validate
```

### `llm-stack status` - System Status

| Command | Description |
|---------|-------------|
| `system` | System information |
| `server` | Server status |
| `model` | Model status |
| `dependencies` | Check dependencies |
| `all` | Complete overview |

**Examples:**

```bash
# System info
llm-stack status system

# Server status
llm-stack status server

# Model status
llm-stack status model

# Check dependencies
llm-stack status dependencies

# Everything at once
llm-stack status all
```

## Global Options

| Option | Description |
|--------|-------------|
| `--version`, `-v` | Show version |
| `--help`, `-h` | Show help |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `LLM_STACK_CONFIG` | Custom config path |
| `EDITOR` | Editor for `config edit` |

## Backward Compatibility

Old scripts still work but show deprecation notices:

```bash
./bin/chat-cli          # → llm-stack chat interactive
./bin/agent             # → llm-stack chat agent
./bin/start-webui.sh    # → llm-stack server start
./bin/stop-server.sh    # → llm-stack server stop
```

## Getting Help

```bash
# General help
llm-stack --help

# Command help
llm-stack server --help
llm-stack server start --help

# Subcommand help
llm-stack benchmark run --help
```
