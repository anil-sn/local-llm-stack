# Local LLM Stack CLI - Test Suite

This directory contains comprehensive tests for the Local LLM Stack CLI.

---

## Quick Start

```bash
# Run quick test (2 minutes, recommended for CI)
./tests/test-quick.sh

# Run specific tests
./tests/test-gpu.sh
./tests/test-config.sh
./tests/test-server.sh
./tests/test-cross-platform.sh

# Run all tests (10+ minutes)
./tests/test-all.sh
```

---

## Test Files

| File | Description | Duration |
|------|-------------|----------|
| `test-quick.sh` | Core functionality test | ~2 min |
| `test-gpu.sh` | GPU detection test | ~1 min |
| `test-config.sh` | Configuration test | ~2 min |
| `test-server.sh` | Server test (non-destructive) | ~3 min |
| `test-cross-platform.sh` | Cross-platform compatibility | ~2 min |
| `test-all.sh` | Complete test suite | ~10 min |

---

## Test Coverage

### Quick Test (`test-quick.sh`)
Tests 16 core commands:
- ✅ Main CLI help and version
- ✅ Status commands (system, server, model, dependencies)
- ✅ Configuration commands (show, validate, models)
- ✅ Model commands (list, info)
- ✅ Server commands (help, status)
- ✅ Chat commands (help)
- ✅ Benchmark commands (help)

### GPU Test (`test-gpu.sh`)
Tests GPU detection:
- ✅ Metal GPU on macOS
- ✅ CUDA/ROCm on Linux
- ✅ Python GPU API
- ✅ Recommended layers calculation

### Config Test (`test-config.sh`)
Tests configuration:
- ✅ Config loading
- ✅ Section display (server, api, advanced, models)
- ✅ Config validation
- ✅ Path resolution
- ✅ Model information

### Server Test (`test-server.sh`)
Tests server functionality (non-destructive):
- ✅ Server status detection
- ✅ API endpoint health check
- ✅ Quick chat functionality
- ✅ Server configuration

### Cross-Platform Test (`test-cross-platform.sh`)
Tests platform compatibility:
- ✅ macOS detection and commands
- ✅ Linux detection and commands
- ✅ GPU detection on both platforms
- ✅ Python cross-platform utilities

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
./tests/test-all.sh

# View test log
cat tests/test-*.log | tail -100
```

### Run Individual Tests

```bash
# Quick smoke test
./tests/test-quick.sh

# GPU detection
./tests/test-gpu.sh

# Configuration
./tests/test-config.sh

# Server (requires server running for full test)
./tests/test-server.sh

# Cross-platform
./tests/test-cross-platform.sh
```

---

## Test Output

Tests produce colored output:
- 🟢 **Green** - Test passed
- 🔴 **Red** - Test failed
- 🟡 **Yellow** - Test skipped

Example:
```
╔══════════════════════════════════════════════════╗
║     Local LLM Stack CLI - Quick Test            ║
╚══════════════════════════════════════════════════╝

Testing: Main help... ✅ PASS
Testing: Version... ✅ PASS
Testing: Status system... ✅ PASS
...

══════════════════════════════════════════════════
Results: 16 passed, 0 failed
══════════════════════════════════════════════════
✅ All quick tests passed!
```

---

## Test Logs

Each test run creates a log file:
```
tests/test-YYYYMMDD-HHMMSS.log
```

View latest log:
```bash
ls -lt tests/*.log | head -1
cat tests/test-*.log | tail -50
```

---

## CI/CD Integration

### GitHub Actions Example

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
        pip install -e .
    
    - name: Run quick tests
      run: ./tests/test-quick.sh
```

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
./tests/test-quick.sh || exit 1
```

---

## Troubleshooting

### Tests Fail Immediately
```bash
# Check if CLI is installed
llm-stack --version

# If not, install it
./bin/install-cli.sh
```

### Server Tests Fail
```bash
# Start server first
llm-stack server start

# Then run server tests
./tests/test-server.sh
```

### GPU Tests Fail
```bash
# Check GPU detection
llm-stack status system

# Should show GPU information
```

---

## Test Coverage Report

Run comprehensive test and generate report:
```bash
./tests/test-all.sh 2>&1 | tee test-report.txt
```

---

## Contributing

When adding new commands, add tests to:
1. `test-quick.sh` - For core functionality
2. `test-all.sh` - For comprehensive coverage

Example test:
```bash
test_command "llm-stack new-command --help" "New command help"
```

---

## License

Tests are part of the Local LLM Stack project (MIT License).
