# llama.cpp Metal Crash - Workaround Guide

## Issue

On macOS with Apple Silicon (M1/M2/M3/M4), llama.cpp may crash with:

```
ggml_metal_device_init: tensor API disabled for pre-M5 and pre-A19 devices
ggml_metal_synchronize + 340
fatal error
```

## Root Cause

The crash occurs in llama.cpp's Metal backend when:
1. Using Apple Silicon chips **older than M5/A19**
2. llama.cpp tries to use unsupported Metal tensor features
3. The `ggml_metal_synchronize` call fails

## Workarounds

### Option 1: Disable Metal Residency Sets (Recommended)

Set this environment variable before running llama.cpp:

```bash
export GGML_METAL_RESIDENCY_SETS=0
```

Add to your shell config (`~/.zshrc`):
```bash
# Fix llama.cpp Metal crash on Apple Silicon
export GGML_METAL_RESIDENCY_SETS=0
```

### Option 2: Use CPU-Only Mode (Temporary)

For benchmarks or testing:

```bash
# Run with 0 GPU layers
llama-bench -m ~/models/model.gguf -ngl 0
```

### Option 3: Reduce GPU Layers

If full offload causes crashes:

```bash
# Use fewer GPU layers
llama-server -m model.gguf -ngl 35
```

### Option 4: Build llama.cpp from Source

The Homebrew version may have issues. Build with specific flags:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
cmake -B build -DGGML_METAL=ON -DGGML_METAL_EMBED_LIBRARY=ON
cmake --build build --target llama-server --config Release
```

## CLI Integration

The CLI now detects your GPU and recommends appropriate settings:

```bash
# Check GPU status
llm-stack status system

# Output shows:
# GPU: ✅ Apple M4 Pro (Metal)
# GPU Type: METAL
# Recommended Layers: 999
```

## Report the Bug

If the crash persists, report to llama.cpp:

**GitHub Issue:** https://github.com/ggml-org/llama.cpp/issues

**Include:**
1. Your chip: `sysctl -n machdep.cpu.brand_string`
2. macOS version: `sw_vers`
3. llama.cpp version: `llama-server --version`
4. Full error message
5. Steps to reproduce

## Current Status

✅ **CLI GPU Detection**: Working correctly
✅ **Metal Support**: Enabled by default on macOS
⚠️ **llama.cpp Bug**: Known issue with Metal residency sets on pre-M5 chips
🔧 **Workaround**: Set `GGML_METAL_RESIDENCY_SETS=0`

## Quick Fix Script

Add this to your `~/.zshrc`:

```bash
# Fix llama.cpp Metal crash
export GGML_METAL_RESIDENCY_SETS=0
export GGML_METAL=1

# Reload
source ~/.zshrc
```

Then restart your terminal and try again:

```bash
llama-bench -m ~/models/model.gguf
```
