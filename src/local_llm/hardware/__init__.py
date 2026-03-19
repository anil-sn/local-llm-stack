"""
Hardware detection and optimization module.

Automatically detects GPU, CPU, RAM and provides optimal configuration.
"""

from local_llm.hardware.detector import HardwareDetector, HardwareInfo
from local_llm.hardware.recommender import ModelRecommender, Recommendation

__all__ = [
    "HardwareDetector",
    "HardwareInfo",
    "ModelRecommender",
    "Recommendation",
]
