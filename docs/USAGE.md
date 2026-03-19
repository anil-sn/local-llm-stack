# Usage Guide - Local LLM Stack

## Quick Reference

### 🚀 Most Common Commands

```bash
# Run any model (background by default)
llm-stack run <model> --chat

# Get recommendations for your hardware
llm-stack model recommend

# Check what's running
llm-stack status
```

---

## Running Models

### Background Mode (Default)

```bash
# Config model
llm-stack run llama-3-8b --chat

# HuggingFace model
llm-stack run unsloth/Qwen3.5-9B-GGUF:Q4_K_M --webui

# Custom quantization
llm-stack run HauhauCS/Qwen3.5-9B-Uncensored-HauhauCS-Aggressive:Q4_K_M --api
```

**What happens:**
1. ✅ Resolves model identifier
2. ✅ Detects hardware (GPU/CPU/RAM)
3. ✅ Downloads if needed
4. ✅ Auto-optimizes settings
5. ✅ Starts server in background
6. ✅ Opens chat/WebUI (if requested)

### Foreground Mode (Debugging)

```bash
# Run in foreground
llm-stack run llama-3-8b --fg

# With chat interface
llm-stack run llama-3-8b --fg --chat
```

**Use when:**
- Debugging startup issues
- Need to see server logs in real-time
- Testing configuration changes

### Model Identifier Formats

```bash
# Config key (from config.yaml)
llm-stack run llama-3-8b

# HuggingFace repo with quantization
llm-stack run unsloth/Qwen3.5-9B-GGUF:Q4_K_M

# HuggingFace repo with custom filename
llm-stack run TheBloke/Llama-2-7B-GGUF:Q5_K_M

# Full HuggingFace URL
llm-stack run "https://huggingface.co/unsloth/Qwen3.5-9B-GGUF"
```

---

## Hardware Auto-Optimization

### What Gets Optimized

| Setting | Auto-Detection | Override |
|---------|---------------|----------|
| **GPU Layers** | Based on VRAM | `--gpu-layers` |
| **Context Size** | Based on RAM | `--context` |
| **Batch Size** | Based on VRAM | `--batch-size` |
| **Threads** | CPU core count | `--threads` |
| **Flash Attention** | GPU capability | `--flash-attn` |

### Example Outputs

**RTX 4090 (24GB VRAM, 64GB RAM):**
```
✅ GPU: NVIDIA GeForce RTX 4090 (24.0GB VRAM)
✅ CPU: AMD Ryzen 9 7950X3D (32 cores)
✅ RAM: 62.0GB total, 53.9GB available

Optimized settings:
   GPU Layers: 999 (full offload)
   Context: 32768
   Batch Size: 512
   Threads: 16
```

**Apple M2 (16GB Unified Memory):**
```
✅ GPU: Apple Silicon GPU (Metal)
✅ CPU: Apple M2 (8 cores)
✅ RAM: 16.0GB total, 12.0GB available

Optimized settings:
   GPU Layers: 999 (full offload)
   Context: 16384
   Batch Size: 256
   Threads: 4
```

---

## Model Management

### Get Recommendations

```bash
# Default recommendations
llm-stack model recommend

# For specific use case
llm-stack model recommend --use-case code
llm-stack model recommend --use-case reasoning

# Prioritize speed or quality
llm-stack model recommend --priority speed
llm-stack model recommend --priority quality
```

**Example Output:**
```
🔍 Analyzing your hardware...

Your System:
  GPU: NVIDIA GeForce RTX 4090 (24.0GB VRAM)
  CPU: AMD Ryzen 9 7950X3D (32 cores)
  RAM: 62.0GB total, 53.9GB available

📦 Recommended Models (general, balanced):

           Top Recommendations
╭───────┬──────────────────────┬──────┬──────┬──────┬───────┬──────────────╮
│ Rank  │ Model                │ Size │ VRAM │  RAM │ Score │ Command      │
├───────┼──────────────────────┼──────┼──────┼──────┼───────┼──────────────┤
│ ⭐ #1 │ Qwen3.5-9B           │  7GB │  8GB │ 16GB │ ⭐ 93 │ run qwen3... │
│  #2   │ Llama-3-8B           │  5GB │  6GB │ 16GB │ ⭐ 90 │ run llama... │
│  #3   │ Gemma-2-7B           │  5GB │  6GB │ 16GB │ ⭐ 88 │ run gemma... │
╰───────┴──────────────────────┴──────┴──────┴──────┴───────┴──────────────╯
```

### List Models

```bash
# List all configured models
llm-stack model list

# With verbose info
llm-stack model list --verbose
```

### Download Models

```bash
# Download active model from config
llm-stack model download

# Download specific model
llm-stack model download llama-3-8b

# Download with custom quantization
llm-stack model download qwen-35b-a3b --quantization Q4_K_S
```

### Validate Models

```bash
# Validate active model
llm-stack model validate

# Validate specific model
llm-stack model validate llama-3-8b
```

### Delete Models

```bash
# Delete active model
llm-stack model delete

# Delete specific model
llm-stack model delete mistral-7b

# Force delete (no confirmation)
llm-stack model delete mistral-7b --force
```

---

## Server Management

### Start/Stop

```bash
# Start server (background)
llm-stack server start

# Stop server
llm-stack server stop

# Restart server
llm-stack server restart

# Force restart
llm-stack server restart --force
```

### Status & Logs

```bash
# Check server status
llm-stack status

# View server logs
llm-stack server logs

# Follow logs (like tail -f)
llm-stack server logs --follow

# Show last 100 lines
llm-stack server logs --lines 100
```

### Custom Server Configuration

```bash
# Custom port
llm-stack server start --port 9000

# Custom context size
llm-stack server start --context 65536

# Custom GPU layers
llm-stack server start --gpu-layers 50

# Multiple options
llm-stack server start --port 9000 --context 32768 --gpu-layers 999
```

---

## Chat Interfaces

### Interactive Chat

```bash
# Start interactive chat
llm-stack chat interactive

# With custom port
llm-stack chat interactive --port 9000

# With system prompt
llm-stack chat interactive --system "You are a helpful coding assistant."
```

**Commands in chat:**
- `/exit` or `/quit` - Exit chat
- `/clear` - Clear conversation history
- `/help` - Show help

### Quick Chat

```bash
# Ask a quick question
llm-stack chat quick "What is Python?"

# With custom model
llm-stack chat quick "Explain quantum computing" --model llama-3-8b
```

### Agent Mode

```bash
# Interactive agent
llm-stack chat agent

# Single task
llm-stack chat agent "Find all Python files with TODO comments"
```

**Available Tools:**
- `execute_bash` - Run shell commands
- `read_file` - Read file contents
- `write_file` - Write to files
- `list_dir` - List directory contents
- `web_search` - Search the web
- `execute_python` - Run Python code

---

## API Usage

### OpenAI-Compatible API

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8081/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="model-name",
    messages=[
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hello!"}
    ],
    max_tokens=100,
    temperature=0.7
)

print(response.choices[0].message.content)
print(f"Tokens: {response.usage.total_tokens}")
print(f"Speed: {response.timings.predicted_per_second} tok/s")
```

### curl Examples

```bash
# Health check
curl http://localhost:8081/health

# List models
curl http://localhost:8081/v1/models

# Chat completion
curl http://localhost:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 100
  }'
```

---

## Common Workflows

### Workflow 1: Quick Test

```bash
# Test a model quickly
llm-stack run mistral-7b --chat

# Exit with /quit
```

### Workflow 2: Production Setup

```bash
# Start server in background
llm-stack run llama-3-8b --api --port 8081

# Use from your application
# API available at http://localhost:8081/v1
```

### Workflow 3: Model Comparison

```bash
# Try different models
llm-stack run mistral-7b --chat
llm-stack run qwen3.5-9b --chat
llm-stack run llama-3-8b --chat

# Pick the best one for your use case
```

### Workflow 4: Maximum Performance

```bash
# Get best model for your hardware
llm-stack model recommend --priority quality

# Run with maximum context
llm-stack run llama-3-70b --context 131072 --bg
```

---

## Troubleshooting

### Server Won't Start

```bash
# Check if port is in use
lsof -i :8081

# Stop existing server
llm-stack server stop

# Check logs
llm-stack server logs

# Try foreground mode for debugging
llm-stack run llama-3-8b --fg
```

### Out of Memory

```bash
# Reduce context size
llm-stack run llama-3-8b --context 16384 --chat

# Use smaller model
llm-stack run mistral-7b --chat

# Reduce batch size
llm-stack server start --batch-size 256
```

### Download Failed

```bash
# Check disk space
df -h ~/models

# Clear partial downloads
rm -f ~/models/*.gguf.incomplete

# Try manual download
huggingface-cli download \
  --local-dir ~/models \
  unsloth/Qwen3.5-9B-GGUF \
  --include "Qwen3.5-9B-UD-Q4_K_M.gguf"
```

### Slow Performance

```bash
# Check GPU offloading
llm-stack status

# Verify GPU layers
nvidia-smi  # Should show GPU usage

# Reduce context size
llm-stack run llama-3-8b --context 8192 --chat
```

---

## Environment Variables

```bash
# Custom models directory
export LOCAL_LLM_MODELS_DIR=~/my-models

# Custom cache directory
export HF_HOME=~/.cache/huggingface

# Enable HF transfer (faster downloads)
export HF_HUB_ENABLE_HF_TRANSFER=1
```

---

## Configuration Files

### config.yaml Location

- **Default:** `./config.yaml` (project root)
- **Override:** `--config /path/to/config.yaml`

### Model Storage

- **Default:** `~/models/`
- **Override:** Set in `config.yaml` or use `LOCAL_LLM_MODELS_DIR`

### Server Logs

- **Default:** `/tmp/llama-server.log`
- **View:** `llm-stack server logs`

---

## Performance Tips

### For Best Speed

1. Use smaller models (7B-9B)
2. Maximize GPU offload
3. Use Q4_K_M or Q5_K_M quantization
4. Reduce context size if not needed

### For Best Quality

1. Use larger models (35B-70B)
2. Use Q6_K or Q8_0 quantization
3. Maximize context size
4. Increase batch size if VRAM allows

### For Low RAM Systems

1. Use 7B or smaller models
2. Reduce context to 8192 or less
3. Use Q4_K_S quantization
4. Run in CPU-only mode if needed

---

## Next Steps

- **API Reference:** See `docs/API.md`
- **CLI Reference:** See `docs/CLI-REFERENCE.md`
- **Model Guide:** See `MODELS.md`
- **Benchmarks:** See `tools/benchmarks/README.md`
