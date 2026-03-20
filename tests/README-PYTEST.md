# Local LLM Stack CLI - Pytest Test Suite

Comprehensive test suite for the Local LLM Stack CLI with **zero mocking** - all tests use real system calls and actual configurations.

---

## Quick Start

```bash
# Run all tests
./tests/run-pytest.sh

# Run with coverage
./tests/run-pytest.sh --coverage

# Run specific test file
./tests/run-pytest.sh --test test_config.py

# Run with verbose output
./tests/run-pytest.sh --verbose
```

---

## Test Files

| File | Description | Tests | Duration |
|------|-------------|-------|----------|
| `test_cli_commands.py` | CLI command tests | 50+ tests | ~2 min |
| `test_config.py` | Configuration tests | 40+ tests | ~1 min |
| `test_hardware.py` | Hardware detection tests | 35+ tests | ~1 min |
| `test_models.py` | Model resolution tests | 35+ tests | ~1 min |
| `test_utils.py` | Utility function tests | 45+ tests | ~1 min |
| `test_integration.py` | Integration tests | 25+ tests | ~3 min |

**Total: 230+ tests, ~10 minutes**

---

## Test Categories

### CLI Commands (`test_cli_commands.py`)

Tests all CLI commands and subcommands:

- ✅ Main CLI help and version
- ✅ `run` command (download & run models)
- ✅ `server` commands (start, stop, restart, logs, status)
- ✅ `model` commands (list, info, download, delete, validate, recommend)
- ✅ `chat` commands (interactive, quick, agent)
- ✅ `benchmark` commands (run, native, api, compare, clean)
- ✅ `config` commands (show, edit, validate, models)
- ✅ `status` commands (system, server, model, dependencies, all)
- ✅ Command aliases (models → model)

### Configuration (`test_config.py`)

Tests configuration management:

- ✅ Config loading from YAML
- ✅ Nested value access
- ✅ Active model properties
- ✅ Server configuration (port, host, context, layers)
- ✅ API configuration (base URL, key)
- ✅ Advanced settings (temperature, top_p, repeat_penalty)
- ✅ Path resolution (log file, PID file, directories)
- ✅ Model information retrieval
- ✅ Config validation
- ✅ Error handling (invalid paths, missing fields)

### Hardware Detection (`test_hardware.py`)

Tests hardware detection without mocking:

- ✅ GPU detection (CUDA, ROCm, Metal)
- ✅ CPU detection (cores, threads, model)
- ✅ Memory detection (total, available, used)
- ✅ Disk detection (total, used, free)
- ✅ Platform detection (Linux, macOS, Windows)
- ✅ Optimal configuration generation
- ✅ Hardware info summary
- ✅ Dataclass validation (GPUInfo, CPUInfo, MemoryInfo, DiskInfo)

### Model Resolution (`test_models.py`)

Tests model identifier resolution:

- ✅ Config model key resolution
- ✅ HuggingFace repo resolution
- ✅ Partial name matching
- ✅ Quantization extraction
- ✅ URL pattern parsing
- ✅ ModelReference dataclass
- ✅ Edge cases (empty strings, malformed repos)
- ✅ Search functionality

### Utilities (`test_utils.py`)

Tests cross-platform utilities:

- ✅ Platform detection (get_platform, is_macos, is_linux)
- ✅ CPU functions (get_cpu_count)
- ✅ Memory functions (get_total_ram_gb, get_available_ram_gb)
- ✅ Disk functions (get_disk_usage)
- ✅ Port functions (is_port_in_use, get_process_using_port)
- ✅ Process functions (kill_process)
- ✅ System info (get_system_info)
- ✅ Command functions (check_command_exists, get_command_path)
- ✅ Path functions (expand_path, ensure_directory)
- ✅ Format functions (format_size)
- ✅ GPU info (get_gpu_info)

### Integration (`test_integration.py`)

Tests complete workflows:

- ✅ Server lifecycle (start, status, stop)
- ✅ Model workflows (list, info, validate, recommend)
- ✅ Configuration workflows (show, validate, sections)
- ✅ Status workflows (system, server, model, dependencies)
- ✅ Hardware detection workflow
- ✅ Model resolution workflow
- ✅ Chat workflow (help commands)
- ✅ Benchmark workflow
- ✅ End-to-end workflows
- ✅ Error handling
- ✅ Concurrency and state management

---

## Running Tests

### Prerequisites

```bash
# Activate virtual environment
source .venv/bin/activate

# Or install CLI
./bin/install-cli.sh
```

### Run All Tests

```bash
# Complete test suite
./tests/run-pytest.sh

# With coverage
./tests/run-pytest.sh --coverage

# Verbose output
./tests/run-pytest.sh --verbose
```

### Run Specific Tests

```bash
# CLI commands only
./tests/run-pytest.sh --test test_cli_commands.py

# Configuration tests
./tests/run-pytest.sh --test test_config.py

# Hardware detection
./tests/run-pytest.sh --test test_hardware.py

# Model resolution
./tests/run-pytest.sh --test test_models.py

# Utilities
./tests/run-pytest.sh --test test_utils.py

# Integration tests
./tests/run-pytest.sh --test test_integration.py
```

### Run with Pytest Directly

```bash
# Activate venv first
source .venv/bin/activate

# Run all tests
pytest tests/

# Run specific file
pytest tests/test_config.py

# Run specific test
pytest tests/test_config.py::TestConfigLoading::test_load_default_config

# Run with markers
pytest tests/ -m "not slow"

# Run with coverage
pytest tests/ --cov=src/local_llm --cov-report=html
```

---

## Test Output

Tests produce colored output:
- 🟢 **Green** - Test passed
- 🔴 **Red** - Test failed
- 🟡 **Yellow** - Test skipped

Example:
```
tests/test_config.py::TestConfigLoading::test_load_default_config PASSED
tests/test_config.py::TestConfigAccess::test_get_nested_value PASSED
tests/test_hardware.py::TestHardwareDetector::test_detect_gpu PASSED
...

==================== 230 passed in 8.52s ====================
```

---

## Coverage Report

Generate HTML coverage report:

```bash
./tests/run-pytest.sh --coverage

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

---

## Test Fixtures

The test suite provides several fixtures in `conftest.py`:

- `project_root` - Project root directory
- `config_file` - Path to config.yaml
- `temp_dir` - Temporary directory (auto-cleaned)
- `temp_config_file` - Temporary config for testing
- `cli_env` - Environment variables for CLI
- `run_cli` - Run CLI commands
- `check_llama_tools` - Check llama.cpp availability
- `gpu_available` - Check GPU availability
- `server_port` - Get available port
- `sample_model_ref` - Sample model reference

---

## Writing New Tests

### Example Test

```python
import pytest
from local_llm.config import get_config

def test_example(run_cli):
    """Example test."""
    # Test CLI command
    result = run_cli(["status", "system"])
    assert result.returncode == 0
    assert "CPU" in result.stdout or "RAM" in result.stdout

def test_config_access(project_root):
    """Test config access."""
    from local_llm.config import Config
    
    config = Config(str(project_root / "config.yaml"))
    assert config.server_port is not None
    assert isinstance(config.server_port, int)
```

### Best Practices

1. **No mocking** - Use real system calls
2. **Use fixtures** - Leverage conftest.py fixtures
3. **Descriptive names** - Clear test function names
4. **Assert specifically** - Check exact conditions
5. **Handle errors** - Test error cases
6. **Clean up** - Use temp_dir for artifacts

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [macos-latest, ubuntu-latest]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        python -m venv .venv
        source .venv/bin/activate
        pip install -e ".[dev]"

    - name: Run tests
      run: ./tests/run-pytest.sh --coverage

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
```

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
./tests/run-pytest.sh --test test_cli_commands.py || exit 1
```

---

## Troubleshooting

### Tests Fail Immediately
```bash
# Check if CLI is installed
local-llm --version

# If not, install it
./bin/install-cli.sh
```

### Import Errors
```bash
# Ensure venv is activated
source .venv/bin/activate

# Reinstall package
pip install -e .
```

### Slow Tests
Some tests may be slow due to:
- Hardware detection
- File system operations
- Network calls (if any)

Run quick tests only:
```bash
./tests/run-pytest.sh --test test_cli_commands.py
```

### Port Conflicts
If server tests fail due to port conflicts:
```bash
# Stop any running server
local-llm server stop

# Or use custom port
lsof -ti :8081 | xargs kill -9
```

---

## Test Coverage Goals

Current coverage targets:
- CLI Commands: 100%
- Configuration: 95%
- Hardware Detection: 90%
- Model Resolution: 90%
- Utilities: 85%
- Integration: 80%

---

## License

Tests are part of the Local LLM Stack project (MIT License).
