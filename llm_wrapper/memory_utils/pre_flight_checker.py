# utils/pre_flight_checker.py
import psutil
import subprocess
from typing import Tuple, Dict, Any
from system_circuit_breaker import SystemCircuitBreaker
from system_limits import SystemLimits


class PreFlightChecker:
    def __init__(self):
        self.system_info = self._get_system_info()

    def _get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        # Check GPU memory if available
        gpu_memory = self._get_gpu_memory()

        return {
            "total_ram_gb": memory.total / 1024**3,
            "available_ram_gb": memory.available / 1024**3,
            "swap_total_gb": swap.total / 1024**3,
            "swap_used_gb": swap.used / 1024**3,
            "gpu_memory_gb": gpu_memory,
            "cpu_cores": psutil.cpu_count(),
        }

    def _get_gpu_memory(self) -> float:
        """Get GPU memory info (macOS Metal)"""
        try:
            # For macOS M-series chips, GPU memory is unified
            result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"],
                capture_output=True,
                text=True,
            )
            # Parse output for VRAM info - simplified
            return self.system_info.get("total_ram_gb", 0) * 0.7  # Rough estimate
        except:
            return 0

    def can_run_safely(
        self, model_size_gb: float, context_size: int = 4096, batch_size: int = 512
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """Comprehensive safety check"""

        # Calculate estimated memory needs
        base_memory = model_size_gb
        context_memory = (context_size * batch_size * 4) / 1024**3  # 4 bytes per token
        overhead_memory = 2.0  # OS and other processes
        total_needed = base_memory + context_memory + overhead_memory

        available = self.system_info["available_ram_gb"]

        # Safety levels
        if total_needed > available * 1.2:  # Would need >120% of available
            return (
                False,
                f"🚫 UNSAFE: Need {total_needed:.1f}GB, only {available:.1f}GB available",
                {},
            )

        if total_needed > available * 0.9:  # Would use >90% of available
            return (
                True,
                f"⚠️  RISKY: Will use {total_needed:.1f}GB of {available:.1f}GB",
                {"recommendation": "Use smaller context size or quantized model"},
            )

        return (
            True,
            f"✅ SAFE: Using {total_needed:.1f}GB of {available:.1f}GB",
            {"headroom_gb": available - total_needed},
        )
