from pathlib import Path
from typing import Dict, Any, Optional, List
from utils.prompt_templates import PromptTemplates, format_prompt
from utils.benchmarking import LLMBenchmark, quick_benchmark
import sys

# Add the parent directory to the path so we can import core modules
sys.path.append(str(Path(__file__).parent.parent))

from core.inference_engine import InferenceEngine


class LocalLLM:
    """
    Main API interface for local LLM operations.
    Simple, clean interface for other projects to use.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        preset: str = "default",
        config_dir: str = "config",
        allow_slow_models: bool = True,
    ):
        """
        Initialize the LocalLLM interface.

        Args:
            model: Model name to use (auto-selects if None)
            preset: Parameter preset to start with
            config_dir: Directory containing configuration files
        """
        # Handle relative config path
        if not Path(config_dir).is_absolute():
            # Assume config is relative to this file's parent directory
            config_dir = str(Path(__file__).parent.parent / config_dir)

        self.engine = InferenceEngine(config_dir)

        # Set up model
        if model:
            self.engine.set_model(model)
        else:
            auto_selected = self.engine.auto_select_model()
            if not auto_selected:
                raise RuntimeError("No models available. Check your configuration.")

        # Set up parameters
        self.engine.set_preset(preset)
        self.templates = PromptTemplates()
        self.benchmark = LLMBenchmark(self)
        self.allow_slow_models = allow_slow_models

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text from a prompt.

        Args:
            prompt: The input prompt
            **kwargs: Parameter overrides (temperature, max_tokens, etc.)

        Returns:
            Generated text
        """
        # current_model = self.engine.model_manager.get_current_model()
        model_info = self.engine.model_manager.get_model_info()

        if model_info.get("size_gb", 0) > 50:
            profile_name = getattr(self.engine, "current_memory_profile", "unknown")
            if profile_name in ["mmap_aggressive", "ultra_conservative"]:
                print(f"⚠️  Large model detected - this may take several minutes")
                print(f"   Strategy: {profile_name}")

                if not self.allow_slow_models:
                    raise RuntimeError(
                        "Large model generation disabled. Set allow_slow_models=True"
                    )
        return self.engine.generate(prompt, **kwargs)

    def estimate_generation_time(
        self, prompt: str, max_tokens: int = 300
    ) -> Dict[str, Any]:
        """Estimate how long generation will take"""
        model_info = self.engine.model_manager.get_model_info()
        model_size_gb = model_info.get("size_gb", 0)

        if hasattr(self.engine, "memory_manager"):
            _, profile = self.engine.memory_manager.select_optimal_profile(
                model_size_gb
            )
            performance = self.engine.memory_manager.estimate_performance(
                model_size_gb, profile
            )

            tokens_per_second = performance["estimated_tokens_per_second"]
            estimated_seconds = max_tokens / tokens_per_second

            return {
                "estimated_duration_seconds": estimated_seconds,
                "estimated_duration_minutes": estimated_seconds / 60,
                "tokens_per_second": tokens_per_second,
                "memory_strategy": self.engine.current_memory_profile or "unknown",
            }

        return {"estimated_duration_seconds": "unknown"}

    def generate_with_progress(self, prompt: str, **kwargs):
        """Generate with progress estimation"""
        estimate = self.estimate_generation_time(prompt, kwargs.get("max_tokens", 300))

        if estimate["estimated_duration_seconds"] != "unknown":
            if estimate["estimated_duration_minutes"] > 2:
                print(
                    f"⏳ Estimated generation time: {estimate['estimated_duration_minutes']:.1f} minutes"
                )
                print(f"   Strategy: {estimate['memory_strategy']}")

        return self.generate(prompt, **kwargs)

    def chat(self, message: str, context: Optional[List[str]] = None, **kwargs) -> str:
        """Chat with memory-aware warnings"""
        # Build prompt with context (existing logic)
        if context:
            prompt_parts = []
            for i, ctx_msg in enumerate(context):
                if i % 2 == 0:
                    prompt_parts.append(f"Human: {ctx_msg}")
                else:
                    prompt_parts.append(f"Assistant: {ctx_msg}")
            prompt_parts.append(f"Human: {message}")
            prompt_parts.append("Assistant:")
            prompt = "\n".join(prompt_parts)
        else:
            prompt = f"Human: {message}\nAssistant:"

        # Use generate_with_progress for large models
        model_info = self.engine.model_manager.get_model_info()
        if model_info.get("size_gb", 0) > 50:
            return self.generate_with_progress(prompt, **kwargs)
        else:
            return self.generate(prompt, **kwargs)

    def set_model(self, model_name: str):
        """Switch to a different model"""
        self.engine.set_model(model_name)
        return self

    def set_preset(self, preset_name: str):
        """Switch to a different parameter preset"""
        self.engine.set_preset(preset_name)
        return self

    def set_parameters(self, **kwargs):
        """Set custom parameters"""
        self.engine.set_parameters(**kwargs)
        return self

    def creative(self):
        """Quick switch to creative preset"""
        return self.set_preset("creative")

    def precise(self):
        """Quick switch to precise preset"""
        return self.set_preset("precise")

    def default(self):
        """Quick switch to default preset"""
        return self.set_preset("default")

    # Information methods
    def available_models(self) -> List[str]:
        """Get list of available models"""
        return self.engine.get_available_models()

    def current_model(self) -> Optional[str]:
        """Get current model name"""
        return self.engine.model_manager.get_current_model()

    def current_preset(self) -> str:
        """Get current parameter preset"""
        return self.engine.param_manager.current_preset

    def current_parameters(self) -> Dict[str, Any]:
        """Get current parameters"""
        return self.engine.param_manager.get_parameters()

    def model_info(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed model information"""
        return self.engine.get_model_info(model_name)

    def status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return self.engine.get_system_status()

    # Convenience methods for experimentation
    def experiment(
        self, prompt: str, presets: Optional[List[str]] = None, **kwargs
    ) -> Dict[str, str]:
        """Experiment with memory awareness"""
        if presets is None:
            presets = ["default", "creative", "precise"]

        results = {}
        original_preset = self.current_preset()

        # Warn about large model experiments
        model_info = self.engine.model_manager.get_model_info()
        if model_info.get("size_gb", 0) > 50:
            print(f"⚠️  Large model experiment - each preset may take several minutes")
            total_estimate = self.estimate_generation_time(
                prompt, kwargs.get("max_tokens", 100)
            )
            if total_estimate["estimated_duration_seconds"] != "unknown":
                total_time = total_estimate["estimated_duration_minutes"] * len(presets)
                print(
                    f"   Total estimated time: {total_time:.1f} minutes for {len(presets)} presets"
                )

        try:
            for preset in presets:
                try:
                    self.set_preset(preset)
                    # Use regular generate (not generate_with_progress to avoid spam)
                    response = self.generate(prompt, max_tokens=100, **kwargs)
                    results[f"preset_{preset}"] = response
                except Exception as e:
                    results[f"preset_{preset}"] = f"Error: {str(e)}"
        finally:
            self.set_preset(original_preset)

        return results

    # Template methods
    def use_template(self, template_name: str, **kwargs) -> str:
        """Generate using a prompt template"""
        prompt = self.templates.format_prompt(template_name, **kwargs)
        template_params = self.templates.get_template_params(template_name)

        # Merge template params with any provided kwargs
        generation_params = {**template_params}
        # Remove template variables from generation params
        template_vars = set(
            self.templates.get_template(template_name).template.split("{")
        )
        template_vars = {var.split("}")[0] for var in template_vars if "}" in var}
        generation_params = {
            k: v for k, v in generation_params.items() if k not in template_vars
        }

        return self.generate(prompt, **generation_params)

    def list_templates(self) -> List[str]:
        """Get available prompt templates"""
        return self.templates.list_templates()

    def describe_template(self, template_name: str) -> str:
        """Get template description"""
        return self.templates.describe_template(template_name)

    # Benchmarking methods
    def benchmark_presets(self, prompt: str, presets: List[str] = None):
        """Benchmark different presets"""
        return self.benchmark.benchmark_presets(prompt, presets)

    def stress_test(self, prompt: str, iterations: int = 5, **kwargs):
        """Run stress test"""
        return self.benchmark.stress_test(prompt, iterations, **kwargs)

    def quick_benchmark(self, prompt: str = "Tell me a short story about robots."):
        """Run a quick benchmark"""
        return quick_benchmark(self, prompt)

    def benchmark_report(self) -> str:
        """Get benchmark report"""
        return self.benchmark.generate_report()
