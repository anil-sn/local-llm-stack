# Local LLM Stack CLI - Complete Command Reference

**Version:** 1.0.0  
**Last Updated:** 2026-03-02

---

## 📋 Quick Reference

### Status Commands
```bash
# Complete system overview
llm-stack status all

# Individual status checks
llm-stack status system      # CPU, GPU, RAM, Disk
llm-stack status server      # Server running status
llm-stack status model       # Active model status
llm-stack status dependencies # Installed dependencies
```

### Server Management
```bash
# Start server (background, uses config.yaml)
llm-stack server start

# Start with custom settings
llm-stack server start --port 9000 --context 32768
llm-stack server start --gpu-layers 35
llm-stack server start --foreground  # Run in foreground

# Stop server
llm-stack server stop
llm-stack server stop --force  # Force kill

# Restart server
llm-stack server restart

# Check server status
llm-stack server status

# View logs
llm-stack server logs          # Last 50 lines
llm-stack server logs -n 100   # Last 100 lines
llm-stack server logs --follow # Follow in real-time
```

### Chat Commands
```bash
# Interactive terminal chat
llm-stack chat interactive
llm-stack chat interactive --context 32768
llm-stack chat interactive -s "You are a coding assistant"

# Quick single-turn chat
llm-stack chat quick 'Hello!'
llm-stack chat quick 'What is quantum computing?'

# Agent mode (with tools)
llm-stack chat agent
llm-stack chat agent 'Find Python files with TODO'
```

### Model Management
```bash
# List all models
llm-stack model list
llm-stack model list --verbose

# Model information
llm-stack model info                    # Active model
llm-stack model info llama-3-8b        # Specific model

# Download model
llm-stack model download
llm-stack model download llama-3-8b
llm-stack model download -q Q4_K_S     # Specific quantization

# Validate model
llm-stack model validate
llm-stack model validate llama-3-8b

# Delete model
llm-stack model delete
llm-stack model delete llama-3-8b
llm-stack model delete --force         # Skip confirmation
```

### Configuration
```bash
# Show configuration
llm-stack config show                   # Summary
llm-stack config show server           # Server section
llm-stack config show models           # Models section
llm-stack config show api              # API section
llm-stack config show advanced         # Advanced settings
llm-stack config show --raw            # Raw YAML

# Validate configuration
llm-stack config validate

# Edit configuration (opens in $EDITOR)
llm-stack config edit

# List model configs
llm-stack config models
```

### Benchmarks
```bash
# Run all benchmarks
llm-stack benchmark run
llm-stack benchmark run -t all         # All types
llm-stack benchmark run -t native      # Native only
llm-stack benchmark run -t api         # API only
llm-stack benchmark run -r 5           # 5 repetitions

# Individual benchmarks
llm-stack benchmark native             # llama-bench
llm-stack benchmark native -p 512 -g 128
llm-stack benchmark api                # API latency
llm-stack benchmark api -p 8081 -r 3

# Compare results
llm-stack benchmark compare
llm-stack benchmark compare result1.json result2.json

# Clean results
llm-stack benchmark clean
```

---

## 🔧 Complete Command List

### Main CLI
| Command | Description |
|---------|-------------|
| `llm-stack --help` | Show help |
| `llm-stack --version` | Show version (-v) |
| `llm-stack --install-completion` | Install shell completion |

### Server (5 commands)
| Command | Description |
|---------|-------------|
| `llm-stack server start` | Start server |
| `llm-stack server stop` | Stop server |
| `llm-stack server restart` | Restart server |
| `llm-stack server status` | Check status |
| `llm-stack server logs` | View logs |

### Model (5 commands)
| Command | Description |
|---------|-------------|
| `llm-stack model list` | List models |
| `llm-stack model info` | Model details |
| `llm-stack model download` | Download model |
| `llm-stack model delete` | Delete model |
| `llm-stack model validate` | Validate model |

### Chat (3 commands)
| Command | Description |
|---------|-------------|
| `llm-stack chat interactive` | Interactive chat |
| `llm-stack chat quick` | Quick chat |
| `llm-stack chat agent` | Agent mode |

### Benchmark (5 commands)
| Command | Description |
|---------|-------------|
| `llm-stack benchmark run` | Run suite |
| `llm-stack benchmark native` | Native benchmark |
| `llm-stack benchmark api` | API benchmark |
| `llm-stack benchmark compare` | Compare results |
| `llm-stack benchmark clean` | Clean results |

### Config (4 commands)
| Command | Description |
|---------|-------------|
| `llm-stack config show` | Show config |
| `llm-stack config edit` | Edit config |
| `llm-stack config validate` | Validate config |
| `llm-stack config models` | List models |

### Status (5 commands)
| Command | Description |
|---------|-------------|
| `llm-stack status system` | System info |
| `llm-stack status server` | Server status |
| `llm-stack status model` | Model status |
| `llm-stack status dependencies` | Dependencies |
| `llm-stack status all` | Complete overview |

**Total: 28 commands** across 6 command groups

---

## 🎯 Common Workflows

### First Time Setup
```bash
# 1. Check system
llm-stack status system

# 2. Check configuration
llm-stack config show

# 3. Download model
llm-stack model download

# 4. Validate model
llm-stack model validate

# 5. Start server
llm-stack server start

# 6. Test chat
llm-stack chat interactive
```

### Daily Use
```bash
# 1. Check if server is running
llm-stack status server

# 2. Start if needed
llm-stack server start

# 3. Chat
llm-stack chat interactive

# 4. Check status anytime
llm-stack status
```

### Model Management
```bash
# List available models
llm-stack model list --verbose

# Switch to different model (edit config.yaml)
llm-stack config edit
# Change: active_model: "llama-3-8b"

# Download new model
llm-stack model download llama-3-8b

# Validate
llm-stack model validate llama-3-8b
```

### Performance Testing
```bash
# Check GPU status
llm-stack status system

# Run benchmarks
llm-stack benchmark run

# Compare results
llm-stack benchmark compare

# Check server performance
llm-stack status server
```

### Troubleshooting
```bash
# Check all dependencies
llm-stack status dependencies

# Validate configuration
llm-stack config validate

# Check server logs
llm-stack server logs --follow

# Check system resources
llm-stack status system
```

---

## ⚡ Power User Tips

### Combine Commands
```bash
# Quick status check
llm-stack status all | head -50

# Watch server logs while chatting
llm-stack server logs --follow &
llm-stack chat interactive

# Check model then start server
llm-stack model info && llm-stack server start
```

### Custom Settings
```bash
# Temporary port change
llm-stack server start --port 9000

# Reduced context for faster response
llm-stack server start --context 32768

# CPU-only mode (no GPU)
llm-stack server start --gpu-layers 0

# Custom threads
llm-stack server start --threads 8
```

### Quick One-Liners
```bash
# Test API is working
curl http://localhost:8081/health

# Quick question without entering chat
llm-stack chat quick 'What is 2+2?'

# Check if specific model exists
llm-stack model info llama-3-8b | grep Status
```

### Shell Aliases (add to ~/.zshrc)
```bash
# Quick status
alias llm-status='llm-stack status all'

# Quick chat
alias llm-chat='llm-stack chat interactive'

# Quick server control
alias llm-start='llm-stack server start'
alias llm-stop='llm-stack server stop'

# Quick model info
alias llm-model='llm-stack model info'
```

---

## 🛠️ Command Options Reference

### Server Start Options
```bash
llm-stack server start [MODEL_PATH] [OPTIONS]

Options:
  -p, --port INTEGER        Server port (default: 8081)
  -c, --context INTEGER     Context size (default: 131072)
  -t, --threads INTEGER     Number of threads (auto-detect)
  -gl, --gpu-layers INTEGER GPU layers (default: 999)
  -b, --background / -f, --foreground
                            Run in background (default) or foreground
  -v, --verbose             Show verbose output
```

### Model Download Options
```bash
llm-stack model download [MODEL_KEY] [OPTIONS]

Options:
  -q, --quantization TEXT   Quantization type (e.g., Q4_K_S)
  -o, --output DIRECTORY    Output directory
  -f, --force               Overwrite existing file
```

### Chat Interactive Options
```bash
llm-stack chat interactive [MODEL_PATH] [OPTIONS]

Options:
  -c, --context INTEGER     Context size
  -t, --threads INTEGER     Number of threads
  -s, --system-prompt TEXT  System prompt
```

### Benchmark Run Options
```bash
llm-stack benchmark run [OPTIONS]

Options:
  -t, --type TEXT           Benchmark type: all, native, batched, 
                            perplexity, api (default: all)
  -r, --repetitions INTEGER Number of repetitions
  -o, --output DIRECTORY    Output directory for results
```

### Status System Shows
```bash
llm-stack status system

Output:
  🖥️  System Information
  
  Platform    darwin (Darwin)
  Machine     arm64
  Python      3.14.3
  
  GPU         ✅ Apple M4 Pro (Metal)
  GPU Type    METAL
  Layers      999
  
  CPU Cores   14
  
  Memory Total      48.0 GB
  Memory Available  2.0 GB
  Memory Usage      95.8%
  
  Disk Total  460.4 GB
  Disk Used   308.5 GB
  Disk Free   152.0 GB
  Disk Usage  67.0%
```

---

## 📝 Help System

```bash
# General help
llm-stack --help

# Command group help
llm-stack server --help
llm-stack model --help
llm-stack chat --help
llm-stack benchmark --help
llm-stack config --help
llm-stack status --help

# Specific command help
llm-stack server start --help
llm-stack model download --help
llm-stack chat interactive --help
```

---

## 🔑 Key Bindings (Interactive Chat)

When using `llm-stack chat interactive`:

| Key/Command | Action |
|-------------|--------|
| `/exit` or `/quit` | Exit chat |
| `/clear` | Clear conversation history |
| `Ctrl+C` | Cancel current response |
| `Ctrl+D` | Exit chat |

---

## 📊 Configuration Quick Reference

### Edit config.yaml
```bash
llm-stack config edit
```

### Key Settings
```yaml
# Active model
active_model: "qwen-35b-a3b"

# Server settings
server:
  port: 8081
  context_size: 131072
  gpu_layers: 999

# Advanced settings
advanced:
  temperature: 0.7
  top_p: 0.9
  repeat_penalty: 1.1
```

### Validate Configuration
```bash
llm-stack config validate
```

---

## 🚨 Troubleshooting Commands

### Server Won't Start
```bash
# Check if port is in use
llm-stack status server

# Check logs
llm-stack server logs

# Check dependencies
llm-stack status dependencies

# Validate config
llm-stack config validate
```

### Model Not Found
```bash
# Check model status
llm-stack status model

# List available models
llm-stack model list

# Download model
llm-stack model download

# Validate model
llm-stack model validate
```

### Slow Performance
```bash
# Check GPU is being used
llm-stack status system

# Check server configuration
llm-stack status server

# Run benchmarks
llm-stack benchmark run
```

---

## 📚 Additional Resources

| Document | Description |
|----------|-------------|
| [README.md](../README.md) | Main documentation |
| [CLI-IMPLEMENTATION.md](CLI-IMPLEMENTATION.md) | CLI implementation details |
| [GPU-AUTODETECTION.md](GPU-AUTODETECTION.md) | GPU detection guide |
| [METAL-CRASH-FIX.md](METAL-CRASH-FIX.md) | Metal crash workaround |
| [TEST-REPORT.md](TEST-REPORT.md) | Test results |

---

**For more information:** `llm-stack --help`

**Report issues:** https://github.com/anil-sn/local-llm-stack/issues
