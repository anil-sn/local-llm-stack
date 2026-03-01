# Quick Start Guide - Local LLM Stack

Get up and running with Qwen, Llama, Mistral, and 10+ other models in 5 minutes.

---

## Prerequisites

| Requirement | Specification |
|-------------|---------------|
| **OS** | macOS 12+ (M1/M2/M3/M4) or Linux (Ubuntu 20.04+, Fedora 35+) |
| **RAM** | 32GB recommended (16GB minimum) |
| **Disk** | 25GB free space |
| **Python** | 3.10+ |

---

## Step 1: Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/local-llm-stack.git
cd local-llm-stack
```

---

## Step 2: Run Automated Setup

```bash
./prepare.sh
```

This script will:

1. **Detect your OS** (macOS or Linux)
2. **Install dependencies**
   - macOS: Homebrew + Xcode Command Line Tools
   - Linux: apt/dnf/yum/pacman packages
3. **Install llama.cpp** with GPU acceleration
4. **Setup Python** virtual environment
5. **Download model** (optional, ~19GB)

**Expected output:**
```
╔══════════════════════════════════════════════════════════╗
║     Qwen3.5-35B-A3B Local Inference Setup                ║
╚══════════════════════════════════════════════════════════╝

📊 System Information:
   OS: macos
   Version: 14.0
   Architecture: arm64

✅ RAM: 36GB
✅ Disk Space: 500GB available
✅ Python: Python 3.12.0
✅ pip: installed

📦 Installing llama.cpp via Homebrew...
✅ llama.cpp: version 8180

✅ Setup complete!
```

---

## Step 3: Start the Server

### Option A: Web UI (Browser)

```bash
./bin/start-webui.sh
```

**What happens:**
1. Server starts on http://localhost:8080
2. Browser opens automatically
3. You'll see the chat interface

**Expected output:**
```
╔══════════════════════════════════════════════════════════╗
║          Starting llama.cpp Web UI                       ║
╚══════════════════════════════════════════════════════════╝

📦 Model: /Users/you/models/Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf
📍 Port: 8080
🧠 Context: 131072 tokens
🧵 Threads: 14
🤔 Reasoning: ❌ Disabled
🌐 Web UI: http://localhost:8080

⏳ Waiting for server to be ready...

╔══════════════════════════════════════════════════════════╗
║           Web UI is Ready! ✅                            ║
╚══════════════════════════════════════════════════════════╝

🌐 Opening Web UI in your browser...
```

### Option B: Terminal Chat (CLI)

```bash
./bin/chat-cli
```

**Features:**
- Fast terminal interface
- Full conversation history
- Color-coded output
- Commands: `/exit`, `/quit`, `/clear`

### Option C: Claude Code CLI

```bash
source scripts/claude-code.sh
claude
```

Uses local LLM as backend for Claude Code.

---

## Step 4: Test the API

```bash
./bin/test-api.sh
```

**Expected output:**
```
╔══════════════════════════════════════════════════════════╗
║           Testing Qwen3.5-35B-A3B API                    ║
╚══════════════════════════════════════════════════════════╝

📍 Test 1: Health Check
   ✅ Server is healthy

📍 Test 2: List Models
   ✅ Found 1 model(s)
"Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf"

📍 Test 3: Chat Completion (Short)
   ✅ Response: Hello

📍 Test 4: Chat Completion (Full Response)
   ✅ Response: The sum of 2 and 2 is **4**.

╔══════════════════════════════════════════════════════════╗
║                  All Tests Passed! ✅                    ║
╚══════════════════════════════════════════════════════════╝
```

---

## Step 5: Use the API

### Python

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="qwen3.5-35b-a3b",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)
```

### cURL

```bash
curl http://localhost:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen3.5-35b-a3b",
    "messages": [{"role": "user", "content": "Hello!"}]
  }' | jq .
```

### Claude Code

```bash
source scripts/claude-code.sh
claude "Explain quantum computing"
```

---

## Switch Models (Optional)

### 1. Edit config.yaml

```yaml
# Change this line:
active_model: "llama-3-70b"

# Available models:
# - qwen-35b-a3b (19GB, 32GB RAM)
# - llama-3-70b (42GB, 64GB RAM)
# - llama-3-8b (5GB, 16GB RAM)
# - mistral-7b (4GB, 8GB RAM)
# - gemma-7b (5GB, 16GB RAM)
# - phi-3-mini (2GB, 8GB RAM)
# ...and more
```

### 2. Download New Model

```bash
./bin/download-model.sh
```

### 3. Restart Server

```bash
./bin/stop-server.sh
./bin/start-webui.sh
```

---

## Run Benchmarks (Optional)

```bash
# Complete benchmark suite
./tools/benchmarks/run-all.sh

# Quick performance test
./tools/benchmarks/run-native-benchmark.sh

# View results
./tools/benchmarks/compare-results.sh
```

---

## Common Commands Reference

| Command | Description |
|---------|-------------|
| `./prepare.sh` | Automated setup |
| `./bin/start-webui.sh` | Start Web UI |
| `./bin/chat-cli` | Terminal chat |
| `./bin/stop-server.sh` | Stop server |
| `./bin/test-api.sh` | Test API |
| `./bin/validate-model.sh` | Validate model |
| `source scripts/claude-code.sh` | Configure for Claude Code |
| `./tools/benchmarks/run-all.sh` | Run benchmarks |

---

## Troubleshooting

### Server Won't Start

```bash
# Check logs
cat /tmp/llama-server.log

# Check port
lsof -i :8080
kill -9 <PID>

# Restart
./bin/stop-server.sh
./bin/start-webui.sh
```

### Out of Memory

```bash
# Use smaller model
# Edit config.yaml:
active_model: "llama-3-8b"  # or "phi-3-mini"

# Or reduce context
./bin/start-webui.sh ~/models/model.gguf 8080 32768
```

### Model Not Found

```bash
# Check path
source scripts/config.sh
echo $MODEL_PATH

# Re-download
./bin/download-model.sh
```

### Slow Performance

```bash
# Check GPU offloading
grep "offloading" /tmp/llama-server.log
# Should show all layers offloaded

# Close other GPU apps
# Reduce batch size in config.yaml
```

---

## Next Steps

1. **Explore the Web UI** at http://localhost:8080
2. **Try different models** - edit `config.yaml`
3. **Run benchmarks** - `./tools/benchmarks/run-all.sh`
4. **Read full docs** - See [README.md](../README.md)
5. **Use with Claude Code** - See [CLAUDE-CODE.md](../CLAUDE-CODE.md)

---

## Quick Reference Card

```bash
# Start everything
./prepare.sh              # First time setup
./bin/start-webui.sh      # Start server
source scripts/claude-code.sh && claude  # Use Claude Code

# Test
./bin/test-api.sh         # Test API
./tools/benchmarks/run-all.sh  # Benchmarks

# Switch model
# 1. Edit config.yaml: active_model: "llama-3-70b"
# 2. ./bin/download-model.sh
# 3. ./bin/start-webui.sh

# Stop
./bin/stop-server.sh      # Stop server
```

---

**That's it! You're ready to use local LLMs!** 🎉

For detailed documentation, see [README.md](../README.md).
