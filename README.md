# Qwen3.5-35B-A3B Local Inference Stack

Run Qwen, Llama, Mistral, Gemma, Phi and 10+ other large language models locally on macOS and Linux with a unified configuration-driven interface.

---

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Clone and setup
git clone https://github.com/anil-sn/local-llm-stack.git
cd local-llm-stack
./prepare.sh
```

This will:
- Auto-detect your OS (macOS/Linux)
- Install all dependencies
- Install llama.cpp with GPU acceleration
- Setup Python environment
- Optionally download the model (~19GB)

### Option 2: Manual Setup

```bash
# 1. Install llama.cpp
./bin/install.sh

# 2. Download model
./bin/download-model.sh

# 3. Validate model (recommended)
./bin/validate-model.sh

# 4. Start server
./bin/start-webui.sh

# 5. Test API
./bin/test-api.sh
```

---

## ✨ Features

### 🎯 Multi-Model Support

Switch between 10+ pre-configured models with a single line change:

| Model | Size | RAM | Speed | Best For |
|-------|------|-----|-------|----------|
| **Qwen3.5-35B-A3B** | 19GB | 32GB | ⚡⚡⚡⚡ | Best balance |
| Llama-3-70B | 42GB | 64GB | ⚡⚡ | Highest quality |
| Llama-3-8B | 5GB | 16GB | ⚡⚡⚡⚡⚡ | Fast, low RAM |
| Mistral-7B | 4GB | 8GB | ⚡⚡⚡⚡⚡ | Ultra fast |
| Gemma-2-7B | 5GB | 16GB | ⚡⚡⚡⚡ | Efficient |
| Phi-3-Mini | 2GB | 8GB | ⚡⚡⚡⚡⚡ | Minimal resources |

### 🖥️ Multiple Interfaces

| Interface | Command | Use Case |
|-----------|---------|----------|
| **Web UI** | `./bin/start-webui.sh` | Browser-based chat |
| **Terminal** | `./bin/chat-cli` | CLI interactive chat |
| **Claude Code** | `source scripts/claude-code.sh && claude` | Claude Code CLI |
| **Python API** | `from openai import OpenAI` | Programmatic access |
| **Agent Mode** | `./bin/agent --chat` | Tool-calling agent |

### 📊 Comprehensive Benchmarking

Built-in benchmarking suite with 6 different test types:

```bash
# Complete benchmark suite
./tools/benchmarks/run-all.sh

# Individual benchmarks
./tools/benchmarks/run-native-benchmark.sh    # llama-bench
./tools/benchmarks/run-batched-bench.sh       # Throughput
./tools/benchmarks/run-perplexity.sh          # Quality
./tools/benchmarks/run-api-benchmark.sh 8080  # API tests
./tools/benchmarks/compare-results.sh         # Compare runs
```

### 🔧 Configuration-Driven

All settings in one YAML file:

```yaml
# config.yaml
active_model: "qwen-35b-a3b"  # Change this to switch models

models:
  qwen-35b-a3b:
    name: "Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf"
    path: "$HOME/models/..."
    hf_repo: "unsloth/Qwen3.5-35B-A3B-GGUF"
  
  llama-3-70b:
    name: "Llama-3-70B-Instruct-Q4_K_M.gguf"
    ...
```

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Features](#-features)
- [Installation](#-installation)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [API Reference](#-api-reference)
- [Benchmarks](#-benchmarks)
- [Claude Code Integration](#-claude-code-integration)
- [Troubleshooting](#-troubleshooting)
- [Project Structure](#-project-structure)

---

## 📦 Installation

### Prerequisites

| Requirement | macOS | Linux |
|-------------|-------|-------|
| **OS** | macOS 12+ (M1/M2/M3/M4) | Ubuntu 20.04+, Fedora 35+, etc. |
| **RAM** | 32GB recommended (16GB minimum) | 32GB recommended (16GB minimum) |
| **Disk** | 25GB free space | 25GB free space |
| **Python** | 3.10+ | 3.10+ |

### Automated Installation

```bash
./prepare.sh
```

**What it does:**
1. Detects OS (macOS/Linux)
2. Installs system dependencies (Homebrew/apt/dnf/pacman)
3. Installs llama.cpp with GPU acceleration
4. Creates Python virtual environment
5. Optionally downloads the model

**Options:**
```bash
./prepare.sh --help           # Show all options
./prepare.sh --skip-model     # Skip model download
./prepare.sh --only-deps      # Dependencies only
./prepare.sh --only-llama     # llama.cpp only
./prepare.sh --only-model     # Model download only
```

### Manual Installation

#### Step 1: Install llama.cpp

**macOS:**
```bash
./bin/install.sh
# Or manually:
brew install llama.cpp
```

**Linux:**
```bash
# Debian/Ubuntu
sudo apt-get update && sudo apt-get install -y build-essential cmake git
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp && cmake -B build && cmake --build build --target llama-server
sudo cp build/bin/llama-server /usr/local/bin/

# Fedora/RHEL
sudo dnf install -y gcc gcc-c++ cmake git
# (same build steps as above)
```

#### Step 2: Download Model

```bash
./bin/download-model.sh
```

Downloads `Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf` (~19GB) to `~/models/`.

**Alternative quantizations:**
Edit `bin/download-model.sh` to change:
```bash
QUANTIZATION="Q4_K_S"  # Options: Q4_K_S, Q5_K_M, Q6_K, Q8_0
```

#### Step 3: Validate Model

```bash
./bin/validate-model.sh
```

Verifies:
- SHA256 hash integrity
- GGUF file structure
- Model metadata

---

## 💻 Usage

### Web UI (Browser Interface)

```bash
./bin/start-webui.sh
```

**Features:**
- 🌐 Opens http://localhost:8080 automatically
- 💬 Chat interface with markdown rendering
- 🎨 Code highlighting
- ⚙️ Adjustable parameters (temperature, tokens, etc.)
- 📝 System prompts support
- 📚 Chat history
- 📖 API documentation at `/docs`

**Options:**
```bash
# Default (no reasoning)
./bin/start-webui.sh

# With reasoning enabled
./bin/start-webui-reasoning.sh

# Custom configuration
./bin/start-webui.sh ~/models/model.gguf 8000 65536 8
#                                    ^port ^context ^threads
```

### Terminal Chat (CLI)

```bash
./bin/chat-cli
```

**Features:**
- ⚡ Fast terminal-based interface
- 📜 Full conversation history
- 🎨 Color-coded output
- 🔧 Commands: `/exit`, `/quit`, `/clear`

### Python API

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="qwen3.5-35b-a3b",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing."}
    ],
    max_tokens=None,
    temperature=0.7
)

print(response.choices[0].message.content)
print(f"Tokens: {response.usage.total_tokens}")
print(f"Speed: {response.timings.predicted_per_second} tok/s")
```

### Agent Mode (Tool Calling)

```bash
# Interactive agent
./bin/agent --chat

# Single task
./bin/agent "Find all Python files with TODO comments"
```

**Available Tools:**
- `execute_bash` - Run shell commands
- `read_file` - Read file contents
- `write_file` - Write to files
- `list_dir` - List directory contents
- `web_search` - Search the web
- `execute_python` - Run Python code

### Claude Code CLI Integration

Use this local LLM as a backend for **Claude Code CLI**:

```bash
# Configure environment
source scripts/claude-code.sh

# Run Claude Code
claude
```

**What it does:**
- ✅ Starts server if not running
- ✅ Configures environment variables
- ✅ Sets model from config.yaml
- ✅ Disables telemetry

See [CLAUDE-CODE.md](CLAUDE-CODE.md) for complete guide.

---

## ⚙️ Configuration

All configuration is in `config.yaml`.

### Model Selection

```yaml
# Change this to switch models
active_model: "qwen-35b-a3b"

models:
  qwen-35b-a3b:
    name: "Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf"
    path: "$HOME/models/Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf"
    hf_repo: "unsloth/Qwen3.5-35B-A3B-GGUF"
    hf_file: "Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf"
    size_gb: 19
    ram_required_gb: 32
    description: "Qwen3.5 35B MoE - Best balance"
  
  llama-3-70b:
    name: "Llama-3-70B-Instruct-Q4_K_M.gguf"
    ...
```

### Server Configuration

```yaml
server:
  port: 8080
  host: "0.0.0.0"
  context_size: 131072  # Max: 262144
  gpu_layers: 999       # 999 = all layers offloaded
  batch_size: 512
  ubatch_size: 256
  flash_attn: "auto"    # auto, on, off
  threads: null         # null = auto-detect
```

### Reasoning Configuration

```yaml
reasoning:
  format: "none"        # "none" or "deepseek"
  budget: 0             # -1 = unlimited, 0 = disabled
  enable_thinking: false
```

### Available Configuration Options

| Category | Options |
|----------|---------|
| **model** | name, path, hf_repo, hf_file, size_gb, ram_required_gb |
| **server** | port, host, context_size, gpu_layers, batch_size, ubatch_size |
| **reasoning** | format, budget, enable_thinking |
| **api** | base_url, key |
| **paths** | install_dir, build_dir, log_file, pid_file, venv_dir |
| **benchmarks** | repetitions |
| **system** | min_ram_gb, recommended_ram_gb, min_disk_gb |
| **features** | enable_webui, enable_chat_cli, enable_agent, enable_benchmarks |
| **advanced** | temperature, top_p, repeat_penalty, max_tokens |
| **claude_code** | enabled, disable_telemetry, auth_token, timeout, max_tokens |

See [MODELS.md](MODELS.md) for complete model switching guide.

---

## 🔌 API Reference

### Base URL

```
http://localhost:8080/v1
```

### Endpoints

#### GET /health

Check server health.

```bash
curl http://localhost:8080/health
```

**Response:**
```json
{"status": "ok"}
```

#### GET /v1/models

List available models.

```bash
curl http://localhost:8080/v1/models
```

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf",
      "object": "model",
      "created": 1234567890,
      "owned_by": "llama.cpp"
    }
  ]
}
```

#### POST /v1/chat/completions

Chat completion (OpenAI-compatible).

```bash
curl http://localhost:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen3.5-35b-a3b",
    "messages": [
      {"role": "system", "content": "You are helpful."},
      {"role": "user", "content": "Hello!"}
    ],
    "max_tokens": null,
    "temperature": 0.7,
    "top_p": 0.9
  }'
```

**Request Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | string | required | Model name |
| `messages` | array | required | Message objects |
| `max_tokens` | integer | null | Max tokens (null = unlimited) |
| `temperature` | float | 0.7 | Sampling temperature (0-2) |
| `top_p` | float | 0.9 | Nucleus sampling (0-1) |
| `repeat_penalty` | float | 1.1 | Repetition penalty |
| `stream` | boolean | false | Stream response |

**Response:**
```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Hello! How can I help you?"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 18,
    "completion_tokens": 10,
    "total_tokens": 28
  },
  "timings": {
    "prompt_ms": 123.5,
    "predicted_ms": 285.3,
    "prompt_per_second": 145.7,
    "predicted_per_second": 35.1
  }
}
```

#### POST /v1/completions

Legacy text completion.

```bash
curl http://localhost:8080/v1/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen3.5-35b-a3b",
    "prompt": "Once upon a time",
    "max_tokens": 100
  }'
```

See [docs/API.md](docs/API.md) for complete API documentation.

---

## 📊 Benchmarks

### Quick Start

```bash
# Complete suite
./tools/benchmarks/run-all.sh

# Individual tests
./tools/benchmarks/run-native-benchmark.sh    # llama-bench
./tools/benchmarks/run-batched-bench.sh       # Throughput
./tools/benchmarks/run-perplexity.sh          # Quality
./tools/benchmarks/run-api-benchmark.sh 8080  # API tests
./tools/benchmarks/compare-results.sh         # Compare
```

### Benchmark Types

| Script | Tool | Description | Server Required |
|--------|------|-------------|-----------------|
| `run-all.sh` | All | Complete suite | Optional |
| `run-native-benchmark.sh` | llama-bench | Prompt/gen speed | No |
| `run-batched-bench.sh` | llama-batched-bench | Throughput test | No |
| `run-perplexity.sh` | llama-perplexity | Model quality | No |
| `run-api-benchmark.sh` | curl + jq | API latency | Yes |
| `compare-results.sh` | - | Compare runs | No |

### Performance Expectations (M4 Pro)

| Test | Tokens | Expected Time | Tokens/sec |
|------|--------|---------------|------------|
| Greeting | 20 | < 1s | 35+ |
| Factual QA | 50 | 1-2s | 33-35 |
| Explanation | 150 | 4-5s | 32-35 |
| Code Gen | 300 | 8-10s | 30-35 |
| Long-form | 500 | 14-16s | 30-35 |

### Native Performance (llama-bench)

| Test | Tokens/sec |
|------|------------|
| Prompt (pp512) | 510-520 |
| Generation (tg128) | 30-35 |

### Batched Throughput

| PP | TG | Prompt (t/s) | Generation (t/s) |
|----|----|--------------|------------------|
| 256 | 128 | 370-380 | 31-32 |

See [tools/benchmarks/README.md](tools/benchmarks/README.md) for complete benchmark guide.

---

## 🤖 Claude Code Integration

Use this local LLM stack as a backend for **Claude Code CLI**.

### Quick Start

```bash
# Start server and configure
source scripts/claude-code.sh

# Run Claude Code
claude
```

### What It Does

1. ✅ Checks if server is running
2. ✅ Starts server if needed
3. ✅ Configures environment variables:
   - `CLAUDE_CODE_DISABLE_TELEMETRY=1`
   - `ANTHROPIC_AUTH_TOKEN=dummy`
   - `ANTHROPIC_BASE_URL=http://localhost:8080`
   - `ANTHROPIC_MODEL=<from config.yaml>`

### Configuration

```yaml
claude_code:
  enabled: true
  disable_telemetry: true
  auth_token: "dummy"
  timeout: 300
  max_tokens: 8192
  alias: ""  # Custom model name (optional)
```

### Test Results

| Test | Status |
|------|--------|
| Server Health | ✅ PASS |
| Models Endpoint | ✅ PASS |
| Chat Completion API | ✅ PASS |
| Environment Variables | ✅ PASS |
| Model Name from Config | ✅ PASS |
| Claude Code CLI | ✅ PASS |
| API Response Format | ✅ PASS |
| Response Time | ✅ PASS (417ms) |

**All 8/8 tests passing!**

See [CLAUDE-CODE.md](CLAUDE-CODE.md) for complete integration guide.

---

## 🔧 Troubleshooting

### Server Won't Start

```bash
# Check logs
cat /tmp/llama-server.log

# Check if port is in use
lsof -i :8080
kill -9 <PID>

# Or use stop script
./bin/stop-server.sh
```

### Out of Memory

```bash
# Reduce context size
./bin/start-webui.sh ~/models/model.gguf 8080 32768

# Or edit config.yaml
server:
  context_size: 32768  # Reduce from 131072
```

### Slow Generation

```bash
# Check GPU offloading
grep "offloading" /tmp/llama-server.log
# Should show "41/41 layers" on M4 Pro

# Close other GPU applications
# Reduce batch size in config.yaml
server:
  batch_size: 256  # Reduce from 512
```

### Model Not Found

```bash
# Check model path
source scripts/config.sh
echo $MODEL_PATH

# Verify file exists
ls -lh $MODEL_PATH

# Re-download if needed
./bin/download-model.sh
```

### API Errors

```bash
# Test API
./bin/test-api.sh

# Check server health
curl http://localhost:8080/health

# View logs
tail -f /tmp/llama-server.log
```

---

## 📁 Project Structure

```
.
├── README.md                      # This file
├── prepare.sh                     # Automated setup script
├── config.yaml                    # Configuration file
├── MODELS.md                      # Model switching guide
├── CLAUDE-CODE.md                 # Claude Code integration
│
├── bin/                           # Executable scripts (10 files)
│   ├── install.sh                 # Install llama.cpp
│   ├── download-model.sh          # Download model
│   ├── validate-model.sh          # Model validation
│   ├── start-webui.sh             # Start Web UI
│   ├── start-webui-reasoning.sh   # Start with reasoning
│   ├── start-server.sh            # Start server (foreground)
│   ├── stop-server.sh             # Stop server
│   ├── test-api.sh                # Test API endpoints
│   ├── chat-cli                   # Terminal chat
│   └── agent                      # AI agent
│
├── src/python/                    # Python source (6 files)
│   ├── qwen.py                    # Simple client
│   ├── qwen-agent.py              # Agent with tools
│   ├── config.py                  # Configuration module
│   ├── render_md.py               # Markdown renderer
│   ├── test_agent.py              # Agent tests
│   └── requirements.txt           # Dependencies
│
├── scripts/                       # Helper scripts (4 files)
│   ├── config.sh                  # Bash config loader
│   ├── claude-code.sh             # Claude Code integration
│   ├── test-claude-code.sh        # Integration tests
│   └── load-env.sh                # Legacy loader
│
├── tools/benchmarks/              # Benchmark tools (10 files)
│   ├── README.md                  # Benchmark guide
│   ├── run-all.sh                 # Complete suite
│   ├── run-native-benchmark.sh    # llama-bench
│   ├── run-batched-bench.sh       # Throughput test
│   ├── run-perplexity.sh          # Model quality
│   ├── run-api-benchmark.sh       # API tests
│   └── compare-results.sh         # Compare runs
│
├── config/benchmarks/             # Benchmark configs (8 files)
│   └── *.json                     # Test prompt configs
│
└── docs/                          # Documentation (5 files)
    ├── README.md                  # Documentation index
    ├── QUICKSTART.md              # Quick start guide
    ├── API.md                     # API reference
    ├── system-prompts.md          # System prompts
    └── TEST-RESULTS.md            # Test results
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | This file - main documentation |
| [docs/QUICKSTART.md](docs/QUICKSTART.md) | 5-minute getting started |
| [docs/API.md](docs/API.md) | Complete API reference |
| [docs/system-prompts.md](docs/system-prompts.md) | Pre-built prompts |
| [MODELS.md](MODELS.md) | Model switching guide |
| [CLAUDE-CODE.md](CLAUDE-CODE.md) | Claude Code integration |
| [tools/benchmarks/README.md](tools/benchmarks/README.md) | Benchmark guide |

---

## 🤝 Contributing

### Adding a New Model

1. Edit `config.yaml`:
```yaml
models:
  my-new-model:
    name: "Model-Name-Q4_K_M.gguf"
    path: "$HOME/models/Model-Name-Q4_K_M.gguf"
    hf_repo: "username/Model-GGUF"
    hf_file: "Model-Name-Q4_K_M.gguf"
    size_gb: 10
    ram_required_gb: 24
    description: "Description here"
```

2. Set as active:
```yaml
active_model: "my-new-model"
```

3. Download:
```bash
./bin/download-model.sh
```

### Adding Features

1. Create feature in appropriate directory
2. Update `config.yaml` with new options
3. Add documentation
4. Update tests

---

## 📄 License

- **Model:** Apache 2.0 (Qwen)
- **llama.cpp:** MIT
- **This Project:** MIT

---

## 🙏 Acknowledgments

- [Qwen Team](https://qwenlm.github.io/) for Qwen3.5-35B-A3B
- [llama.cpp](https://github.com/ggml-org/llama.cpp) for inference engine
- [Unsloth](https://huggingface.co/unsloth) for GGUF quantizations
- [Anthropic](https://www.anthropic.com/) for Claude Code CLI

---

## 📞 Support

- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions
- **Documentation:** See docs/ folder

---

**Ready to run LLMs locally?** Start with `./prepare.sh`! 🚀
