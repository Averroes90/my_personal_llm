# utils/system_limits.py
import resource
import os
import subprocess
from typing import Optional


class SystemLimits:
    def __init__(self):
        self.original_limits = {}

    def set_memory_limit(self, max_memory_gb: float):
        """Set hard memory limit via ulimit"""
        max_bytes = int(max_memory_gb * 1024**3)

        # Store original limit
        original = resource.getrlimit(resource.RLIMIT_AS)
        self.original_limits["memory"] = original

        # Set new limit (address space)
        resource.setrlimit(resource.RLIMIT_AS, (max_bytes, max_bytes))
        print(f"🔒 Hard memory limit set: {max_memory_gb:.1f}GB")

    def set_process_limits(self, max_processes: int = 100):
        """Limit number of processes"""
        original = resource.getrlimit(resource.RLIMIT_NPROC)
        self.original_limits["processes"] = original

        resource.setrlimit(resource.RLIMIT_NPROC, (max_processes, max_processes))
        print(f"🔒 Process limit set: {max_processes}")

    def set_cpu_limit(self, max_cpu_seconds: int = 3600):
        """Limit CPU time (prevents infinite loops)"""
        original = resource.getrlimit(resource.RLIMIT_CPU)
        self.original_limits["cpu"] = original

        resource.setrlimit(resource.RLIMIT_CPU, (max_cpu_seconds, max_cpu_seconds))
        print(f"🔒 CPU time limit set: {max_cpu_seconds}s")

    def restore_limits(self):
        """Restore original system limits"""
        for limit_type, (soft, hard) in self.original_limits.items():
            if limit_type == "memory":
                resource.setrlimit(resource.RLIMIT_AS, (soft, hard))
            elif limit_type == "processes":
                resource.setrlimit(resource.RLIMIT_NPROC, (soft, hard))
            elif limit_type == "cpu":
                resource.setrlimit(resource.RLIMIT_CPU, (soft, hard))
        print("🔓 System limits restored")

    def create_limited_subprocess(self, command: list, max_memory_gb: float):
        """Create subprocess with built-in limits"""

        def limit_resources():
            # Set limits in child process
            max_bytes = int(max_memory_gb * 1024**3)
            resource.setrlimit(resource.RLIMIT_AS, (max_bytes, max_bytes))
            resource.setrlimit(resource.RLIMIT_CPU, (3600, 3600))  # 1 hour max

        return subprocess.Popen(
            command,
            preexec_fn=limit_resources,  # Apply limits before exec
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
