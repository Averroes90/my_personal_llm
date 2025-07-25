# utils/fortress_protection.py
from pre_flight_checker import PreFlightChecker
from system_limits import SystemLimits
from system_circuit_breaker import SystemCircuitBreaker
from memory_guardian import EnhancedMemoryGuardian
from typing import Callable
import os


class FortressProtection:
    """Multi-layer defense system for hardware protection"""

    def __init__(self, max_memory_gb: float = 20.0):
        self.max_memory_gb = max_memory_gb
        self.pre_flight = PreFlightChecker()
        self.system_limits = SystemLimits()
        self.circuit_breaker = SystemCircuitBreaker()
        self.memory_guardian = EnhancedMemoryGuardian(max_memory_gb=max_memory_gb)

    def fortified_execution(
        self, target_function: Callable, model_size_gb: float = 0, *args, **kwargs
    ):
        """Execute function with all protection layers"""

        print("🏰 Activating Fortress Protection...")

        # LAYER 1: Pre-flight Safety Check
        if model_size_gb > 0:
            safe, message, details = self.pre_flight.can_run_safely(model_size_gb)
            print(f"Layer 1 - Pre-flight: {message}")

            if not safe:
                raise RuntimeError(f"Pre-flight check failed: {message}")

        try:
            # LAYER 2: System-Level Limits
            print("Layer 2 - Setting system limits...")
            self.system_limits.set_memory_limit(self.max_memory_gb)
            self.system_limits.set_process_limits(50)
            self.system_limits.set_cpu_limit(7200)  # 2 hours max

            # LAYER 3: System Circuit Breaker
            print("Layer 3 - Activating circuit breaker...")
            self.circuit_breaker.register_process(os.getpid())
            self.circuit_breaker.start_system_monitoring()

            # LAYER 4: Memory Guardian
            print("Layer 4 - Memory guardian protection...")
            result = self.memory_guardian.protect_process(
                target_function, *args, **kwargs
            )

            print("🎉 Function completed successfully with full protection")
            return result

        except Exception as e:
            print(f"🚨 Protected function failed: {e}")
            raise
        finally:
            # Cleanup all layers
            print("🧹 Cleaning up protection layers...")
            self.circuit_breaker.stop_system_monitoring()
            self.system_limits.restore_limits()
            print("🏰 Fortress Protection deactivated")
