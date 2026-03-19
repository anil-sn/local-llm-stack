"""
Model resolution module.

Resolves model identifiers to downloadable models:
- HuggingFace URLs
- HF repo references (user/repo:file)
- Config model keys
- Partial name matches
"""

import re
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from pathlib import Path


@dataclass
class ModelReference:
    """Parsed model reference."""
    original: str
    ref_type: str  # url, hf_repo, config_key, partial
    hf_repo: Optional[str] = None
    hf_file: Optional[str] = None
    config_key: Optional[str] = None
    model_name: Optional[str] = None
    quantization: Optional[str] = None
    
    def is_downloadable(self) -> bool:
        """Check if this reference can be downloaded."""
        return self.ref_type in ("url", "hf_repo") and self.hf_repo is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "original": self.original,
            "ref_type": self.ref_type,
            "hf_repo": self.hf_repo,
            "hf_file": self.hf_file,
            "config_key": self.config_key,
            "model_name": self.model_name,
            "quantization": self.quantization,
        }


class ModelResolver:
    """Resolve model identifiers to downloadable models."""
    
    # Known GGUF repositories
    GGUF_REPOS = [
        "unsloth",
        "TheBloke",
        "MaziyarPanahi",
        "Jackrong",
        "bartowski",
        "MaziyarPanahi",
        "QuantFactory",
    ]
    
    # Common quantization patterns
    QUANT_PATTERNS = [
        r"Q4_K_M",
        r"Q4_K_S",
        r"Q5_K_M",
        r"Q5_K_S",
        r"Q6_K",
        r"Q8_0",
        r"UD-Q4_K_XL",
        r"UD-Q4_K_M",
        r"UD-Q5_K_M",
    ]
    
    def __init__(self, config=None):
        """
        Initialize resolver.
        
        Args:
            config: Config instance for looking up model keys
        """
        self.config = config
        self._model_cache: Optional[List[Dict]] = None
    
    def resolve(self, identifier: str) -> ModelReference:
        """
        Resolve a model identifier.
        
        Args:
            identifier: Model identifier (URL, repo, key, or partial name)
        
        Returns:
            ModelReference with parsed information
        """
        identifier = identifier.strip()
        
        # Try different resolution strategies
        ref = self._try_url(identifier)
        if ref:
            return ref
        
        ref = self._try_hf_repo(identifier)
        if ref:
            return ref
        
        ref = self._try_config_key(identifier)
        if ref:
            return ref
        
        ref = self._try_partial_match(identifier)
        if ref:
            return ref
        
        # No match - return as HF repo attempt
        return ModelReference(
            original=identifier,
            ref_type="unknown",
            hf_repo=identifier,
        )
    
    def _try_url(self, identifier: str) -> Optional[ModelReference]:
        """Try to parse as HuggingFace URL."""
        # https://huggingface.co/unsloth/Qwen3.5-9B-GGUF/blob/main/Qwen3.5-9B-UD-Q4_K_M.gguf
        url_pattern = r"huggingface\.co/([^/]+)/([^/]+?)(?:/blob/[^/]+/(.+))?"
        match = re.search(url_pattern, identifier)
        
        if match:
            repo = f"{match.group(1)}/{match.group(2)}"
            file = match.group(3) if match.group(3) else None
            
            # Extract quantization from filename
            quant = self._extract_quantization(file or "")
            
            return ModelReference(
                original=identifier,
                ref_type="url",
                hf_repo=repo,
                hf_file=file,
                quantization=quant,
            )
        
        return None
    
    def _try_hf_repo(self, identifier: str) -> Optional[ModelReference]:
        """Try to parse as HuggingFace repo reference."""
        # Format: user/repo or user/repo:quant or user/repo:file.gguf
        if "/" not in identifier:
            return None
        
        # Skip if it looks like a path
        if identifier.startswith("/") or identifier.startswith("."):
            return None
        
        # Split repo and quant/file
        quant_part = None
        if ":" in identifier:
            identifier, quant_part = identifier.rsplit(":", 1)
        
        # Validate repo format
        parts = identifier.split("/")
        if len(parts) != 2 or not all(parts):
            return None
        
        repo = identifier
        file = None
        quant = quant_part
        
        # If quant_part looks like a filename, use it as file
        if quant_part and (quant_part.endswith(".gguf") or quant_part.endswith(".safetensors")):
            file = quant_part
            quant = self._extract_quantization(file)
        elif quant_part:
            # Construct filename from quantization - preserve original case from repo name
            model_name = parts[1]  # Keep original case
            # Remove -GGUF suffix if present
            if model_name.upper().endswith('-GGUF'):
                model_name = model_name[:-5]
            file = f"{model_name}-{quant_part}.gguf"
        
        return ModelReference(
            original=identifier + (f":{quant_part}" if quant_part else ""),
            ref_type="hf_repo",
            hf_repo=repo,
            hf_file=file,
            quantization=quant,
            model_name=parts[1],
        )
    
    def _try_config_key(self, identifier: str) -> Optional[ModelReference]:
        """Try to match config model key."""
        if not self.config:
            return None
        
        try:
            models = self.config.get("models", default={})
            if identifier in models:
                model = models[identifier]
                return ModelReference(
                    original=identifier,
                    ref_type="config_key",
                    config_key=identifier,
                    hf_repo=model.get("hf_repo"),
                    hf_file=model.get("hf_file"),
                    model_name=model.get("name"),
                    quantization=self._extract_quantization(model.get("name", "")),
                )
        except Exception:
            pass
        
        return None
    
    def _try_partial_match(self, identifier: str) -> Optional[ModelReference]:
        """Try partial name match against known models."""
        if not self.config:
            return None
        
        try:
            models = self.config.get("models", default={})
            identifier_lower = identifier.lower()
            
            # Try exact substring match
            for key, model in models.items():
                name = model.get("name", "").lower()
                if identifier_lower in name or identifier_lower in key:
                    return ModelReference(
                        original=identifier,
                        ref_type="partial",
                        config_key=key,
                        hf_repo=model.get("hf_repo"),
                        hf_file=model.get("hf_file"),
                        model_name=model.get("name"),
                        quantization=self._extract_quantization(model.get("name", "")),
                    )
            
            # Try fuzzy match (remove separators)
            identifier_normalized = re.sub(r"[-_.\s]", "", identifier_lower)
            for key, model in models.items():
                name = model.get("name", "").lower()
                name_normalized = re.sub(r"[-_.\s]", "", name)
                if identifier_normalized in name_normalized:
                    return ModelReference(
                        original=identifier,
                        ref_type="partial",
                        config_key=key,
                        hf_repo=model.get("hf_repo"),
                        hf_file=model.get("hf_file"),
                        model_name=model.get("name"),
                        quantization=self._extract_quantization(model.get("name", "")),
                    )
        except Exception:
            pass
        
        return None
    
    def _extract_quantization(self, name: str) -> Optional[str]:
        """Extract quantization type from filename."""
        name_upper = name.upper()
        
        for pattern in self.QUANT_PATTERNS:
            if pattern.upper() in name_upper:
                # Find the actual case from original
                match = re.search(pattern, name, re.IGNORECASE)
                if match:
                    return match.group()
        
        # Check for common patterns
        if "Q4" in name_upper:
            return "Q4_K_M"
        elif "Q5" in name_upper:
            return "Q5_K_M"
        elif "Q6" in name_upper:
            return "Q6_K"
        elif "Q8" in name_upper:
            return "Q8_0"
        
        return None
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """List all models available in config."""
        if not self.config:
            return []
        
        try:
            models = self.config.get("models", default={})
            result = []
            
            for key, model in models.items():
                result.append({
                    "key": key,
                    "name": model.get("name", ""),
                    "hf_repo": model.get("hf_repo", ""),
                    "hf_file": model.get("hf_file", ""),
                    "size_gb": model.get("size_gb", 0),
                    "description": model.get("description", ""),
                })
            
            return result
        except Exception:
            return []
    
    def search_huggingface(
        self,
        query: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search HuggingFace for models.
        
        Args:
            query: Search query
            limit: Max results
        
        Returns:
            List of model info dicts
        """
        try:
            from huggingface_hub import list_models
            
            results = []
            for model in list_models(search=query, limit=limit):
                results.append({
                    "id": model.id,
                    "repo": model.id,
                    "downloads": getattr(model, "downloads", 0),
                    "likes": getattr(model, "likes", 0),
                })
            
            return results
        except ImportError:
            return []
        except Exception:
            return []


# Convenience function
def resolve_model(identifier: str, config=None) -> ModelReference:
    """Resolve a model identifier."""
    resolver = ModelResolver(config)
    return resolver.resolve(identifier)
