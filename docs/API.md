# API Reference - Local LLM Stack

Complete API documentation for the Qwen3.5-35B-A3B inference server with OpenAI-compatible endpoints.

---

## Overview

This project provides an **OpenAI-compatible API** using llama.cpp, allowing you to use any OpenAI SDK or tool with your local LLM.

---

## Base URL

```
http://localhost:PORT/v1  # PORT from config.yaml (default: 8081)
```

---

## Authentication

No authentication required by default.

```python
api_key = "not-needed"  # Any value works
```

---

## Endpoints

### GET /health

Check server health status.

**Request:**
```bash
curl http://localhost:8081/health  # Use port from config.yaml
```

**Response:**
```json
{
  "status": "ok"
}
```

**Error Response:**
```json
{
  "status": "error",
  "message": "Server not ready"
}
```

---

### GET /v1/models

List available models.

**Request:**
```bash
curl http://localhost:8081/v1/models  # Use port from config.yaml
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

---

### POST /v1/chat/completions

Chat completion endpoint (OpenAI-compatible).

**Request:**
```bash
curl http://localhost:8081/v1/chat/completions \  # Use port from config.yaml
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen3.5-35b-a3b",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello!"}
    ],
    "max_tokens": null,
    "temperature": 0.7
  }'
```

**Request Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | string | required | Model name (any value works) |
| `messages` | array | required | Array of message objects |
| `max_tokens` | integer | null | Max tokens to generate (null = unlimited) |
| `temperature` | float | 0.7 | Sampling temperature (0.0 - 2.0) |
| `top_p` | float | 0.9 | Nucleus sampling parameter (0.0 - 1.0) |
| `top_k` | integer | 40 | Top-k sampling |
| `repeat_penalty` | float | 1.1 | Repetition penalty (1.0 - 2.0) |
| `stream` | boolean | false | Stream response tokens |
| `stop` | array | [] | Stop sequences |
| `presence_penalty` | float | 0.0 | Presence penalty (-2.0 - 2.0) |
| `frequency_penalty` | float | 0.0 | Frequency penalty (-2.0 - 2.0) |

**Message Object:**

| Field | Type | Description |
|-------|------|-------------|
| `role` | string | "system", "user", or "assistant" |
| `content` | string | Message content |

**Response:**
```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf",
  "system_fingerprint": "b8180-d979f2b17",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?",
        "reasoning_content": null
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 18,
    "completion_tokens": 10,
    "total_tokens": 28
  },
  "timings": {
    "cache_n": 0,
    "prompt_n": 14,
    "prompt_ms": 123.5,
    "prompt_per_token_ms": 8.82,
    "prompt_per_second": 113.6,
    "predicted_n": 10,
    "predicted_ms": 285.3,
    "predicted_per_token_ms": 28.53,
    "predicted_per_second": 35.1
  }
}
```

**Streaming Response:**
```bash
curl http://localhost:8081/v1/chat/completions \  # Use port from config.yaml
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen3.5-35b-a3b",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": true
  }'
```

**Streaming Response Format:**
```
data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":1234567890,"model":"Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf","choices":[{"index":0,"delta":{"role":"assistant","content":"Hello"},"finish_reason":null}]}

data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":1234567890,"model":"Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf","choices":[{"index":0,"delta":{"content":"!"},"finish_reason":null}]}

data: [DONE]
```

---

### POST /v1/completions

Legacy text completion endpoint.

**Request:**
```bash
curl http://localhost:8081/v1/completions \  # Use port from config.yaml
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen3.5-35b-a3b",
    "prompt": "Once upon a time",
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

**Request Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | string | required | Model name |
| `prompt` | string | required | Prompt text |
| `max_tokens` | integer | 16 | Max tokens to generate |
| `temperature` | float | 0.7 | Sampling temperature |
| `top_p` | float | 0.9 | Nucleus sampling |
| `n` | integer | 1 | Number of completions |
| `stream` | boolean | false | Stream response |
| `stop` | array/string | null | Stop sequences |

**Response:**
```json
{
  "id": "cmpl-xxx",
  "object": "text_completion",
  "created": 1234567890,
  "model": "Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf",
  "choices": [
    {
      "index": 0,
      "text": ", there was a brave knight...",
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 4,
    "completion_tokens": 100,
    "total_tokens": 104
  }
}
```

---

### POST /v1/embeddings

Generate embeddings (if model supports it).

**Request:**
```bash
curl http://localhost:8081/v1/embeddings \  # Use port from config.yaml
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen3.5-35b-a3b",
    "input": "The quick brown fox"
  }'
```

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "embedding": [0.0023, -0.0156, 0.0891, ...],
      "index": 0
    }
  ],
  "model": "Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf",
  "usage": {
    "prompt_tokens": 4,
    "total_tokens": 4
  }
}
```

---

## Client Libraries

### Python (OpenAI SDK)

```python
from openai import OpenAI

# Port is configured in config.yaml (server.port)
client = OpenAI(
    base_url="http://localhost:8081/v1",
    api_key="not-needed"
)

# Chat completion
response = client.chat.completions.create(
    model="qwen3.5-35b-a3b",
    messages=[
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hello!"}
    ],
    max_tokens=None,
    temperature=0.7,
    top_p=0.9
)

print(response.choices[0].message.content)
print(f"Tokens: {response.usage.total_tokens}")
print(f"Speed: {response.timings.predicted_per_second} tok/s")

# Streaming
stream = client.chat.completions.create(
    model="qwen3.5-35b-a3b",
    messages=[{"role": "user", "content": "Write a story."}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### Node.js (OpenAI SDK)

```javascript
const { OpenAI } = require('openai');

// Port is configured in config.yaml (server.port)
const client = new OpenAI({
    baseURL: 'http://localhost:8081/v1',
    apiKey: 'not-needed'
});

async function chat() {
    const response = await client.chat.completions.create({
        model: 'qwen3.5-35b-a3b',
        messages: [
            { role: 'system', content: 'You are helpful.' },
            { role: 'user', content: 'Hello!' }
        ],
        temperature: 0.7
    });
    
    console.log(response.choices[0].message.content);
}

chat();
```

### cURL

```bash
# Simple chat (use port from config.yaml)
curl http://localhost:8081/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen3.5-35b-a3b",
    "messages": [{"role": "user", "content": "Hello!"}]
  }' | jq .

# With system prompt
curl http://localhost:8081/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen3.5-35b-a3b",
    "messages": [
      {"role": "system", "content": "You are a coding expert."},
      {"role": "user", "content": "Write Python hello world"}
    ]
  }' | jq .

# Streaming
curl http://localhost:8081/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen3.5-35b-a3b",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": true
  }'
```

---

## Error Handling

### Error Response Format

```json
{
  "error": {
    "message": "Error description",
    "type": "error_type",
    "code": "error_code",
    "param": null
  }
}
```

### Common Errors

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| 400 | bad_request | Invalid parameters |
| 401 | authentication_error | Invalid API key |
| 404 | not_found | Model not found |
| 429 | rate_limit_error | Too many requests |
| 500 | server_error | Internal server error |
| 503 | service_unavailable | Server not ready |

### Python Error Handling

```python
from openai import OpenAI, APIError, APIConnectionError, RateLimitError

# Port is configured in config.yaml (server.port)
client = OpenAI(
    base_url="http://localhost:8081/v1",
    api_key="not-needed"
)

try:
    response = client.chat.completions.create(
        model="qwen3.5-35b-a3b",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print(response.choices[0].message.content)
except RateLimitError as e:
    print(f"Rate limit exceeded: {e.message}")
except APIConnectionError as e:
    print(f"Connection error: {e.message}")
except APIError as e:
    print(f"API error: {e.message}")
except Exception as e:
    print(f"Error: {str(e)}")
```

---

## Performance Metrics

### Response Timings

The API returns detailed timing information:

```json
"timings": {
    "prompt_ms": 123.5,           // Time to process prompt
    "prompt_per_second": 113.6,   // Prompt processing speed
    "predicted_ms": 285.3,        // Time for generation
    "predicted_per_second": 35.1  // Generation speed
}
```

### Expected Performance (M4 Pro)

| Metric | Expected Value |
|--------|----------------|
| Prompt Processing | 100-200 tokens/sec |
| Generation Speed | 30-40 tokens/sec |
| Time to First Token | 100-500ms |
| Total Latency (100 tokens) | 3-5 seconds |

---

## Advanced Usage

### System Prompts

```python
response = client.chat.completions.create(
    model="qwen3.5-35b-a3b",
    messages=[
        {
            "role": "system",
            "content": "You are an expert software engineer. Write clean, efficient code with explanations."
        },
        {
            "role": "user",
            "content": "Write a Python function to sort a list."
        }
    ]
)
```

### Multi-Turn Conversation

```python
messages = [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "What is Python?"},
    {"role": "assistant", "content": "Python is a programming language..."},
    {"role": "user", "content": "Show me an example."}
]

response = client.chat.completions.create(
    model="qwen3.5-35b-a3b",
    messages=messages
)
```

### Temperature Tuning

```python
# Factual/responsive (more deterministic)
response = client.chat.completions.create(
    model="qwen3.5-35b-a3b",
    messages=[{"role": "user", "content": "What is 2+2?"}],
    temperature=0.3
)

# Creative (more varied)
response = client.chat.completions.create(
    model="qwen3.5-35b-a3b",
    messages=[{"role": "user", "content": "Write a poem."}],
    temperature=0.9
)
```

### Max Tokens Control

```python
# Unlimited (waits for complete response)
response = client.chat.completions.create(
    model="qwen3.5-35b-a3b",
    messages=[{"role": "user", "content": "Explain AI."}],
    max_tokens=None
)

# Limited (faster initial response)
response = client.chat.completions.create(
    model="qwen3.5-35b-a3b",
    messages=[{"role": "user", "content": "Explain AI."}],
    max_tokens=200
)
```

---

## Server Configuration

### Start with Custom Settings

```bash
# Note: Default port is configured in config.yaml (server.port)

# Custom port (overrides config.yaml)
./bin/start-webui.sh ~/models/model.gguf 8000

# Custom context size (use port from config.yaml)
./bin/start-webui.sh ~/models/model.gguf 8081 65536

# Full control
llama-server \
    -m ~/models/model.gguf \
    --port 8081 \
    --ctx-size 131072 \
    --n-gpu-layers 999 \
    --threads 8
```

### Environment Variables

```bash
# Note: Port should match config.yaml (server.port)
export QWEN_API_BASE="http://localhost:8081/v1"
export QWEN_MODEL="qwen3.5-35b-a3b"
```

---

## Troubleshooting

### Server Not Responding

```bash
# Check if running (use port from config.yaml)
curl http://localhost:8081/health

# Start server
./bin/start-webui.sh

# Check logs
cat /tmp/llama-server.log
```

### Model Not Found

```bash
# List available models (use port from config.yaml)
curl http://localhost:8081/v1/models | jq .

# Check model path
source scripts/config.sh
echo $MODEL_PATH
```

### Slow Responses

```bash
# Check GPU offloading
grep "offloading" /tmp/llama-server.log

# Reduce context size (use port from config.yaml)
./bin/start-webui.sh ~/models/model.gguf 8081 32768
```

### API Errors

```bash
# Test API
./bin/test-api.sh

# Check server health (use port from config.yaml)
curl http://localhost:8081/health

# View detailed logs
tail -f /tmp/llama-server.log
```

---

## See Also

- [README.md](../README.md) - Main documentation
- [QUICKSTART.md](QUICKSTART.md) - Getting started
- [CLAUDE-CODE.md](../CLAUDE-CODE.md) - Claude Code integration
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference) - Official docs
