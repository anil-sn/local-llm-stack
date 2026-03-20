"""
Pytest configuration and fixtures for Local LLM Stack CLI tests.

This module provides shared fixtures and utilities for testing CLI commands
without mocking - using actual system calls and real configurations.
"""

import os
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Optional

import pytest
import yaml


# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
CONFIG_FILE = PROJECT_ROOT / "config.yaml"

# Add src to path for imports
sys.path.insert(0, str(SRC_DIR))


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get project root directory."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def config_file() -> Path:
    """Get config.yaml path."""
    return CONFIG_FILE


@pytest.fixture
def temp_dir() -> Path:
    """Create a temporary directory for test artifacts."""
    tmp = tempfile.mkdtemp(prefix="llm-stack-test-")
    yield Path(tmp)
    # Cleanup
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def temp_config_file(temp_dir: Path) -> Path:
    """Create a temporary config file for testing."""
    # Load original config
    with open(CONFIG_FILE, "r") as f:
        config_data = yaml.safe_load(f)

    # Modify paths for testing
    config_data["paths"] = {
        "log_file": str(temp_dir / "llama-server.log"),
        "pid_file": str(temp_dir / "llama-server.pid"),
        "venv_dir": str(temp_dir / ".venv"),
        "benchmark_dir": str(temp_dir / "benchmarks"),
        "build_dir": str(temp_dir / "llama.cpp"),
        "install_dir": str(temp_dir / "bin"),
    }

    # Write temp config
    temp_config = temp_dir / "config.yaml"
    with open(temp_config, "w") as f:
        yaml.dump(config_data, f, default_flow_style=False)

    yield temp_config


@pytest.fixture
def cli_env() -> dict:
    """Get environment variables for CLI commands."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_DIR)
    return env


@pytest.fixture
def run_cli(cli_env: dict):
    """
    Fixture to run CLI commands.

    Usage:
        def test_something(run_cli):
            result = run_cli(["--help"])
            assert result.returncode == 0
    """
    def _run_cli(
        args: list,
        cwd: Optional[Path] = None,
        timeout: int = 30,
        capture_output: bool = True,
    ) -> subprocess.CompletedProcess:
        """Run CLI command and return result."""
        # Use the installed CLI command (local-llm)
        cmd = ["local-llm"] + args

        result = subprocess.run(
            cmd,
            cwd=cwd or PROJECT_ROOT,
            env=cli_env,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
        )

        return result

    return _run_cli


@pytest.fixture
def check_llama_tools():
    """Check if llama.cpp tools are available."""
    import shutil

    tools = {
        "llama-server": shutil.which("llama-server"),
        "llama-cli": shutil.which("llama-cli"),
        "llama-bench": shutil.which("llama-bench"),
        "llama-perplexity": shutil.which("llama-perplexity"),
    }

    return tools


@pytest.fixture
def gpu_available():
    """Check if GPU is available."""
    import shutil
    import subprocess

    # Check NVIDIA
    if shutil.which("nvidia-smi"):
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                return {"available": True, "type": "cuda", "name": result.stdout.strip()}
        except Exception:
            pass

    # Check Apple Metal
    if sys.platform == "darwin":
        try:
            result = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and "apple" in result.stdout.lower():
                return {"available": True, "type": "metal", "name": result.stdout.strip()}
        except Exception:
            pass

    return {"available": False, "type": "none", "name": "CPU only"}


@pytest.fixture
def server_port() -> int:
    """Get an available port for testing."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]

    return port


@pytest.fixture
def sample_model_ref():
    """Sample model reference for testing."""
    return {
        "key": "llama-3-8b",
        "name": "Llama-3-8B-Instruct-Q4_K_M.gguf",
        "hf_repo": "unsloth/Llama-3-8B-Instruct-GGUF",
        "hf_file": "Llama-3-8B-Instruct-Q4_K_M.gguf",
        "size_gb": 5,
        "ram_required_gb": 16,
    }


@pytest.fixture
def detector():
    """Create hardware detector instance."""
    from local_llm.hardware.detector import HardwareDetector
    return HardwareDetector()


@pytest.fixture(autouse=True)
def set_working_directory(project_root: Path):
    """Set working directory to project root for all tests."""
    original_cwd = os.getcwd()
    os.chdir(project_root)
    yield
    os.chdir(original_cwd)
