#!/usr/bin/env python3
"""
Qwen3.5-35B-A3B Python Client Example

Usage:
    python qwen.py "What is quantum computing?"
    python qwen.py --chat  # Interactive mode
"""

import argparse
import sys
from openai import OpenAI


def create_client():
    """Create OpenAI-compatible client for local llama.cpp server."""
    return OpenAI(
        base_url="http://localhost:8080/v1",
        api_key="not-needed"
    )


def chat(client, message, max_tokens=None, system_prompt=None):
    """Send a chat message and return the response."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model="qwen3.5-35b-a3b",
        messages=messages,
        max_tokens=max_tokens,
        stream=False
    )

    return response.choices[0].message.content


def interactive_mode(client):
    """Run interactive chat session."""
    print("╔══════════════════════════════════════════════════════════╗")
    print("║        Qwen3.5-35B-A3B Interactive Chat                  ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print("Commands:")
    print("  /quit, /exit  - Exit chat")
    print("  /clear        - Clear conversation history")
    print()

    messages = [
        {"role": "system", "content": "You are a helpful, harmless, and honest AI assistant."}
    ]

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("/quit", "/exit"):
            print("Goodbye!")
            break

        if user_input.lower() == "/clear":
            messages = messages[:1]  # Keep system prompt
            print("Conversation cleared.")
            continue

        messages.append({"role": "user", "content": user_input})

        try:
            response = client.chat.completions.create(
                model="qwen3.5-35b-a3b",
                messages=messages,
                max_tokens=None,
                stream=True
            )

            print("Assistant: ", end="", flush=True)
            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content
            print()

            messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="Qwen3.5-35B-A3B Client")
    parser.add_argument("prompt", nargs="?", help="Prompt to send")
    parser.add_argument("--chat", action="store_true", help="Interactive mode")
    parser.add_argument("--tokens", type=int, default=None, help="Max tokens (default: unlimited)")
    parser.add_argument("--system", type=str, help="System prompt")
    args = parser.parse_args()

    try:
        client = create_client()
        # Test connection
        client.models.list()
    except Exception as e:
        print(f"Error connecting to server: {e}")
        print("Make sure llama-server is running: ./start-qwen.sh")
        sys.exit(1)

    if args.chat:
        interactive_mode(client)
    elif args.prompt:
        response = chat(client, args.prompt, args.tokens, args.system)
        print(response)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
