#!/usr/bin/env python3
"""
Setup script for Local LLM Stack CLI

Install with:
    pip install -e .

Or for development:
    pip install -e ".[dev]"
"""

from pathlib import Path
from setuptools import setup, find_packages

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")

# Read requirements
requirements_path = Path(__file__).parent / "src" / "local_llm" / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = [
        line.strip()
        for line in requirements_path.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]

# Development requirements
dev_requirements = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
    "types-PyYAML>=6.0.0",
    "types-requests>=2.31.0",
]

setup(
    name="local-llm-stack",
    version="1.0.0",
    author="Local LLM Stack Contributors",
    author_email="local-llm-stack@example.com",
    description="Professional CLI for managing local LLM inference",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anil-sn/local-llm-stack",
    project_urls={
        "Bug Tracker": "https://github.com/anil-sn/local-llm-stack/issues",
        "Documentation": "https://github.com/anil-sn/local-llm-stack#readme",
    },
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Typing :: Typed",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "all": requirements + dev_requirements,
    },
    entry_points={
        "console_scripts": [
            "llm-stack=local_llm.cli.main:app",
            "local-llm=local_llm.cli.main:app",  # Alternative name
        ],
    },
    include_package_data=True,
    package_data={
        "local_llm": [
            "py.typed",
            "requirements.txt",
        ],
    },
    keywords=[
        "llm",
        "llama",
        "llama.cpp",
        "qwen",
        "mistral",
        "gemma",
        "phi",
        "inference",
        "cli",
        "local-llm",
        "gguf",
    ],
)
