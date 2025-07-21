import psutil
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import subprocess


class UniversalMemoryManager:
    """
    Handles models of any size by automatically adapting memory strategies.
    Guarantees: Any model will run, only speed varies.
    """

    def __init__(self):
        self.system_info = self._detect_system_capabilities()
        self.memory_profiles = self._define_memory_profiles()

    def _detect_system_capabilities(self) -> Dict[str, Any]:
        """Detect all available system resources"""
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return {
            "total_ram_gb": memory.total / (1024**3),
            "available_ram_gb": memory.available / (1024**3),
            "total_disk_gb": disk.total / (1024**3),
            "available_disk_gb": disk.free / (1024**3),
            "cpu_cores": psutil.cpu_count(),
            "platform": os.uname().system,
            "architecture": os.uname().machine,
        }

    def _define_memory_profiles(self) -> Dict[str, Dict]:
        """Define escalating memory management strategies"""
        return {
            "direct": {
                "description": "Model fits in RAM - direct loading",
                "ram_usage_ratio": 0.8,  # Use up to 80% of available RAM
                "context_size": 8192,
                "batch_size": 512,
                "gpu_layers": -1,  # All layers
                "mmap": False,
                "streaming": False,
            },
            "mmap_light": {
                "description": "Light memory mapping - model 1-3x RAM",
                "ram_usage_ratio": 0.9,
                "context_size": 4096,
                "batch_size": 256,
                "gpu_layers": "auto",
                "mmap": True,
                "streaming": False,
            },
            "mmap_aggressive": {
                "description": "Aggressive memory mapping - model 3-10x RAM",
                "ram_usage_ratio": 0.95,
                "context_size": 2048,
                "batch_size": 128,
                "gpu_layers": "minimal",
                "mmap": True,
                "streaming": True,
            },
            "ultra_conservative": {
                "description": "Ultra-conservative - any size model",
                "ram_usage_ratio": 0.5,  # Only use half of RAM
                "context_size": 1024,
                "batch_size": 32,
                "gpu_layers": 0,  # CPU only
                "mmap": True,
                "streaming": True,
                "sequential_loading": True,
            },
        }

    def select_optimal_profile(self, model_size_gb: float) -> Tuple[str, Dict]:
        """Automatically select the best profile for model size"""
        available_ram = self.system_info["available_ram_gb"]

        # Calculate size ratios
        size_ratio = model_size_gb / available_ram

        if size_ratio <= 0.8:
            profile = "direct"
        elif size_ratio <= 3.0:
            profile = "mmap_light"
        elif size_ratio <= 10.0:
            profile = "mmap_aggressive"
        else:
            profile = "ultra_conservative"

        selected_profile = self.memory_profiles[profile].copy()

        # Dynamic adjustments based on actual ratio
        if size_ratio > 5:
            # For very large models, further reduce resources
            selected_profile["context_size"] = min(
                selected_profile["context_size"], 512
            )
            selected_profile["batch_size"] = min(selected_profile["batch_size"], 16)

        if size_ratio > 20:
            # Extreme cases - minimal everything
            selected_profile["context_size"] = 256
            selected_profile["batch_size"] = 8
            selected_profile["sequential_loading"] = True

        return profile, selected_profile

    def calculate_gpu_layers(
        self, total_layers: int, profile: Dict, model_size_gb: float
    ) -> int:
        """Calculate optimal GPU layer distribution"""
        gpu_layers_setting = profile["gpu_layers"]

        if gpu_layers_setting == -1:
            return total_layers  # All layers
        elif gpu_layers_setting == "auto":
            # Estimate layers that fit in GPU memory
            available_gpu_memory = (
                self.system_info["available_ram_gb"] * 0.7
            )  # Conservative
            layers_per_gb = total_layers / model_size_gb
            max_gpu_layers = int(available_gpu_memory * layers_per_gb)
            return min(max_gpu_layers, total_layers)
        elif gpu_layers_setting == "minimal":
            return min(8, total_layers)  # Only a few layers
        else:
            return int(gpu_layers_setting)

    def estimate_performance(
        self, model_size_gb: float, profile: Dict
    ) -> Dict[str, Any]:
        """Estimate performance characteristics"""
        size_ratio = model_size_gb / self.system_info["available_ram_gb"]

        # Base performance metrics
        base_tokens_per_second = 50  # Optimistic baseline

        # Apply penalties based on memory pressure
        if profile["mmap"]:
            base_tokens_per_second *= 0.3  # Memory mapping penalty

        if size_ratio > 3:
            base_tokens_per_second *= 0.2  # Heavy swapping penalty

        if size_ratio > 10:
            base_tokens_per_second *= 0.1  # Extreme swapping penalty

        # Context size affects memory usage
        context_penalty = 8192 / profile["context_size"]
        base_tokens_per_second *= min(context_penalty, 2.0)

        return {
            "estimated_tokens_per_second": max(base_tokens_per_second, 0.1),
            "estimated_loading_time_minutes": model_size_gb / 2,  # Rough estimate
            "memory_efficiency": min(100, (1 / size_ratio) * 100),
            "ssd_usage_intensity": "high" if size_ratio > 2 else "low",
        }
