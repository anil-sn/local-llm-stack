# Qwen3.5-35B-A3B - Test Results & Performance Summary

## ✅ Test Suite Results

**All 12 tests passed!**

### Tool Executor Tests (5/5)
- ✅ execute_bash - Shell command execution
- ✅ read_file - File reading
- ✅ write_file - File writing  
- ✅ list_dir - Directory listing
- ✅ execute_python - Python code execution

### Agent Tests (5/5)
- ✅ Simple Query - Basic conversation
- ✅ File Operations - Create and read files
- ✅ Bash Command - Execute system commands
- ✅ List Directory - Browse filesystem
- ✅ Python Execution - Run calculations

### Performance & Integration (2/2)
- ✅ Response Time - Under 30s for simple queries
- ✅ Conversation History - Multi-turn memory

---

## 📊 Performance Benchmarks

### Generation Speed (M4 Pro)
| Metric | Speed |
|--------|-------|
| **Generation** | 35-36 tokens/sec |
| **Prompt Processing** | 100-200 tokens/sec |
| **First Token** | < 500ms |

### Response Quality
- Unlimited token generation (no artificial limits)
- Full reasoning content displayed
- Markdown rendered with **glow** (beautiful terminal output)

---

## 🎨 Markdown Rendering

### Available Renderers
```bash
$ python scripts/render_md.py --check
Available markdown renderers:
  ✅ rich
  ✅ glow       ← Best quality
  ❌ mdv

Recommended: glow
```

### Benchmarks with Glow Rendering
```bash
./benchmarks/run-benchmark.sh
```

Output includes:
- 💭 Reasoning (full, untruncated)
- 📤 Output (rendered with glow for beautiful formatting)
- 📊 Performance metrics

---

## 🛠️ Agent Capabilities

### Unrestricted Access
- ✅ Full filesystem access (read/write anywhere)
- ✅ Execute any bash command
- ✅ Run Python code
- ✅ Web search and URL fetching
- ✅ No working directory restrictions
- ✅ No artificial timeouts

### Tool Usage Format
```xml
<tool>execute_bash(command="ls -la /")</tool>
<tool>read_file(path="/etc/hosts")</tool>
<tool>write_file(path="/tmp/test.py", content="print('hi')")</tool>
<tool>list_dir(path="/")</tool>
<tool>web_search(query="latest news")</tool>
<tool>execute_python(code="print(2+2)")</tool>
```

---

## 📁 Files Created

### Core Scripts
- `scripts/qwen-agent.py` - Advanced agent with tool calling
- `scripts/test_agent.py` - Comprehensive test suite (12 tests)
- `scripts/render_md.py` - Markdown renderer (glow/rich/mdv)

### Documentation
- `scripts/AGENT-UNRESTRICTED.md` - Full access guide
- `scripts/AGENT.md` - Agent usage guide
- `scripts/MARKDOWN-RENDERER.md` - Rendering guide
- `TEST-RESULTS.md` - This file

### Benchmarks
- `benchmarks/run-benchmark.sh` - Performance tests (with glow)
- `benchmarks/run-evaluation.sh` - Quality evaluation (with glow)
- `benchmarks/run-throughput.sh` - Concurrency tests
- `benchmarks/run-all.sh` - Run all benchmarks

---

## 🚀 Quick Start

### Run Tests
```bash
python scripts/test_agent.py
```

### Run Benchmarks
```bash
./benchmarks/run-benchmark.sh
```

### Use Agent
```bash
# Interactive mode
python scripts/qwen-agent.py --chat

# Single query
python scripts/qwen-agent.py "List all Python files in /usr"
```

### Render Markdown
```bash
# Render any markdown file with glow
python scripts/render_md.py README.md
```

---

## ⚠️ Security Note

The agent now has **FULL SYSTEM ACCESS**:
- Can read any file (passwords, keys, etc.)
- Can write anywhere (with permissions)
- Can execute any command
- No artificial safety restrictions

**Use at your own risk!** Only run commands you trust.

---

## 📈 Performance Comparison

| Task | Time | Tokens | Speed |
|------|------|--------|-------|
| Greeting | 18.7s | 671 | 36.09 tok/s |
| Factual | 7.3s | 252 | 34.5 tok/s |
| Code Gen | 25.0s | 861 | 34.4 tok/s |
| Python Calc | < 2s | ~50 | 35+ tok/s |

---

## 🎯 Key Improvements

1. **Unrestricted Access** - Removed all working directory and timeout limitations
2. **Glow Rendering** - Beautiful markdown output in benchmarks
3. **Test Suite** - 12 comprehensive tests, all passing
4. **Better Parsing** - Improved tool call argument parsing
5. **Full Output** - No truncation, complete reasoning displayed

---

## 📝 Example Session

```
╔══════════════════════════════════════════════════════════╗
║     Qwen3.5-35B-A3B Advanced Agent                       ║
╚══════════════════════════════════════════════════════════╝

You: Calculate 123 * 456

╭────────────────────────────── 🤖 Assistant ───────────────────────────────╮
│ The result of 123 * 456 is **56,088**.                                    │
╰───────────────────────────────────────────────────────────────────────────╯

You: List files in /etc

╭────────────────────────────── 🤖 Assistant ───────────────────────────────╮
│ Here are the files in /etc:                                               │
│ • hosts                                                                   │
│ • passwd                                                                  │
│ • ssh/                                                                    │
│ • ...                                                                     │
╰───────────────────────────────────────────────────────────────────────────╯
```

---

**Last Updated:** February 28, 2026
**Model:** Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf
**Server:** llama.cpp on port 8080
