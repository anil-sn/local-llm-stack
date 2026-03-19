"""
Model recommendation engine.

Recommends models based on detected hardware and use case.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from local_llm.hardware.detector import HardwareInfo, GPUInfo


@dataclass
class Recommendation:
    """Model recommendation."""
    model_key: str
    model_name: str
    hf_repo: str
    hf_file: str
    size_gb: float
    ram_required_gb: float
    vram_required_gb: float
    description: str
    score: float  # 0-100 recommendation score
    reasons: List[str]
    use_cases: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model_key": self.model_key,
            "model_name": self.model_name,
            "hf_repo": self.hf_repo,
            "hf_file": self.hf_file,
            "size_gb": self.size_gb,
            "ram_required_gb": self.ram_required_gb,
            "vram_required_gb": self.vram_required_gb,
            "description": self.description,
            "score": self.score,
            "reasons": self.reasons,
            "use_cases": self.use_cases,
        }


class ModelRecommender:
    """Recommend models based on hardware and use case."""
    
    # Pre-configured model database
    MODELS = [
        {
            "key": "qwen3.5-35b-a3b",
            "name": "Qwen3.5-35B-A3B-Q5_K_M",
            "repo": "unsloth/Qwen3.5-35B-A3B-GGUF",
            "file": "Qwen3.5-35B-A3B-UD-Q5_K_M.gguf",
            "size_gb": 23,
            "ram_gb": 32,
            "vram_gb": 20,
            "description": "Qwen3.5 35B MoE - Best balance of speed and quality",
            "use_cases": ["general", "code", "reasoning"],
            "speed": 3,  # 1-5 scale
            "quality": 5,
        },
        {
            "key": "qwen3.5-9b",
            "name": "Qwen3.5-9B-Q4_K_M",
            "repo": "unsloth/Qwen3.5-9B-GGUF",
            "file": "Qwen3.5-9B-UD-Q4_K_M.gguf",
            "size_gb": 7,
            "ram_gb": 16,
            "vram_gb": 8,
            "description": "Qwen3.5 9B - Fast and efficient, great for most tasks",
            "use_cases": ["general", "chat", "code"],
            "speed": 5,
            "quality": 4,
        },
        {
            "key": "qwen3.5-27b-distilled",
            "name": "Qwen3.5-27B-Distilled-Q4_K_M",
            "repo": "Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled-GGUF",
            "file": "Qwen3.5-27B.Q4_K_M.gguf",
            "size_gb": 17,
            "ram_gb": 32,
            "vram_gb": 18,
            "description": "Qwen3.5 27B Distilled - Reasoning model distilled from Claude 4.6 Opus",
            "use_cases": ["reasoning", "code", "math"],
            "speed": 3,
            "quality": 5,
        },
        {
            "key": "llama-3-70b",
            "name": "Llama-3-70B-Instruct-Q4_K_M",
            "repo": "unsloth/Llama-3-70B-Instruct-GGUF",
            "file": "Llama-3-70B-Instruct-Q4_K_M.gguf",
            "size_gb": 42,
            "ram_gb": 64,
            "vram_gb": 24,
            "description": "Llama 3 70B - Highest quality, requires significant resources",
            "use_cases": ["general", "reasoning", "creative"],
            "speed": 2,
            "quality": 5,
        },
        {
            "key": "llama-3-8b",
            "name": "Llama-3-8B-Instruct-Q4_K_M",
            "repo": "unsloth/Llama-3-8B-Instruct-GGUF",
            "file": "Llama-3-8B-Instruct-Q4_K_M.gguf",
            "size_gb": 5,
            "ram_gb": 16,
            "vram_gb": 6,
            "description": "Llama 3 8B - Fast, low RAM usage",
            "use_cases": ["general", "chat", "code"],
            "speed": 5,
            "quality": 4,
        },
        {
            "key": "mistral-7b",
            "name": "Mistral-7B-Instruct-v0.3-Q4_K_M",
            "repo": "unsloth/Mistral-7B-Instruct-v0.3-GGUF",
            "file": "Mistral-7B-Instruct-v0.3-Q4_K_M.gguf",
            "size_gb": 4,
            "ram_gb": 8,
            "vram_gb": 5,
            "description": "Mistral 7B - Very fast, minimal RAM",
            "use_cases": ["general", "chat"],
            "speed": 5,
            "quality": 3,
        },
        {
            "key": "gemma-2-7b",
            "name": "Gemma-2-7B-Instruct-Q4_K_M",
            "repo": "unsloth/gemma-2-7b-Instruct-GGUF",
            "file": "gemma-2-7b-Instruct-Q4_K_M.gguf",
            "size_gb": 5,
            "ram_gb": 16,
            "vram_gb": 6,
            "description": "Gemma 2 7B - Efficient Google model",
            "use_cases": ["general", "chat", "code"],
            "speed": 5,
            "quality": 4,
        },
        {
            "key": "phi-3-mini",
            "name": "Phi-3-mini-4k-Instruct-Q4_K_M",
            "repo": "unsloth/Phi-3-mini-4k-instruct-GGUF",
            "file": "Phi-3-mini-4k-instruct-Q4_K_M.gguf",
            "size_gb": 2,
            "ram_gb": 8,
            "vram_gb": 3,
            "description": "Phi 3 Mini - Ultra fast, minimal resources",
            "use_cases": ["general", "chat"],
            "speed": 5,
            "quality": 3,
        },
    ]
    
    def __init__(self, hardware_info: Optional[HardwareInfo] = None):
        """
        Initialize recommender.
        
        Args:
            hardware_info: Hardware info (auto-detects if None)
        """
        self.hardware = hardware_info
        if self.hardware is None:
            from local_llm.hardware.detector import detect_hardware
            self.hardware = detect_hardware()
    
    def recommend(
        self,
        use_case: str = "general",
        priority: str = "balanced",
        limit: int = 3,
    ) -> List[Recommendation]:
        """
        Get model recommendations.
        
        Args:
            use_case: Primary use case (general, code, reasoning, chat, creative)
            priority: Priority (speed, quality, balanced)
            limit: Max recommendations to return
        
        Returns:
            List of recommendations sorted by score
        """
        recommendations = []
        
        for model in self.MODELS:
            # Check if model fits hardware
            fits, reasons = self._check_fit(model)
            
            if not fits:
                continue
            
            # Calculate score
            score = self._calculate_score(model, use_case, priority)
            
            # Create recommendation
            rec = Recommendation(
                model_key=model["key"],
                model_name=model["name"],
                hf_repo=model["repo"],
                hf_file=model["file"],
                size_gb=model["size_gb"],
                ram_required_gb=model["ram_gb"],
                vram_required_gb=model["vram_gb"],
                description=model["description"],
                score=score,
                reasons=reasons,
                use_cases=model["use_cases"],
            )
            recommendations.append(rec)
        
        # Sort by score descending
        recommendations.sort(key=lambda x: x.score, reverse=True)
        
        return recommendations[:limit]
    
    def _check_fit(self, model: Dict[str, Any]) -> tuple:
        """Check if model fits hardware. Returns (fits, reasons)."""
        reasons = []
        fits = True
        
        gpu = self.hardware.gpu
        mem = self.hardware.memory
        disk = self.hardware.disk
        
        # Check RAM
        if mem.available_gb < model["ram_gb"] * 0.8:
            fits = False
            reasons.append(f"Insufficient RAM: need {model['ram_gb']}GB, have {mem.available_gb:.1f}GB")
        else:
            reasons.append(f"✅ RAM sufficient ({mem.available_gb:.1f}GB available)")
        
        # Check VRAM for GPU offload
        if gpu.has_gpu:
            if gpu.vram_total_gb >= model["vram_gb"]:
                reasons.append(f"✅ Full GPU offload possible ({gpu.vram_total_gb:.1f}GB VRAM)")
            elif gpu.vram_total_gb >= model["vram_gb"] * 0.5:
                reasons.append(f"⚠️  Partial GPU offload ({gpu.vram_total_gb:.1f}GB VRAM)")
            else:
                reasons.append(f"⚠️  Limited GPU offload ({gpu.vram_total_gb:.1f}GB VRAM)")
        else:
            reasons.append("⚠️  CPU-only mode (no GPU detected)")
        
        # Check disk space
        if disk.free_gb < model["size_gb"] * 1.5:
            reasons.append(f"⚠️  Low disk space: need {model['size_gb']}GB, have {disk.free_gb:.1f}GB free")
        else:
            reasons.append(f"✅ Disk space sufficient ({disk.free_gb:.1f}GB free)")
        
        return fits, reasons
    
    def _calculate_score(
        self,
        model: Dict[str, Any],
        use_case: str,
        priority: str,
    ) -> float:
        """Calculate recommendation score (0-100)."""
        score = 50.0  # Base score
        
        gpu = self.hardware.gpu
        mem = self.hardware.memory
        
        # Use case match (0-20 points)
        if use_case in model["use_cases"]:
            score += 20
        elif use_case == "general":
            score += 10
        
        # Priority scoring
        if priority == "speed":
            # Speed priority: favor smaller models
            speed_score = model["speed"] * 4  # 0-20 points
            score += speed_score
            
            # Penalty for large models
            if model["size_gb"] > 20:
                score -= 10
            elif model["size_gb"] > 10:
                score -= 5
        
        elif priority == "quality":
            # Quality priority: favor larger models
            quality_score = model["quality"] * 4  # 0-20 points
            score += quality_score
            
            # Bonus if hardware can handle it
            if gpu.has_gpu and gpu.vram_total_gb >= model["vram_gb"]:
                score += 10
        
        else:  # balanced
            # Balanced: average of speed and quality
            balance_score = (model["speed"] + model["quality"]) * 2  # 0-20 points
            score += balance_score
        
        # Hardware optimization bonus
        if gpu.has_gpu:
            # Bonus for full GPU offload
            if gpu.vram_total_gb >= model["vram_gb"]:
                score += 10
            elif gpu.vram_total_gb >= model["vram_gb"] * 0.7:
                score += 5
        
        # RAM headroom bonus
        ram_ratio = mem.available_gb / model["ram_gb"]
        if ram_ratio >= 2:
            score += 5  # Plenty of headroom
        elif ram_ratio >= 1.5:
            score += 3
        
        return min(100, max(0, score))
    
    def get_best_model(
        self,
        use_case: str = "general",
        priority: str = "balanced",
    ) -> Optional[Recommendation]:
        """Get the single best model recommendation."""
        recs = self.recommend(use_case, priority, limit=1)
        return recs[0] if recs else None
    
    def get_optimal_settings(self, model_key: str) -> Dict[str, Any]:
        """
        Get optimal inference settings for a model.
        
        Returns settings for config.yaml
        """
        model = next((m for m in self.MODELS if m["key"] == model_key), None)
        if not model:
            return {}
        
        gpu = self.hardware.gpu
        mem = self.hardware.memory
        
        settings = {
            "gpu_layers": 999,  # Default: full offload
            "context_size": 131072,
            "batch_size": 512,
            "ubatch_size": 256,
            "flash_attn": "auto",
            "threads": self.hardware.cpu.threads,
        }
        
        # Adjust based on VRAM
        if gpu.has_gpu:
            vram_ratio = gpu.vram_total_gb / model["vram_gb"]
            
            if vram_ratio >= 1.2:
                # Plenty of VRAM
                settings["gpu_layers"] = 999
                settings["batch_size"] = 1024
                settings["ubatch_size"] = 512
            elif vram_ratio >= 0.8:
                # Good fit
                settings["gpu_layers"] = 999
                settings["batch_size"] = 512
                settings["ubatch_size"] = 256
            elif vram_ratio >= 0.5:
                # Partial offload
                settings["gpu_layers"] = int(999 * vram_ratio)
                settings["batch_size"] = 256
                settings["ubatch_size"] = 128
            else:
                # Limited offload
                settings["gpu_layers"] = int(999 * vram_ratio * 0.8)
                settings["batch_size"] = 128
                settings["ubatch_size"] = 64
            
            # Flash attention
            if gpu.gpu_type == "cuda" and gpu.vram_total_gb >= 16:
                settings["flash_attn"] = "on"
        
        # Adjust context based on RAM
        available_for_context = max(0, mem.available_gb - model["ram_gb"] - 4)
        max_context = int(available_for_context * 16 * 1024)
        settings["context_size"] = min(262144, max(16384, max_context))
        
        # Thread optimization
        if gpu.has_gpu:
            settings["threads"] = max(4, self.hardware.cpu.cores // 2)
        
        return settings


# Convenience functions
def recommend_models(
    use_case: str = "general",
    priority: str = "balanced",
    limit: int = 3,
) -> List[Recommendation]:
    """Get model recommendations."""
    recommender = ModelRecommender()
    return recommender.recommend(use_case, priority, limit)


def get_best_model(
    use_case: str = "general",
    priority: str = "balanced",
) -> Optional[Recommendation]:
    """Get best model recommendation."""
    recommender = ModelRecommender()
    return recommender.get_best_model(use_case, priority)


def get_optimal_settings(model_key: str) -> Dict[str, Any]:
    """Get optimal settings for a model."""
    recommender = ModelRecommender()
    return recommender.get_optimal_settings(model_key)
