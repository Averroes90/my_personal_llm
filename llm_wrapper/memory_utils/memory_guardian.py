import psutil
import signal
import os
import threading
import time
import logging
from typing import Optional, Callable
from contextlib import contextmanager
from system_circuit_breaker import SystemCircuitBreaker
from system_limits import SystemLimits


class MemoryGuardian:
    def __init__(
        self,
        max_memory_gb: float = 20.0,
        check_interval: float = 0.5,
        grace_period: float = 3.0,
        logger: Optional[logging.Logger] = None,
    ):
        self.max_memory_bytes = max_memory_gb * 1024**3
        self.check_interval = check_interval
        self.grace_period = grace_period
        self.logger = logger or self._setup_logger()
        self.monitoring = False
        self.monitor_thread = None
        self.emergency_triggered = False
        self._shutdown_event = threading.Event()

    def _setup_logger(self):
        """Setup basic logging"""
        logger = logging.getLogger("MemoryGuardian")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    @contextmanager
    def protect(self):
        """Context manager for memory protection"""
        self.logger.info(
            f"🛡️  Memory protection active: {self.max_memory_bytes / 1024**3:.1f}GB limit"
        )
        self.start_monitoring()
        try:
            yield self
        except Exception as e:
            self.logger.error(f"Protected function failed: {e}")
            raise
        finally:
            self.stop_monitoring()

    def protect_process(self, target_function: Callable, *args, **kwargs):
        """Run a function with memory protection"""
        self.logger.info(
            f"🛡️  Memory protection active: {self.max_memory_bytes / 1024**3:.1f}GB limit"
        )
        # Start monitoring
        self.start_monitoring()

        try:
            # Enhanced: Add timeout protection
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError("Function execution timed out")

            # Set timeout (optional)
            # signal.signal(signal.SIGALRM, timeout_handler)
            # signal.alarm(3600)  # 1 hour timeout
            # Run the protected function
            result = target_function(*args, **kwargs)
            return result
        except Exception as e:
            self.logger.error(f"Protected function failed: {e}")
            raise
        finally:
            # signal.alarm(0)  # Cancel timeout
            # Always stop monitoring
            self.stop_monitoring()

    # METHOD 3: Decorator (Convenient)
    def protected(self, func: Callable):
        """Decorator for automatic memory protection"""

        def wrapper(*args, **kwargs):
            return self.protect_process(func, *args, **kwargs)

        return wrapper

    def start_monitoring(self):
        """Start memory monitoring in background thread - ENHANCED"""
        if self.monitoring:
            self.logger.warning("Monitoring already active")
            return

        self.monitoring = True
        self.emergency_triggered = False
        self._shutdown_event.clear()

        self.monitor_thread = threading.Thread(
            target=self._monitor_memory, daemon=True, name="MemoryGuardian"
        )
        self.monitor_thread.start()
        self.logger.info("Memory monitoring started")

    def stop_monitoring(self):
        """Stop memory monitoring - ENHANCED"""
        if not self.monitoring:
            return

        self.monitoring = False
        self._shutdown_event.set()

        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
            if self.monitor_thread.is_alive():
                self.logger.warning("Monitor thread didn't stop cleanly")

        self.logger.info("Memory monitoring stopped")

    def _monitor_memory(self):
        """Monitor memory usage and kill if exceeded - ENHANCED"""
        current_process = psutil.Process()
        warning_issued = False
        consecutive_violations = 0

        while self.monitoring and not self._shutdown_event.is_set():
            try:
                total_memory = self._get_total_memory_usage(current_process)
                memory_gb = total_memory / 1024**3

                # Warning at 80% of limit
                if not warning_issued and total_memory > (self.max_memory_bytes * 0.8):
                    self.logger.warning(
                        f"Memory warning: {memory_gb:.1f}GB used (80% of {self.max_memory_bytes/1024**3:.1f}GB limit)"
                    )
                    warning_issued = True

                # Kill at 100% of limit
                if total_memory > self.max_memory_bytes:
                    consecutive_violations += 1

                    if consecutive_violations >= 2:  # Confirm it's not a spike
                        self.logger.critical(
                            f"MEMORY LIMIT EXCEEDED: {memory_gb:.1f}GB > {self.max_memory_bytes/1024**3:.1f}GB"
                        )
                        self.logger.critical(
                            "Terminating process to prevent system crash..."
                        )
                        self._emergency_shutdown(current_process)
                        break
                else:
                    consecutive_violations = 0

            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                self.logger.error(f"Process monitoring error: {e}")
                break
            except Exception as e:
                self.logger.error(f"Unexpected monitoring error: {e}")

            time.sleep(self.check_interval)

    def _get_total_memory_usage(self, process):
        """Get total memory usage including children - ENHANCED"""
        try:
            total_memory = process.memory_info().rss

            # Handle children processes
            try:
                children = process.children(recursive=True)
                for child in children:
                    try:
                        if (
                            child.is_running()
                            and child.status() != psutil.STATUS_ZOMBIE
                        ):
                            total_memory += child.memory_info().rss
                    except (
                        psutil.NoSuchProcess,
                        psutil.AccessDenied,
                        psutil.ZombieProcess,
                    ):
                        continue
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

            return total_memory

        except Exception as e:
            self.logger.error(f"Memory calculation error: {e}")
            return 0

    def _emergency_shutdown(self, process):
        """Emergency shutdown of process and children - ENHANCED"""
        if self.emergency_triggered:
            return  # Prevent recursive calls

        self.emergency_triggered = True
        killed_processes = []

        try:
            # Step 1: Graceful termination (SIGTERM)
            self.logger.info("Step 1: Attempting graceful shutdown...")
            try:
                for child in process.children(recursive=True):
                    try:
                        child.terminate()  # SIGTERM
                        killed_processes.append(child.pid)
                        self.logger.info(f"Terminated child process: {child.pid}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                process.terminate()  # Terminate main process

            except Exception as e:
                self.logger.error(f"Graceful shutdown failed: {e}")

            # Step 2: Wait for graceful shutdown
            time.sleep(self.grace_period)

            # Step 3: Force kill (SIGKILL)
            self.logger.info("Step 2: Force killing remaining processes...")
            try:
                for child in process.children(recursive=True):
                    try:
                        if child.is_running():
                            child.kill()  # SIGKILL
                            self.logger.info(f"Force killed child process: {child.pid}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                if process.is_running():
                    process.kill()  # Kill main process

            except Exception as e:
                self.logger.error(f"Force kill failed: {e}")

            # Step 4: Nuclear option
            self.logger.critical("Step 3: Nuclear shutdown...")
            os._exit(1)  # Immediate process termination

        except Exception as e:
            self.logger.critical(f"Emergency shutdown completely failed: {e}")
            os._exit(1)


# Your existing Memory Guardian with additional features
class EnhancedMemoryGuardian(MemoryGuardian):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.system_circuit_breaker = SystemCircuitBreaker()
        self.system_limits = SystemLimits()

    def protect_process(self, target_function: Callable, *args, **kwargs):
        """Multi-layer protection"""
        # Layer 1: Pre-flight check
        # Layer 2: Set system limits
        # Layer 3: Start circuit breaker
        # Layer 4: Run with memory guardian

        try:
            # Apply system limits
            self.system_limits.set_memory_limit(self.max_memory_bytes / 1024**3)

            # Register with circuit breaker
            self.system_circuit_breaker.register_process(os.getpid())
            self.system_circuit_breaker.start_system_monitoring()

            # Run original protection
            return super().protect_process(target_function, *args, **kwargs)

        finally:
            # Cleanup
            self.system_circuit_breaker.stop_system_monitoring()
            self.system_limits.restore_limits()
