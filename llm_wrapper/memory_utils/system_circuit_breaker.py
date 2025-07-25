# utils/system_circuit_breaker.py
import psutil
import threading
import time
import os
import signal
from typing import Callable, Optional
import subprocess


class SystemCircuitBreaker:
    """External process monitor - catches what Memory Guardian misses"""

    def __init__(
        self,
        memory_threshold_percent: float = 85.0,
        swap_threshold_percent: float = 50.0,
        check_interval: float = 0.5,
    ):
        self.memory_threshold = memory_threshold_percent / 100
        self.swap_threshold = swap_threshold_percent / 100
        self.check_interval = check_interval
        self.monitoring = False
        self.monitor_thread = None
        self.protected_pids = set()

    def register_process(self, pid: int):
        """Register a process for protection"""
        self.protected_pids.add(pid)

    def start_system_monitoring(self):
        """Start system-wide monitoring"""
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_system, daemon=True)
        self.monitor_thread.start()
        print(
            f"🔍 System circuit breaker active (Memory: {self.memory_threshold*100}%, Swap: {self.swap_threshold*100}%)"
        )

    def stop_system_monitoring(self):
        """Stop system monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)

    def _monitor_system(self):
        """Monitor system-wide resource usage"""
        consecutive_violations = 0

        while self.monitoring:
            try:
                memory = psutil.virtual_memory()
                swap = psutil.swap_memory()

                memory_usage = 1 - (memory.available / memory.total)
                swap_usage = swap.used / max(swap.total, 1)  # Avoid division by zero

                # Check for dangerous conditions
                dangerous = (
                    memory_usage > self.memory_threshold
                    or swap_usage > self.swap_threshold
                )

                if dangerous:
                    consecutive_violations += 1
                    print(
                        f"⚠️  System under pressure: RAM {memory_usage*100:.1f}%, Swap {swap_usage*100:.1f}%"
                    )

                    if consecutive_violations >= 3:  # 1.5 seconds of violations
                        print("🚨 SYSTEM CIRCUIT BREAKER TRIGGERED")
                        self._emergency_system_protection()
                        break
                else:
                    consecutive_violations = 0

            except Exception as e:
                print(f"Circuit breaker error: {e}")

            time.sleep(self.check_interval)

    def _emergency_system_protection(self):
        """Emergency system protection"""
        print("🛡️  Activating emergency system protection...")

        # Step 1: Kill registered processes first
        for pid in self.protected_pids.copy():
            try:
                os.kill(pid, signal.SIGTERM)
                print(f"Terminated registered process: {pid}")
            except (OSError, ProcessLookupError):
                self.protected_pids.discard(pid)

        time.sleep(2)

        # Step 2: Kill high-memory processes
        try:
            processes = [
                (p.info["pid"], p.info["memory_percent"], p.info["name"])
                for p in psutil.process_iter(["pid", "memory_percent", "name"])
            ]

            # Sort by memory usage, kill top consumers
            high_memory_procs = sorted(processes, key=lambda x: x[1], reverse=True)[:5]

            for pid, memory_pct, name in high_memory_procs:
                if memory_pct > 5.0:  # Using more than 5% of system memory
                    try:
                        os.kill(pid, signal.SIGKILL)
                        print(
                            f"Emergency killed: {name} (PID: {pid}, {memory_pct:.1f}% memory)"
                        )
                    except (OSError, ProcessLookupError):
                        pass

        except Exception as e:
            print(f"Emergency process cleanup failed: {e}")

        # Step 3: Clear swap if possible (macOS)
        try:
            subprocess.run(["sudo", "purge"], check=False, timeout=10)
        except:
            pass
