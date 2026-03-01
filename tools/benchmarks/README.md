# Benchmark Suite for Qwen3.5-35B-A3B

Comprehensive performance and quality testing powered by llama.cpp tools.

---

## Quick Start

```bash
# Run complete benchmark suite (interactive)
./tools/benchmarks/run-all.sh

# Or run individual benchmarks
./tools/benchmarks/run-native-benchmark.sh    # llama-bench
./tools/benchmarks/run-batched-bench.sh       # Throughput test
./tools/benchmarks/run-perplexity.sh          # Model quality
./tools/benchmarks/run-api-benchmark.sh 8080  # API tests
./tools/benchmarks/compare-results.sh         # Compare runs
```

---

## Prerequisites

```bash
# Required tools
brew install llama.cpp jq bc

# Verify installation
llama-bench --version
llama-perplexity --version
```

---

## Benchmark Types

### 1. Native Performance (`run-native-benchmark.sh`)

**Tool:** `llama-bench`

Measures raw model performance:
- Prompt processing speed (tokens/sec)
- Generation speed (tokens/sec)
- GPU offload efficiency

**Usage:**
```bash
./tools/benchmarks/run-native-benchmark.sh
```

**Output:** `benchmarks/llama-bench.md`

**Example Results:**
```
| model    | size     | test  | t/s      |
|----------|----------|-------|----------|
| Qwen35B  | 19.16 GB | pp512 | 512.21   |
| Qwen35B  | 19.16 GB | tg128 | 30.23    |
```

---

### 2. Batched Throughput (`run-batched-bench.sh`)

**Tool:** `llama-batched-bench`

Tests concurrent request handling:
- Multiple parallel prompts
- Batch processing efficiency
- Memory bandwidth utilization

**Usage:**
```bash
./tools/benchmarks/run-batched-bench.sh
```

**Options:**
1. Quick test (single batch)
2. Standard test (multiple configurations)
3. Full test (comprehensive)

**Output:** `benchmarks/batched-bench.md`

**Example Results:**
```
| PP  | TG  | B | T_PP s | S_PP t/s | T_TG s | S_TG t/s |
|-----|-----|---|--------|----------|--------|----------|
| 256 | 128 | 1 | 0.685  | 373.71   | 4.047  | 31.63    |
```

---

### 3. Perplexity (`run-perplexity.sh`)

**Tool:** `llama-perplexity`

Measures language model quality:
- Lower perplexity = better predictions
- Tests on various text types
- Model confidence evaluation

**Usage:**
```bash
./tools/benchmarks/run-perplexity.sh
```

**Test Texts:**
- Short (general text)
- Medium (technical content)
- Code (Python)
- Custom file

**Output:** `benchmarks/perplexity.txt`

---

### 4. API Benchmark (`run-api-benchmark.sh`)

**Tool:** HTTP requests + `jq`

Tests API performance:
- End-to-end latency
- Tokens per second (generation)
- Concurrent request handling

**Usage:**
```bash
# Start server first
./bin/start-webui.sh

# Run benchmark
./tools/benchmarks/run-api-benchmark.sh 8080
```

**Tests:**
- Greeting (simple)
- Math (calculation)
- Explanation (technical)
- Reasoning (logic)
- Creative (writing)

**Output:** `benchmarks/YYYYMMDD_HHMMSS/api-current.json`

---

### 5. Complete Suite (`run-all.sh`)

**Tool:** All of the above

Runs comprehensive benchmarks:
1. Model validation
2. Native performance
3. Perplexity test
4. Batched throughput
5. API tests (optional)
6. Summary report

**Usage:**
```bash
./tools/benchmarks/run-all.sh
```

**Modes:**
1. Quick (llama-bench only)
2. Standard (+ perplexity)
3. Full (all benchmarks)
4. Custom (select tests)

**Output:** `benchmarks/YYYYMMDD_HHMMSS/`

---

### 6. Compare Results (`compare-results.sh`)

Compares benchmark runs:
- Side-by-side performance
- Trend analysis
- Mode comparison (reasoning vs non-reasoning)

**Usage:**
```bash
./tools/benchmarks/compare-results.sh
```

---

## Metrics Explained

| Metric | Description | Good Value (M4 Pro) |
|--------|-------------|---------------------|
| **S_PP** | Prompt processing speed | 400-600 tok/s |
| **S_TG** | Generation speed | 30-40 tok/s |
| **Perplexity** | Language model quality | Lower is better |
| **Latency** | End-to-end response time | < 5s for 200 tokens |
| **Batch/s** | Batches per second | Varies by batch size |

---

## Performance Expectations

### Qwen3.5-35B-A3B on M4 Pro

| Test | Tokens | Expected Time | Tokens/sec |
|------|--------|---------------|------------|
| Greeting | 20 | < 1s | 35+ |
| Factual QA | 50 | 1-2s | 33-35 |
| Explanation | 150 | 4-5s | 32-35 |
| Code Gen | 300 | 8-10s | 30-35 |
| Long-form | 500 | 14-16s | 30-35 |

---

## Reasoning vs Non-Reasoning

### Non-Reasoning Mode (Default)
```bash
./bin/start-webui.sh
```
- **Speed:** ~35 tokens/sec
- **Use case:** Quick responses, simple tasks
- **Best for:** Chat, Q&A, code generation

### Reasoning Mode
```bash
./bin/start-webui-reasoning.sh
```
- **Speed:** ~30-33 tokens/sec
- **Use case:** Complex problems, analysis
- **Best for:** Math, logic, detailed explanations

---

## Results Interpretation

### Native Performance
- **pp512 > 400:** Good prompt processing
- **tg128 > 25:** Acceptable generation speed
- **tg128 > 35:** Excellent performance

### Batched Throughput
- Higher batch sizes = better throughput
- Watch for memory bottlenecks
- Optimal batch size depends on use case

### Perplexity
- Lower values indicate better language modeling
- Compare across similar text types
- Affected by text domain and complexity

### API Benchmarks
- Consistent tok/s = stable server
- High variance = potential issues
- Compare with native benchmarks

---

## Example Workflow

```bash
# 1. Validate model
./bin/validate-model.sh

# 2. Run quick benchmark
./tools/benchmarks/run-native-benchmark.sh

# 3. Start server
./bin/start-webui.sh

# 4. Test API
./bin/test-api.sh

# 5. Run API benchmark
./tools/benchmarks/run-api-benchmark.sh 8080

# 6. Compare results
./tools/benchmarks/compare-results.sh
```

---

## Output Files

```
benchmarks/
├── YYYYMMDD_HHMMSS/
│   ├── llama-bench.md
│   ├── batched-bench.md
│   ├── perplexity.txt
│   ├── api-current.json
│   └── SUMMARY.md
├── llama-bench.md (latest)
└── batched-bench.md (latest)
```

---

## Troubleshooting

### Server not responding
```bash
./bin/start-webui.sh
./bin/test-api.sh
```

### Missing tools
```bash
brew install llama.cpp jq bc
```

### Out of memory
```bash
# Reduce context size
./bin/start-webui.sh ~/models/model.gguf 8080 32768
```

### Slow generation
- Check GPU offload: `grep "offloading" /tmp/llama-server.log`
- Close other GPU applications
- Reduce batch size

### Benchmark fails
```bash
# Check model path
./bin/validate-model.sh

# Verify llama.cpp installation
llama-bench --version
llama-perplexity --version
```

---

## Tips for Accurate Results

1. **Close other applications** - Free up RAM and GPU
2. **Run multiple times** - Average the results
3. **Use consistent settings** - Same context, threads
4. **Monitor thermals** - Throttling affects performance
5. **Record system state** - Note background processes

---

## See Also

- [README.md](../README.md) - Full project documentation
- [docs/QUICKSTART.md](../docs/QUICKSTART.md) - Getting started guide
- [docs/API.md](../docs/API.md) - API reference
