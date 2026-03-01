# Model Configuration Guide

## Quick Start - Switch Models

### 1. Edit config.yaml

Open `config.yaml` and change the `active_model`:

```yaml
# Current model
active_model: "qwen-35b-a3b"

# Change to another model:
# active_model: "llama-3-70b"
# active_model: "llama-3-8b"
# active_model: "mistral-7b"
# active_model: "gemma-7b"
# active_model: "phi-3-mini"
```

### 2. Download the Model

```bash
./bin/download-model.sh
```

### 3. Start Server

```bash
./bin/start-webui.sh
```

---

## Available Models

### Qwen Models

| Model | Size | RAM | Speed | Best For |
|-------|------|-----|-------|----------|
| **qwen-35b-a3b** | 19GB | 32GB | ⚡⚡⚡ | Best balance |
| qwen-32b | 20GB | 32GB | ⚡⚡⚡ | All-rounder |

### Llama Models

| Model | Size | RAM | Speed | Best For |
|-------|------|-----|-------|----------|
| llama-3-70b | 42GB | 64GB | ⚡⚡ | Highest quality |
| llama-3-8b | 5GB | 16GB | ⚡⚡⚡⚡ | Fast, low RAM |

### Mistral Models

| Model | Size | RAM | Speed | Best For |
|-------|------|-----|-------|----------|
| mistral-large | 70GB | 96GB | ⚡ | Enterprise |
| mistral-7b | 4GB | 8GB | ⚡⚡⚡⚡⚡ | Very fast |

### Gemma Models

| Model | Size | RAM | Speed | Best For |
|-------|------|-----|-------|----------|
| gemma-7b | 5GB | 16GB | ⚡⚡⚡⚡ | Efficient |
| gemma-27b | 17GB | 24GB | ⚡⚡⚡ | Balanced |

### Phi Models

| Model | Size | RAM | Speed | Best For |
|-------|------|-----|-------|----------|
| phi-3-mini | 2GB | 8GB | ⚡⚡⚡⚡⚡ | Ultra fast |
| phi-3-medium | 5GB | 16GB | ⚡⚡⚡⚡ | Small & capable |

---

## Add a New Model

### 1. Add to config.yaml

```yaml
models:
  my-custom-model:
    name: "MyModel-7B-Q4_K_M.gguf"
    path: "$HOME/models/MyModel-7B-Q4_K_M.gguf"
    hf_repo: "username/MyModel-GGUF"
    hf_file: "MyModel-7B-Q4_K_M.gguf"
    size_gb: 4
    ram_required_gb: 16
    description: "My custom model"
```

### 2. Set as Active

```yaml
active_model: "my-custom-model"
```

### 3. Download

```bash
./bin/download-model.sh
```

---

## Programmatic Model Switching

### Python

```python
from src.python.config import config, set_active_model

# List available models
models = config.list_models()
print(f"Available: {list(models.keys())}")

# Switch model
set_active_model('llama-3-70b')

# Get model info
print(f"Active: {config.get_active_model()}")
print(f"Path: {config.get_model_path()}")
```

### Bash

```bash
# Load config
source scripts/config.sh

# Current model
echo "Active: $ACTIVE_MODEL"
echo "Model: $MODEL_NAME"

# Switch model (edit config.yaml)
sed -i '' 's/active_model: "qwen-35b-a3b"/active_model: "llama-3-70b"/' config.yaml
source scripts/config.sh
```

---

## System Requirements

### Minimum RAM by Model Size

| Model Size | Minimum RAM | Recommended |
|------------|-------------|-------------|
| 2-5GB | 8GB | 16GB |
| 5-10GB | 16GB | 24GB |
| 10-20GB | 24GB | 32GB |
| 20-30GB | 32GB | 48GB |
| 30-50GB | 48GB | 64GB |
| 50GB+ | 64GB | 96GB+ |

### Disk Space

- Model: Size as listed
- Additional: 5GB for cache and temp files

---

## Troubleshooting

### Model Not Found

```bash
# Check active model
source scripts/config.sh
echo $MODEL_PATH

# Verify file exists
ls -lh $MODEL_PATH
```

### Out of Memory

1. Switch to smaller model
2. Reduce context size in config.yaml
3. Close other applications

### Slow Performance

1. Ensure GPU offloading enabled
2. Check model is quantized (Q4_K_M or similar)
3. Reduce batch size in config.yaml

---

## See Also

- [config.yaml](../config.yaml) - Full configuration file
- [README.md](../README.md) - Main documentation
- [QUICKSTART.md](../docs/QUICKSTART.md) - Getting started
