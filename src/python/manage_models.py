#!/usr/bin/env python3
"""
Model Management Utility for Local LLM Stack

Download, list, select, and delete models with ease.

Usage:
    python manage_models.py list              # List all available models
    python manage_models.py download qwen-35b-a3b   # Download a model
    python manage_models.py select llama-3-8b       # Switch active model
    python manage_models.py status            # Show current model status
    python manage_models.py delete mistral-7b # Delete a downloaded model
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent))

from config import Config


class ModelManager:
    """Manage LLM models - download, select, list, delete."""

    def __init__(self):
        self.config = Config()
        self.models_dir = str(Path.home() / "models")

    def list_models(self) -> List[Dict]:
        """List all configured models with their status."""
        models = self.config.get("models", default={})
        active_key = self.config.get("active_model", default="qwen-35b-a3b")

        result = []
        for key, model in models.items():
            model_path = model.get("path", "").replace("$HOME", str(Path.home()))
            exists = os.path.isfile(model_path)
            size_gb = model.get("size_gb", 0)
            ram_gb = model.get("ram_required_gb", 0)

            result.append({
                "key": key,
                "name": model.get("name", "Unknown"),
                "description": model.get("description", ""),
                "size_gb": size_gb,
                "ram_required_gb": ram_gb,
                "hf_repo": model.get("hf_repo", ""),
                "hf_file": model.get("hf_file", ""),
                "path": model_path,
                "downloaded": exists,
                "is_active": key == active_key,
            })

        return result

    def parse_hf_reference(self, ref: str) -> Optional[tuple]:
        """
        Parse HuggingFace reference like 'unsloth/Qwen3.5-9B-GGUF:UD-Q4_K_XL'
        Returns (repo, file) tuple or None if invalid.
        """
        # Check if it looks like a HF reference (contains '/')
        if '/' not in ref:
            return None

        # Split repo and quant
        if ':' in ref:
            repo_part, quant = ref.split(':', 1)
            # Construct filename from repo name + quant
            # e.g., unsloth/Qwen3.5-9B-GGUF:UD-Q4_K_XL -> qwen3.5-9b-UD-Q4_K_XL.gguf
            repo_name = repo_part.split('/')[-1]  # e.g., Qwen3.5-9B-GGUF
            # Remove -GGUF suffix if present
            if repo_name.upper().endswith('-GGUF'):
                repo_name = repo_name[:-5]
            # Convert to lowercase and add quant
            hf_file = f"{repo_name.lower()}-{quant}.gguf"
        else:
            repo_part = ref
            hf_file = None

        return (repo_part, hf_file)

    def download_model(self, model_key: str) -> bool:
        """Download a model from HuggingFace."""
        models = self.config.get("models", default={})

        # Check if this is a HuggingFace reference (e.g., unsloth/Qwen3.5-9B-GGUF:UD-Q4_K_XL)
        hf_ref = self.parse_hf_reference(model_key)
        if hf_ref:
            hf_repo, hf_file = hf_ref
            # For HF references, we need to extract a name from the quant
            if hf_file:
                quant_name = hf_file.replace('.gguf', '')
                model_name = f"{hf_repo.split('/')[-1]}:{quant_name}"
                model_path = str(Path.home() / "models" / hf_file)
                size_gb = 0  # Unknown for direct HF refs
            else:
                print(f"❌ Invalid HuggingFace reference: {model_key}")
                print(f"   Expected format: repo:quant (e.g., unsloth/Qwen3.5-9B-GGUF:UD-Q4_K_XL)")
                return False
        elif model_key in models:
            model = models[model_key]
            hf_repo = model.get("hf_repo", "")
            hf_file = model.get("hf_file", "")
            model_path = model.get("path", "").replace("$HOME", str(Path.home()))
            size_gb = model.get("size_gb", 0)
            model_name = model.get("name", model_key)
        else:
            print(f"❌ Model '{model_key}' not found in configuration.")
            print(f"   Available models: {', '.join(models.keys())}")
            print()
            print("💡 You can also use HuggingFace references directly:")
            print("   ./bin/models download unsloth/Qwen3.5-9B-GGUF:UD-Q4_K_XL")
            return False

        # Check if already downloaded
        if os.path.isfile(model_path):
            size = self._get_file_size(model_path)
            print(f"✅ Model already downloaded: {model_path}")
            print(f"   Size: {size}")
            print()
            response = input("Download anyway? [y/N] ").strip().lower()
            if response != 'y' and response != 'yes':
                return True

        # Check for huggingface_hub Python package
        try:
            from huggingface_hub import hf_hub_download
        except ImportError:
            print("📦 Installing huggingface_hub...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "-U", "huggingface_hub"], check=True)
                from huggingface_hub import hf_hub_download
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install huggingface_hub: {e}")
                return False
            except ImportError:
                print("❌ Failed to import huggingface_hub after installation")
                return False

        # Create models directory
        os.makedirs(self.models_dir, exist_ok=True)

        size_str = f" (~{size_gb}GB)" if size_gb > 0 else ""
        print(f"📥 Downloading {model_name}{size_str}...")
        print(f"   Source: {hf_repo}")
        print(f"   Destination: {model_path}")
        print()

        try:
            # Use requests with SSL verification disabled for problematic certs
            import requests
            from urllib.parse import urljoin
            
            download_url = f"https://huggingface.co/{hf_repo}/resolve/main/{hf_file}"
            
            print(f"   URL: {download_url}")
            print()
            
            # Stream download with progress
            response = requests.get(download_url, stream=True, verify=False, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            block_size = 8192
            downloaded = 0
            
            with open(model_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=block_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Show progress
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            bar_length = 40
                            filled = int(bar_length * downloaded / total_size)
                            bar = '█' * filled + '░' * (bar_length - filled)
                            mb_downloaded = downloaded / (1024 * 1024)
                            mb_total = total_size / (1024 * 1024)
                            print(f'\r   [{bar}] {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)', end='', flush=True)
            
            print()  # Newline after progress

            # Verify download
            if os.path.isfile(model_path):
                size = self._get_file_size(model_path)
                print()
                print("✅ Download complete!")
                print(f"   Location: {model_path}")
                print(f"   Size: {size}")
                return True
            else:
                print("❌ Download failed - file not found!")
                return False

        except KeyboardInterrupt:
            print("\n⚠️  Download cancelled by user")
            # Clean up partial download
            if os.path.exists(model_path):
                os.remove(model_path)
            return False
        except Exception as e:
            print(f"\n❌ Download failed: {e}")
            # Clean up partial download
            if os.path.exists(model_path):
                os.remove(model_path)
            print()
            print("Alternative: Download manually with curl:")
            print(f"   curl -L -o \"{model_path}\" \"https://huggingface.co/{hf_repo}/resolve/main/{hf_file}\"")
            return False

    def select_model(self, model_key: str) -> bool:
        """Set a model as active in config.yaml."""
        models = self.config.get("models", default={})

        if model_key not in models:
            print(f"❌ Model '{model_key}' not found in configuration.")
            print(f"   Available models: {', '.join(models.keys())}")
            return False

        # Check if model is downloaded
        model_path = models[model_key].get("path", "").replace("$HOME", str(Path.home()))
        if not os.path.isfile(model_path):
            print(f"⚠️  Model '{model_key}' is not downloaded.")
            print(f"   Download it first with: python manage_models.py download {model_key}")
            print()
            response = input("Download now? [y/N] ").strip().lower()
            if response == 'y' or response == 'yes':
                return self.download_model(model_key)
            return False

        # Update config.yaml
        config_path = self.config.get_config_path()
        try:
            with open(config_path, 'r') as f:
                content = f.read()

            # Replace active_model line
            old_line = f'active_model: {self.config.get("active_model", default="qwen-35b-a3b")}'
            new_line = f'active_model: {model_key}'
            content = content.replace(old_line, new_line)

            with open(config_path, 'w') as f:
                f.write(content)

            # Regenerate .env file
            self._generate_env_file()

            print(f"✅ Active model switched to: {model_key}")
            print(f"   Model: {models[model_key].get('name')}")
            print(f"   Description: {models[model_key].get('description', '')}")
            return True

        except Exception as e:
            print(f"❌ Failed to update config: {e}")
            return False

    def _generate_env_file(self):
        """Regenerate .env file from config.yaml"""
        try:
            # Add parent directory to path for scripts import
            script_dir = Path(__file__).parent.parent.parent / "scripts"
            sys.path.insert(0, str(script_dir))
            from generate_env import generate_env
            generate_env()
        except Exception as e:
            print(f"⚠️  Warning: Failed to regenerate .env: {e}")

    def delete_model(self, model_key: str) -> bool:
        """Delete a downloaded model file."""
        models = self.config.get("models", default={})

        if model_key not in models:
            print(f"❌ Model '{model_key}' not found in configuration.")
            return False

        model_path = models[model_key].get("path", "").replace("$HOME", str(Path.home()))

        if not os.path.isfile(model_path):
            print(f"ℹ️  Model '{model_key}' is not downloaded.")
            return True

        size = self._get_file_size(model_path)
        print(f"⚠️  This will delete: {model_path}")
        print(f"   Size: {size}")
        print()
        response = input("Are you sure? [y/N] ").strip().lower()

        if response != 'y' and response != 'yes':
            print("Cancelled.")
            return True

        try:
            os.remove(model_path)
            print(f"✅ Model deleted: {model_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to delete: {e}")
            return False

    def get_status(self) -> Dict:
        """Get current model status."""
        active_key = self.config.get("active_model", default="qwen-35b-a3b")
        active_model = self.config.get_model("active_model")

        model_path = active_model.get("path", "").replace("$HOME", str(Path.home()))
        exists = os.path.isfile(model_path)
        size = self._get_file_size(model_path) if exists else "N/A"

        return {
            "active_model": active_key,
            "model_name": active_model.get("name", "Unknown"),
            "description": active_model.get("description", ""),
            "path": model_path,
            "downloaded": exists,
            "size": size,
            "ram_required_gb": active_model.get("ram_required_gb", 0),
            "server_port": self.config.get("server", "port", default=8081),
        }

    def _get_file_size(self, path: str) -> str:
        """Get human-readable file size."""
        try:
            size_bytes = os.path.getsize(path)
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.2f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.2f} PB"
        except:
            return "Unknown"


def print_model_table(models: List[Dict]):
    """Print models in a formatted table."""
    if not models:
        print("No models configured.")
        return

    # Find max widths
    max_key = max(len(m["key"]) for m in models)
    max_name = max(len(m["name"]) for m in models)
    max_desc = min(50, max(len(m["description"]) for m in models))

    print("╔" + "═" * (max_key + max_name + max_desc + 15) + "╗")
    print("║  Available Models")
    print("╠" + "─" * (max_key + max_name + max_desc + 15) + "╣")

    for model in models:
        status = "●" if model["is_active"] else ("✅" if model["downloaded"] else "○")
        key = model["key"].ljust(max_key)
        name = model["name"][:max_name].ljust(max_name)
        desc = model["description"][:max_desc].ljust(max_desc)
        size = f"{model['size_gb']}GB"
        ram = f"{model['ram_required_gb']}GB"

        print(f"║ {status} {key} │ {name} │ {desc} │ {size:>6} │ {ram:>5} RAM ║")

    print("╚" + "═" * (max_key + max_name + max_desc + 15) + "╝")
    print()
    print("Legend: ● Active  ✅ Downloaded  ○ Not downloaded")


def main():
    parser = argparse.ArgumentParser(
        description="Model Management Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python manage_models.py list                    # List all models
  python manage_models.py download qwen-35b-a3b   # Download Qwen 35B
  python manage_models.py select llama-3-8b       # Switch to Llama 3 8B
  python manage_models.py status                  # Show current status
  python manage_models.py delete mistral-7b       # Delete Mistral 7B
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # List command
    subparsers.add_parser("list", help="List all available models")

    # Download command
    download_parser = subparsers.add_parser("download", help="Download a model")
    download_parser.add_argument("model", help="Model key to download")

    # Select command
    select_parser = subparsers.add_parser("select", help="Select active model")
    select_parser.add_argument("model", help="Model key to select")

    # Status command
    subparsers.add_parser("status", help="Show current model status")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a model")
    delete_parser.add_argument("model", help="Model key to delete")

    args = parser.parse_args()
    manager = ModelManager()

    if args.command == "list":
        print("╔══════════════════════════════════════════════════════════╗")
        print("║         Available Models                                 ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print()
        models = manager.list_models()
        print_model_table(models)
        print("Usage: python manage_models.py download <model-key>")
        print("       python manage_models.py select <model-key>")

    elif args.command == "download":
        print("╔══════════════════════════════════════════════════════════╗")
        print("║         Download Model                                   ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print()
        success = manager.download_model(args.model)
        sys.exit(0 if success else 1)

    elif args.command == "select":
        print("╔══════════════════════════════════════════════════════════╗")
        print("║         Select Active Model                              ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print()
        success = manager.select_model(args.model)
        sys.exit(0 if success else 1)

    elif args.command == "status":
        print("╔══════════════════════════════════════════════════════════╗")
        print("║         Current Model Status                             ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print()
        status = manager.get_status()
        print(f"Active Model: {status['active_model']}")
        print(f"Name: {status['model_name']}")
        print(f"Description: {status['description']}")
        print(f"Downloaded: {'✅ Yes' if status['downloaded'] else '❌ No'}")
        if status['downloaded']:
            print(f"Size: {status['size']}")
        print(f"Path: {status['path']}")
        print(f"RAM Required: {status['ram_required_gb']}GB")
        print(f"Server Port: {status['server_port']}")
        print()
        if not status['downloaded']:
            print(f"💡 Download this model with:")
            print(f"   python manage_models.py download {status['active_model']}")

    elif args.command == "delete":
        print("╔══════════════════════════════════════════════════════════╗")
        print("║         Delete Model                                     ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print()
        success = manager.delete_model(args.model)
        sys.exit(0 if success else 1)

    else:
        parser.print_help()
        print()
        print("Quick Start:")
        print("  python manage_models.py status    # Check current model")
        print("  python manage_models.py list      # See all models")
        print("  python manage_models.py download qwen-35b-a3b  # Download main model")


if __name__ == "__main__":
    main()
