# GPU Auto-Detection Implementation

## Summary

The CLI now automatically detects and uses the appropriate GPU backend:

- **macOS**: Uses Metal GPU acceleration (all Apple Silicon)
- **Linux**: Uses CUDA (NVIDIA) or ROCm (AMD) if available, otherwise CPU
- **Automatic Workarounds**: Applies Metal crash fixes on macOS

---

## Implementation Details

### 1. Cross-Platform GPU Detection (`src/local_llm/utils/__init__.py`)

New function `get_gpu_info()` detects GPU hardware:

```python
def get_gpu_info() -> dict:
    """
    Get GPU information (cross-platform).
    
    Returns:
        - has_gpu: bool
        - gpu_type: str ('metal', 'cuda', 'rocm', 'none')
        - gpu_name: str
        - recommended_layers: int
    """
```

#### macOS Detection
- ✅ Detects Apple Silicon GPU (Metal)
- ✅ Identifies chip model (M1/M2/M3/M4)
- ✅ Adjusts layers based on unified memory
- ✅ Applies Metal crash workaround automatically

#### Linux Detection
- ✅ Checks for NVIDIA GPU (CUDA via `nvidia-smi`)
- ✅ Checks for AMD GPU (ROCm via `rocm-smi`)
- ✅ Falls back to `/sys/class/drm` detection
- ✅ Uses CPU if no GPU found

---

### 2. Server Auto-Configuration (`src/local_llm/cli/commands/server.py`)

The server start command now:

1. **Detects GPU** before starting
2. **Applies workarounds** for known issues
3. **Shows GPU status** in output

```python
# Metal crash workaround (macOS)
if is_macos() and gpu_info["gpu_type"] == "metal":
    env["GGML_METAL_RESIDENCY_SETS"] = "0"
    console.print("[dim]   GPU: Metal (workaround enabled)[/dim]")
```

---

### 3. Enhanced Status Display (`src/local_llm/cli/commands/status.py`)

`llm-stack status system` now shows:

```
🖥️  System Information

╭──────────┬─────────────────╮
│ Platform │ darwin (Darwin) │
│ Machine  │ arm64           │
│ Python   │ 3.14.3          │
╰──────────┴─────────────────╯

GPU                  ✅ Apple M4 Pro (Metal)
GPU Type             METAL
Recommended Layers   999
```

---

## Platform Behavior

### macOS (Apple Silicon)

| Chip | GPU Type | Layers | Notes |
|------|----------|--------|-------|
| M1/M2/M3/M4 | Metal | 999 | Full offload |
| M1/M2/M3 (8GB) | Metal | 35 | Conservative |
| M5/A19+ | Metal | 999 | Full tensor support |

**Automatic Workarounds:**
- `GGML_METAL_RESIDENCY_SETS=0` - Prevents crash on pre-M5 chips
- Applied automatically by CLI

### Linux (NVIDIA)

| Detection | GPU Type | Layers |
|-----------|----------|--------|
| `nvidia-smi` works | CUDA | 999 |
| `/sys/class/drm` shows NVIDIA | CUDA | 999 |
| No GPU detected | CPU | 0 |

### Linux (AMD)

| Detection | GPU Type | Layers |
|-----------|----------|--------|
| `rocm-smi` works | ROCm | 999 |
| `/sys/class/drm` shows AMD | ROCm | 999 |
| No GPU detected | CPU | 0 |

---

## Testing

### Test GPU Detection

```bash
# Show GPU info
llm-stack status system

# Python API
python -c "from local_llm.utils import get_gpu_info; print(get_gpu_info())"
```

### Expected Output

**macOS (M4 Pro):**
```python
{
    'has_gpu': True,
    'gpu_type': 'metal',
    'gpu_name': 'Apple M4 Pro (Metal)',
    'recommended_layers': 999
}
```

**Linux (NVIDIA RTX 4090):**
```python
{
    'has_gpu': True,
    'gpu_type': 'cuda',
    'gpu_name': 'NVIDIA GeForce RTX 4090',
    'recommended_layers': 999
}
```

**Linux (No GPU):**
```python
{
    'has_gpu': False,
    'gpu_type': 'none',
    'gpu_name': 'CPU only',
    'recommended_layers': 0
}
```

---

## Metal Crash Fix

### Problem

On macOS with Apple Silicon (pre-M5), llama.cpp crashes:

```
ggml_metal_device_init: tensor API disabled for pre-M5 and pre-A19 devices
ggml_metal_synchronize + 340
fatal error
```

### Solution

CLI automatically sets:
```bash
export GGML_METAL_RESIDENCY_SETS=0
```

This is applied when:
1. Running on macOS
2. Metal GPU detected
3. Starting server or running benchmarks

### Manual Override

To disable the workaround:
```bash
export GGML_METAL_RESIDENCY_SETS=1
```

To force CPU-only:
```bash
llm-stack server start --gpu-layers 0
```

---

## Configuration

### Override GPU Layers

```bash
# Use specific number of layers
llm-stack server start --gpu-layers 35

# Force CPU-only
llm-stack server start --gpu-layers 0

# Full GPU offload (default on macOS)
llm-stack server start --gpu-layers 999
```

### Check Current Settings

```bash
# Show GPU and recommended layers
llm-stack status system

# Show server configuration
llm-stack status server
```

---

## Files Modified

1. **`src/local_llm/utils/__init__.py`**
   - Added `get_gpu_info()`
   - Added `_get_macOS_gpu_info()`
   - Added `_get_linux_gpu_info()`

2. **`src/local_llm/cli/commands/server.py`**
   - Imports GPU detection functions
   - Applies Metal workaround automatically
   - Shows GPU status when starting

3. **`src/local_llm/cli/commands/status.py`**
   - Shows GPU information in `status system`
   - Displays GPU type and recommended layers

4. **`docs/METAL-CRASH-FIX.md`**
   - Workaround guide for Metal crashes

---

## Summary

✅ **macOS**: Always uses Metal GPU (with automatic crash workaround)  
✅ **Linux**: Uses NVIDIA/AMD GPU if available, otherwise CPU  
✅ **Automatic**: No manual configuration needed  
✅ **Override**: Can manually set `--gpu-layers` if needed  
✅ **Detection**: Shows GPU info in `status system`  

**The CLI now handles GPU detection and configuration automatically!**
