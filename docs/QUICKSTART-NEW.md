# 🚀 Quick Start - State of the Art

Run any HuggingFace model with **one command**. Auto-optimized for your hardware.

---

## ⚡ 30-Second Quick Start

### Option 1: Run with Model Key (Simplest)

```bash
# Get recommendations for your hardware
llm-stack model recommend

# Run the recommended model with chat
llm-stack run llama-3-8b --chat
```

### Option 2: Run with HuggingFace Reference

```bash
# Run any GGUF model from HuggingFace
llm-stack run unsloth/Qwen3.5-9B-GGUF:Q4_K_M --chat
```

### Option 3: Run with URL

```bash
# Paste HuggingFace URL directly
llm-stack run "https://huggingface.co/unsloth/Qwen3.5-9B-GGUF" --webui
```

---

## 🎯 What Happens Automatically

When you run `llm-stack run <model>`:

1. **Hardware Detection** - Detects your GPU (RTX 4090 ✅), CPU, RAM
2. **Model Resolution** - Figures out if it's a config key, HF repo, or URL
3. **Smart Download** - Downloads if needed (with resume support)
4. **Auto-Optimization** - Calculates optimal settings:
   - GPU layers for full offload
   - Context size based on available RAM
   - Batch size for your VRAM
   - Thread count for your CPU
5. **Server Start** - Launches optimized llama.cpp server
6. **Your Choice** - Opens chat, WebUI, or API

---

## 📋 Command Reference

### Run Models

```bash
# Download + run + interactive chat
llm-stack run llama-3-8b --chat

# Download + run + open browser WebUI
llm-stack run qwen3.5-9b --webui

# Download + run API server in background
llm-stack run meta-llama/Llama-3-8B-Instruct --bg

# Force re-download
llm-stack run llama-3-8b --force --chat
```

### Get Recommendations

```bash
# Get hardware-based recommendations
llm-stack model recommend

# For coding tasks
llm-stack model recommend --use-case code

# Prioritize quality
llm-stack model recommend --priority quality
```

### Model Management

```bash
# List available models
llm-stack model list

# Download specific model
llm-stack model download llama-3-8b

# Delete model
llm-stack model delete mistral-7b

# Validate model integrity
llm-stack model validate llama-3-8b
```

### Server Control

```bash
# Start server (manual mode)
llm-stack server start

# Stop server
llm-stack server stop

# Check status
llm-stack status

# View logs
llm-stack server logs --follow
```

---

## 🎮 Usage Examples

### Junior Engineer Experience

```bash
# "I want to chat with Llama"
llm-stack run llama-3-8b --chat

# "What model should I use?"
llm-stack model recommend

# "Show me what's running"
llm-stack status
```

### MLOps Engineer Experience

```bash
# Deploy specific quantization
llm-stack run unsloth/Qwen3.5-35B-A3B-GGUF:Q5_K_M --bg --port 8081

# Production deployment with custom context
llm-stack run llama-3-70b --api --port 8081 --context 65536 --bg

# Test different models quickly
llm-stack run mistral-7b --chat      # Fast test
llm-stack run qwen3.5-9b --chat      # Better quality
llm-stack run llama-3-8b --chat      # Compare
```

### Power User Experience

```bash
# Run with custom settings
llm-stack run qwen-35b-a3b \
  --chat \
  --port 9000 \
  --context 262144

# Background server with WebUI
llm-stack run llama-3-70b --bg --webui

# Quick API test
curl http://localhost:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3-8b",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

---

## 🔧 Hardware Auto-Optimization

The framework automatically detects and optimizes for:

### NVIDIA GPU (Your RTX 4090)
- **GPU Layers**: 999 (full offload)
- **Flash Attention**: Enabled
- **Batch Size**: 1024 (max throughput)
- **Context**: Up to 262K tokens

### Apple Silicon (M1/M2/M3)
- **GPU Layers**: 999 (Metal offload)
- **Metal Workaround**: Enabled for pre-M5
- **Unified Memory**: Optimized usage

### AMD ROCm
- **GPU Layers**: 999 (full offload)
- **ROCm Tuning**: Enabled

### CPU-Only
- **Threads**: Auto-detected
- **Batch Size**: Reduced for stability
- **Context**: Limited by RAM

---

## 📊 Model Recommendations (Your Hardware)

Based on your **RTX 4090 + 64GB RAM**:

| Priority | Model | Size | Speed | Quality |
|----------|-------|------|-------|---------|
| **Best Balance** | Qwen3.5-35B-A3B | 23GB | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ |
| **Fastest** | Llama-3-8B | 5GB | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐ |
| **Highest Quality** | Llama-3-70B | 42GB | ⚡⚡ | ⭐⭐⭐⭐⭐ |
| **Efficient** | Qwen3.5-9B | 7GB | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ |

---

## 🌐 API Usage

Once running, access the OpenAI-compatible API:

### Python

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
    ]
)

print(response.choices[0].message.content)
```

### curl

```bash
curl http://localhost:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

---

## 🎯 Common Workflows

### Workflow 1: Quick Test
```bash
# Test a model quickly
llm-stack run mistral-7b --chat

# Exit with /quit
```

### Workflow 2: Production Setup
```bash
# Start server in background
llm-stack run llama-3-8b --bg --port 8081

# Use from your application
# API available at http://localhost:8081/v1
```

### Workflow 3: Model Comparison
```bash
# Try different models
llm-stack run llama-3-8b --chat
llm-stack run qwen3.5-9b --chat
llm-stack run gemma-2-7b --chat

# Pick the best one for your use case
```

### Workflow 4: Maximum Performance
```bash
# Get best model for your hardware
llm-stack model recommend --priority quality

# Run with maximum context
llm-stack run llama-3-70b --context 262144 --bg
```

---

## ❓ Troubleshooting

### "Model not found"
```bash
# Download first
llm-stack model download llama-3-8b

# Or use run command (auto-downloads)
llm-stack run llama-3-8b --chat
```

### "Port already in use"
```bash
# Check what's running
llm-stack status

# Stop existing server
llm-stack server stop

# Or use different port
llm-stack run llama-3-8b --port 9000 --chat
```

### "Out of memory"
```bash
# Use smaller model
llm-stack run llama-3-8b --chat

# Or reduce context
llm-stack run llama-3-70b --context 32768 --chat
```

### "llama-server not found"
```bash
# Install llama.cpp
# macOS:
brew install llama.cpp

# Linux:
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp && cmake -B build && cmake --build build --target llama-server
sudo cp build/bin/llama-server /usr/local/bin/
```

---

## 🎓 Next Steps

1. **Get Recommendations**: `llm-stack model recommend`
2. **Run Your First Model**: `llm-stack run llama-3-8b --chat`
3. **Explore API**: Visit `http://localhost:8081/docs`
4. **Read Full Docs**: See [README.md](../README.md)

---

**Ready?** Just run:
```bash
llm-stack run llama-3-8b --chat
```

🚀
