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

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text from a prompt.

        Args:
            prompt: The input prompt
            **kwargs: Parameter overrides (temperature, max_tokens, etc.)

        Returns:
            Generated text
        """
        return self.engine.generate(prompt, **kwargs)

    def chat(self, message: str, context: Optional[List[str]] = None, **kwargs) -> str:
        """
        Chat-style interaction with optional context.

        Args:
            message: The user's message
            context: List of previous messages for context
            **kwargs: Parameter overrides

        Returns:
            Model's response
        """
        # Build prompt with context
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
        self,
        prompt: str,
        presets: Optional[List[str]] = None,
        parameters: Optional[Dict[str, List[Any]]] = None,
    ) -> Dict[str, str]:
        """
        Run the same prompt with different settings for comparison.

        Args:
            prompt: The prompt to test
            presets: List of presets to try (default: all available)
            parameters: Dict of parameter names to lists of values to try

        Returns:
            Dict mapping setting descriptions to responses
        """
        results = {}
        original_preset = self.current_preset()

        try:
            # Test different presets
            if presets is None:
                presets = ["default", "creative", "precise"]

            for preset in presets:
                try:
                    self.set_preset(preset)
                    response = self.generate(prompt, max_tokens=100)
                    results[f"preset_{preset}"] = response
                except Exception as e:
                    results[f"preset_{preset}"] = f"Error: {str(e)}"

            # Test different parameters
            if parameters:
                self.set_preset("default")  # Reset to default for parameter testing
                for param_name, values in parameters.items():
                    for value in values:
                        try:
                            kwargs = {param_name: value}
                            response = self.generate(prompt, max_tokens=100, **kwargs)
                            results[f"{param_name}_{value}"] = response
                        except Exception as e:
                            results[f"{param_name}_{value}"] = f"Error: {str(e)}"

        finally:
            # Restore original preset
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
