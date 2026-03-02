"""
Local LLM Stack - Professional CLI for Local LLM Management

A unified command-line interface for managing local LLM inference,
supporting Qwen, Llama, Mistral, Gemma, Phi and other models.
"""

__version__ = "1.0.0"
__author__ = "Local LLM Stack Contributors"

from local_llm.cli.main import app
from local_llm.config import Config

__all__ = ["app", "Config"]
