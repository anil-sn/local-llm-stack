# Claude Code CLI Integration

Use this local LLM stack as a custom backend for **Claude Code CLI**, enabling you to use Qwen, Llama, Mistral, and other models with Claude Code.

---

## Quick Start

### 1. Start the Local Server

```bash
./bin/start-webui.sh
```

### 2. Configure Environment

**Option A: Automatic (Recommended)**
```bash
source scripts/claude-code.sh
```

**Option B: Manual**
```bash
source claude-code-env.sh
```

**Option C: One-liner**
```bash
export ANTHROPIC_BASE_URL=http://localhost:8080 && \
export ANTHROPIC_AUTH_TOKEN=dummy && \
export CLAUDE_CODE_DISABLE_TELEMETRY=1 && \
claude
```

### 3. Run Claude Code

```bash
claude
```

---

## How It Works

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Claude Code    │────▶│  Local LLM       │────▶│  Qwen/Llama/    │
│  CLI            │     │  Server (8080)   │     │  Mistral/etc.   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
       │                       │
       │  Anthropic API        │  llama.cpp
       │  Compatible           │  OpenAI Compatible
       ▼                       ▼
```

Claude Code thinks it's talking to Anthropic, but it's actually using your local model!

---

## Environment Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `CLAUDE_CODE_DISABLE_TELEMETRY` | `1` | Disable remote telemetry |
| `ANTHROPIC_API_KEY` | (unset) | Remove Anthropic key |
| `ANTHROPIC_AUTH_TOKEN` | `dummy` | Dummy token (required by CLI) |
| `ANTHROPIC_BASE_URL` | `http://localhost:8080` | Point to local server |
| `ANTHROPIC_MODEL` | Model name | Current model from config |

---

## Configuration

### config.yaml Settings

```yaml
claude_code:
  enabled: true              # Enable integration
  disable_telemetry: true    # Disable analytics
  auth_token: "dummy"        # Required dummy token
  timeout: 300               # Request timeout (seconds)
  max_tokens: 8192           # Max response tokens
  alias: ""                  # Custom model name (optional)
```

### Model Selection

The model name is automatically set from your `active_model` in `config.yaml`:

```yaml
active_model: "qwen-35b-a3b"  # Claude Code will use this model
```

---

## Usage Examples

### Interactive Mode

```bash
# Start server
./bin/start-webui.sh

# Configure environment
source scripts/claude-code.sh

# Run Claude Code interactively
claude
```

### Single Command

```bash
source scripts/claude-code.sh
claude "Explain quantum computing in 3 sentences"
```

### With Specific Model

```bash
# Switch to Llama 3
sed -i '' 's/active_model: "qwen-35b-a3b"/active_model: "llama-3-70b"/' config.yaml

# Download and start
./bin/download-model.sh
./bin/start-webui.sh

# Use with Claude Code
source scripts/claude-code.sh
claude "Write a Python function to sort a list"
```

---

## Troubleshooting

### Server Not Running

```bash
# Check if server is running
curl http://localhost:8080/health

# Start if needed
./bin/start-webui.sh
```

### Model Not Found

```bash
# Check active model
source scripts/config.sh
echo $MODEL_NAME

# Verify file exists
ls -lh $MODEL_PATH
```

### Claude Code Still Using Remote API

```bash
# Verify environment
echo $ANTHROPIC_BASE_URL  # Should be http://localhost:8080
echo $ANTHROPIC_AUTH_TOKEN  # Should be "dummy"
echo $CLAUDE_CODE_DISABLE_TELEMETRY  # Should be 1
```

### Slow Responses

1. **Check GPU offloading:**
   ```bash
   grep "offloading" /tmp/llama-server.log
   ```

2. **Reduce context size in config.yaml:**
   ```yaml
   server:
     context_size: 65536  # Reduce from 131072
   ```

3. **Use smaller model:**
   ```yaml
   active_model: "llama-3-8b"  # or "phi-3-mini"
   ```

---

## Performance Comparison

| Model | Speed (tok/s) | Quality | Best For |
|-------|---------------|---------|----------|
| Qwen3.5-35B | ~35 | ⭐⭐⭐⭐⭐ | General use |
| Llama-3-70B | ~25 | ⭐⭐⭐⭐⭐ | Complex tasks |
| Llama-3-8B | ~50 | ⭐⭐⭐⭐ | Quick tasks |
| Mistral-7B | ~55 | ⭐⭐⭐⭐ | Fast responses |
| Phi-3-Mini | ~70 | ⭐⭐⭐ | Ultra-fast |

---

## Advanced Usage

### Custom Model Alias

Give your model a friendly name for Claude Code:

```yaml
claude_code:
  alias: "my-local-qwen"  # Claude Code will see this name
```

### Multiple Configurations

Create environment-specific configs:

```bash
# Development (fast, small model)
cp config.yaml config.dev.yaml
# Edit config.dev.yaml: active_model: "phi-3-mini"

# Production (best quality)
cp config.yaml config.prod.yaml
# Edit config.prod.yaml: active_model: "llama-3-70b"
```

### Auto-Start Script

Create a wrapper script:

```bash
#!/bin/bash
# ~/bin/claude-local

cd /path/to/project
./bin/start-webui.sh &
sleep 5
source scripts/claude-code.sh
claude "$@"
```

---

## Security Notes

⚠️ **Important:**

1. **Local Only**: This setup is for local development only
2. **No Authentication**: The local server has no auth - don't expose to internet
3. **Dummy Token**: The `dummy` token is only for CLI compatibility
4. **Firewall**: Ensure port 8080 is not exposed externally

---

## See Also

- [config.yaml](../config.yaml) - Full configuration
- [MODELS.md](MODELS.md) - Model switching guide
- [README.md](README.md) - Main documentation
- [Claude Code Docs](https://docs.anthropic.com/claude-code/) - Official docs

---

## Quick Reference

```bash
# Start everything
./bin/start-webui.sh && source scripts/claude-code.sh && claude

# Check status
curl http://localhost:8080/health

# Stop server
./bin/stop-server.sh

# Switch model
sed -i '' 's/active_model: "[^"]*"/active_model: "llama-3-8b"/' config.yaml
./bin/download-model.sh
./bin/start-webui.sh
```
