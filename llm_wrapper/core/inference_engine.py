import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from .parameter_manager import ParameterManager
from .model_manager import ModelManager


class InferenceEngine:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.model_manager = ModelManager(config_dir)
        self.param_manager = ParameterManager(config_dir)

    def set_model(self, model_name: str):
        """Set the active model"""
        return self.model_manager.set_model(model_name)

    def get_available_models(self):
        """Get list of available models"""
        return self.model_manager.get_available_models()

    def get_model_info(self, model_name: Optional[str] = None):
        """Get model information"""
        return self.model_manager.get_model_info(model_name)

    def auto_select_model(self):
        """Auto-select first available model"""
        return self.model_manager.auto_select_model()

    def set_preset(self, preset_name: str):
        """Set parameter preset"""
        self.param_manager.set_preset(preset_name)

    def set_parameters(self, **kwargs):
        """Set individual parameters"""
        self.param_manager.set_parameters(**kwargs)

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using the current model"""
        current_model = self.model_manager.get_current_model()
        if not current_model:
            # Try to auto-select a model
            selected = self.auto_select_model()
            if not selected:
                raise ValueError("No models available. Check your configuration.")

        # Get model info
        model_info = self.model_manager.get_model_info()

        # Get parameters (managed parameters + any kwargs overrides)
        params = self.param_manager.get_parameters()
        params.update(kwargs)  # Allow temporary overrides

        # Build command with parameters
        command = self._build_command(model_info, prompt, params)

        # Execute and return result
        return self._execute_command(command)

    def _build_command(self, model_info: Dict, prompt: str, params: Dict) -> list:
        """Build the llama.cpp command"""
        # Use the full paths from model info
        executable = model_info["executable_full_path"]
        model_path = model_info["model_full_path"]

        # Start with base command
        command = [executable, "-m", model_path]

        # Add prompt
        command.extend(["-p", prompt])

        # Add parameters to command
        command.extend(["-n", str(params.get("max_tokens", 300))])
        command.extend(["-t", str(params.get("temperature", 0.8))])
        command.extend(["--top-p", str(params.get("top_p", 0.9))])
        command.extend(["--repeat-penalty", str(params.get("repeat_penalty", 1.15))])
        command.extend(["--repeat-last-n", str(params.get("repeat_last_n", 64))])

        return command

    def _execute_command(self, command: list) -> str:
        """Execute the llama.cpp command and return output"""
        try:
            print(f"🔄 Executing: {' '.join(command[:4])}... (truncated)")

            result = subprocess.run(
                command, capture_output=True, text=True, timeout=120  # 2 minute timeout
            )

            if result.returncode != 0:
                raise RuntimeError(f"Command failed: {result.stderr}")

            # Parse output
            output = result.stdout.strip()
            return self._parse_output(output)

        except subprocess.TimeoutExpired:
            raise RuntimeError("Generation timed out after 2 minutes")
        except Exception as e:
            raise RuntimeError(f"Execution failed: {str(e)}")

    def _parse_output(self, raw_output: str) -> str:
        """Extract just the generated text from llama.cpp output"""
        lines = raw_output.split("\n")

        generation_lines = []
        found_generation = False

        for line in lines:
            if not line.strip() or line.startswith("llama_"):
                continue

            if not found_generation and len(line.strip()) > 10:
                found_generation = True

            if found_generation:
                generation_lines.append(line)

        result = "\n".join(generation_lines).strip()
        return result if result else raw_output.strip()

    def get_parameter_info(self) -> Dict[str, Any]:
        """Get current parameter information"""
        return self.param_manager.get_parameter_info()

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "model_stats": self.model_manager.get_model_stats(),
            "parameter_info": self.param_manager.get_parameter_info(),
            "current_model_info": (
                self.model_manager.get_model_info()
                if self.model_manager.get_current_model()
                else None
            ),
        }
