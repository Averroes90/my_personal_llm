import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List


class ParameterManager:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.params_config = self._load_config("parameters.yaml")
        self.current_preset = "default"
        self.custom_params = {}

    def _load_config(self, filename: str) -> Dict:
        """Load configuration from YAML file"""
        config_path = self.config_dir / filename
        with open(config_path) as f:
            return yaml.safe_load(f)

    def set_preset(self, preset_name: str):
        """Set parameter preset"""
        if preset_name not in self.params_config["presets"]:
            available = list(self.params_config["presets"].keys())
            raise ValueError(
                f"Preset '{preset_name}' not found. Available: {available}"
            )

        self.current_preset = preset_name
        self.custom_params = {}  # Clear custom overrides
        print(f"✓ Parameter preset set to: {preset_name}")

    def set_parameter(self, param_name: str, value: Any):
        """Set individual parameter with validation"""
        if not self._validate_parameter(param_name, value):
            limits = self.params_config.get("parameter_limits", {}).get(param_name)
            raise ValueError(
                f"Parameter '{param_name}' value {value} outside limits: {limits}"
            )

        self.custom_params[param_name] = value
        print(f"✓ Set {param_name} = {value}")

    def set_parameters(self, **kwargs):
        """Set multiple parameters at once"""
        for param_name, value in kwargs.items():
            self.set_parameter(param_name, value)

    def get_parameters(self) -> Dict[str, Any]:
        """Get current parameters (preset + custom overrides)"""
        preset_params = self.params_config["presets"][self.current_preset].copy()
        preset_params.update(self.custom_params)
        return preset_params

    def _validate_parameter(self, param_name: str, value: Any) -> bool:
        """Validate parameter value against limits"""
        limits = self.params_config.get("parameter_limits", {}).get(param_name)
        if not limits:
            return True  # No limits defined

        min_val, max_val = limits
        return min_val <= value <= max_val

    def get_presets(self) -> List[str]:
        """Get list of available presets"""
        return list(self.params_config["presets"].keys())

    def describe_preset(self, preset_name: str) -> Dict[str, Any]:
        """Get parameters for a specific preset"""
        if preset_name not in self.params_config["presets"]:
            raise ValueError(f"Preset '{preset_name}' not found")
        return self.params_config["presets"][preset_name]

    def reset_to_preset(self):
        """Clear custom parameters and return to current preset"""
        self.custom_params = {}
        print(f"✓ Reset to preset: {self.current_preset}")

    def get_parameter_info(self) -> Dict[str, Any]:
        """Get information about all parameters and their limits"""
        return {
            "current_preset": self.current_preset,
            "current_parameters": self.get_parameters(),
            "custom_overrides": self.custom_params,
            "available_presets": self.get_presets(),
            "parameter_limits": self.params_config.get("parameter_limits", {}),
        }
