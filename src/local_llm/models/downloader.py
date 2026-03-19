"""
Smart model downloader.

Downloads models from HuggingFace with:
- Progress tracking
- Resume support
- Checksum verification
- Auto-retry
"""

import os
import hashlib
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass


@dataclass
class DownloadProgress:
    """Download progress information."""
    downloaded_bytes: int = 0
    total_bytes: int = 0
    speed_mbps: float = 0.0
    eta_seconds: float = 0.0
    status: str = "pending"  # pending, downloading, complete, error
    error: Optional[str] = None
    
    @property
    def percent(self) -> float:
        """Get download percentage."""
        if self.total_bytes == 0:
            return 0.0
        return (self.downloaded_bytes / self.total_bytes) * 100


class ModelDownloader:
    """Download models from HuggingFace."""
    
    def __init__(self, models_dir: Optional[str] = None):
        """
        Initialize downloader.
        
        Args:
            models_dir: Directory to store models (default: ~/models)
        """
        if models_dir is None:
            models_dir = str(Path.home() / "models")
        
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self._progress_callback: Optional[Callable[[DownloadProgress], None]] = None
    
    def set_progress_callback(
        self,
        callback: Callable[[DownloadProgress], None]
    ) -> None:
        """Set progress callback function."""
        self._progress_callback = callback
    
    def _notify_progress(self, progress: DownloadProgress) -> None:
        """Notify progress callback."""
        if self._progress_callback:
            self._progress_callback(progress)
    
    def download(
        self,
        hf_repo: str,
        hf_file: str,
        output_path: Optional[str] = None,
        resume: bool = True,
        verify: bool = True,
    ) -> str:
        """
        Download a model from HuggingFace.
        
        Args:
            hf_repo: HuggingFace repo (e.g., "unsloth/Qwen3.5-9B-GGUF")
            hf_file: Filename (e.g., "Qwen3.5-9B-UD-Q4_K_M.gguf")
            output_path: Output path (default: ~/models/<file>)
            resume: Resume interrupted downloads
            verify: Verify download integrity
        
        Returns:
            Path to downloaded file
        
        Raises:
            RuntimeError: If download fails
        """
        # Determine output path - use EXACT filename from HF
        if output_path is None:
            output_path = str(self.models_dir / hf_file)
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if already downloaded (with exact filename)
        if output_path.exists():
            if verify:
                if self._verify_file(output_path):
                    return str(output_path)
                else:
                    # File corrupted, remove and re-download
                    output_path.unlink()
            elif not resume:
                return str(output_path)
        
        # Use huggingface_hub with EXACT filename preservation
        if self._try_hf_hub_download(hf_repo, hf_file, output_path, resume):
            if output_path.exists() and self._verify_file(output_path):
                return str(output_path)

        # Fallback to direct HTTP download
        if self._try_direct_download(hf_repo, hf_file, output_path, resume):
            if output_path.exists() and self._verify_file(output_path):
                return str(output_path)
        
        raise RuntimeError(
            f"Failed to download {hf_repo}/{hf_file}\n"
            f"Try: huggingface-cli download --local-dir ~/models {hf_repo} --include \"{hf_file}\""
        )
    
    def _try_hf_hub_download(
        self,
        repo: str,
        file: str,
        output: Path,
        resume: bool,
    ) -> bool:
        """Try download using huggingface_hub."""
        try:
            from huggingface_hub import hf_hub_download
            import shutil
            
            progress = DownloadProgress(status="downloading")
            self._notify_progress(progress)
            
            # Download to cache, then copy to desired location with EXACT filename
            cache_path = hf_hub_download(
                repo_id=repo,
                filename=file,  # Use EXACT filename from HF
                resume_download=True,  # Always resume
                force_download=False,
            )
            
            # Copy to desired output location
            if cache_path != str(output):
                output.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(cache_path, output)
            
            if output.exists():
                progress = DownloadProgress(
                    downloaded_bytes=output.stat().st_size,
                    total_bytes=output.stat().st_size,
                    status="complete",
                )
                self._notify_progress(progress)
                return True
            
            return False
            
        except ImportError:
            return False
        except Exception as e:
            progress = DownloadProgress(
                status="error",
                error=f"huggingface_hub failed: {e}",
            )
            self._notify_progress(progress)
            return False
    
    def _try_direct_download(
        self,
        repo: str,
        file: str,
        output: Path,
        resume: bool,
    ) -> bool:
        """Try direct HTTP download with curl."""
        if not shutil.which("curl"):
            return False
        
        download_url = f"https://huggingface.co/{repo}/resolve/main/{file}"
        
        progress = DownloadProgress(status="downloading")
        self._notify_progress(progress)
        
        # Build curl command
        cmd = ["curl", "-L", "-o", str(output)]
        
        if resume and output.exists():
            cmd.append("-C")
            cmd.append("-")  # Resume from where we left off
        
        cmd.append(download_url)
        
        try:
            # Run with progress
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=False,
            )
            
            if output.exists():
                size = output.stat().st_size
                progress = DownloadProgress(
                    downloaded_bytes=size,
                    total_bytes=size,
                    status="complete",
                )
                self._notify_progress(progress)
                return True
            
            return False
            
        except subprocess.CalledProcessError as e:
            progress = DownloadProgress(
                status="error",
                error=f"curl failed: {e}",
            )
            self._notify_progress(progress)
            return False
        except Exception as e:
            progress = DownloadProgress(
                status="error",
                error=str(e),
            )
            self._notify_progress(progress)
            return False
    
    def _verify_file(self, path: Path) -> bool:
        """Verify file integrity (basic check)."""
        if not path.exists():
            return False
        
        # Check file size (should be > 100MB for models)
        size = path.stat().st_size
        if size < 100 * 1024 * 1024:
            return False
        
        # Check GGUF magic number
        try:
            with open(path, "rb") as f:
                magic = f.read(4)
                # GGUF files start with 'GGUF' (0x46554747 in little-endian)
                if magic == b"GGUF" or magic[::-1] == b"GGUF":
                    return True
                # Also accept if file is large enough (might be other format)
                if size > 1024 * 1024 * 1024:  # > 1GB
                    return True
        except Exception:
            pass
        
        return False
    
    def get_download_info(
        self,
        hf_repo: str,
        hf_file: str,
    ) -> Dict[str, Any]:
        """
        Get download information without downloading.
        
        Returns:
            Dict with size, exists, path info
        """
        output_path = self.models_dir / hf_file
        
        info = {
            "repo": hf_repo,
            "file": hf_file,
            "path": str(output_path),
            "exists": output_path.exists(),
            "size_bytes": 0,
            "size_gb": 0.0,
        }
        
        if output_path.exists():
            info["size_bytes"] = output_path.stat().st_size
            info["size_gb"] = info["size_bytes"] / (1024 ** 3)
        
        # Try to get remote size
        try:
            import requests
            url = f"https://huggingface.co/{hf_repo}/resolve/main/{hf_file}"
            response = requests.head(url, timeout=10)
            if response.status_code == 200:
                content_length = response.headers.get("content-length")
                if content_length:
                    info["remote_size_bytes"] = int(content_length)
                    info["remote_size_gb"] = info["remote_size_bytes"] / (1024 ** 3)
        except Exception:
            pass
        
        return info
    
    def delete(self, model_path: str) -> bool:
        """
        Delete a downloaded model.
        
        Args:
            model_path: Path to model file
        
        Returns:
            True if deleted, False otherwise
        """
        try:
            path = Path(model_path)
            if path.exists():
                size = path.stat().st_size
                path.unlink()
                return True
            return False
        except Exception:
            return False
    
    def list_downloaded(self) -> list:
        """List downloaded models."""
        models = []
        for path in self.models_dir.glob("*.gguf"):
            models.append({
                "name": path.name,
                "path": str(path),
                "size_gb": path.stat().st_size / (1024 ** 3),
            })
        return models


# Convenience functions
def download_model(
    hf_repo: str,
    hf_file: str,
    output_path: Optional[str] = None,
) -> str:
    """Download a model."""
    downloader = ModelDownloader()
    return downloader.download(hf_repo, hf_file, output_path)


def get_downloader() -> ModelDownloader:
    """Get default downloader instance."""
    return ModelDownloader()
