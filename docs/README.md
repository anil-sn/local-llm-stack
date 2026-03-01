# Documentation Index

Complete documentation for Qwen3.5-35B-A3B Local Inference Stack.

---

## Getting Started

| Document | Description |
|----------|-------------|
| [README.md](../README.md) | Main project documentation |
| [QUICKSTART.md](QUICKSTART.md) | Quick start guide (5 minutes) |
| [API.md](API.md) | Complete API reference |

---

## User Guides

| Document | Description |
|----------|-------------|
| [system-prompts.md](system-prompts.md) | Pre-built system prompts for different use cases |
| [../tools/benchmarks/README.md](../tools/benchmarks/README.md) | Benchmark suite documentation |

---

## Technical Documentation

| Document | Description |
|----------|-------------|
| [TEST-RESULTS.md](TEST-RESULTS.md) | Test results and performance data |

---

## Quick Reference

### Start Server
```bash
./bin/start-webui.sh              # Web UI
./bin/chat-cli                    # Terminal chat
./bin/start-webui-reasoning.sh    # With reasoning
```

### Run Benchmarks
```bash
./tools/benchmarks/run-all.sh              # Complete suite
./tools/benchmarks/run-native-benchmark.sh # llama-bench
./tools/benchmarks/run-perplexity.sh       # Model quality
```

### Validate & Test
```bash
./bin/validate-model.sh    # Model integrity
./bin/test-api.sh          # API endpoints
```

---

## Documentation Structure

```
.
├── README.md                  # Main project documentation
├── docs/                      # Documentation files
│   ├── README.md              # Documentation index
│   ├── QUICKSTART.md          # Getting started
│   ├── API.md                 # API reference
│   ├── system-prompts.md      # System prompts library
│   └── TEST-RESULTS.md        # Test results
│
├── bin/                       # Executable scripts
│   ├── install.sh
│   ├── start-webui.sh
│   ├── chat-cli
│   └── ...
│
└── tools/benchmarks/          # Benchmark tools
    ├── README.md              # Benchmark documentation
    ├── run-all.sh             # Complete suite
    ├── run-native-benchmark.sh # llama-bench
    └── ...
```

---

## Need Help?

1. **Quick Start:** See [QUICKSTART.md](QUICKSTART.md)
2. **API Usage:** See [API.md](API.md)
3. **Prompts:** See [system-prompts.md](system-prompts.md)
4. **Benchmarks:** See [../tools/benchmarks/README.md](../tools/benchmarks/README.md)
5. **Main Docs:** See [../README.md](../README.md)

---

## External Resources

- [llama.cpp Documentation](https://github.com/ggml-org/llama.cpp)
- [Qwen Model Card](https://huggingface.co/Qwen)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
