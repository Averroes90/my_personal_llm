import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional


class ModelManager:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.models_config = self._load_config("models.yaml")
        self.current_model = None
        self._validate_models()

    def _load_config(self, filename: str) -> Dict:
        """Load configuration from YAML file"""
        config_path = self.config_dir / filename
        with open(config_path) as f:
            return yaml.safe_load(f)

    def _validate_models(self):
        """Validate that configured models and executables exist"""
        for model_name, model_info in self.models_config["models"].items():
            executable_path = Path(model_info["executable"]).expanduser()
            model_path = Path(model_info["path"]).expanduser()

            # Check if files exist
            if not executable_path.exists():
                print(
                    f"⚠️  Warning: Executable not found for {model_name}: {executable_path}"
                )
                model_info["status"] = "executable_missing"
            elif not model_path.exists():
                print(
                    f"⚠️  Warning: Model file not found for {model_name}: {model_path}"
                )
                model_info["status"] = "model_missing"
            else:
                model_info["status"] = "ready"

    def get_available_models(self) -> List[str]:
        """Get list of available model names"""
        return [
            name
            for name, info in self.models_config["models"].items()
            if info.get("status") == "ready"
        ]

    def get_all_models(self) -> List[str]:
        """Get list of all configured models (including unavailable ones)"""
        return list(self.models_config["models"].keys())

    def set_model(self, model_name: str) -> bool:
        """Set the active model"""
        if model_name not in self.models_config["models"]:
            available = self.get_available_models()
            raise ValueError(f"Model '{model_name}' not found. Available: {available}")

        model_info = self.models_config["models"][model_name]
        if model_info.get("status") != "ready":
            raise ValueError(
                f"Model '{model_name}' is not ready. Status: {model_info.get('status')}"
            )

        self.current_model = model_name
        print(f"✓ Model set to: {model_name}")
        return True

    def get_current_model(self) -> Optional[str]:
        """Get the currently active model name"""
        return self.current_model

    def get_model_info(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed information about a model"""
        if model_name is None:
            model_name = self.current_model

        if not model_name or model_name not in self.models_config["models"]:
            raise ValueError(f"Model '{model_name}' not found")

        model_info = self.models_config["models"][model_name].copy()

        # Add computed information
        executable_path = Path(model_info["executable"]).expanduser()
        model_path = Path(model_info["path"]).expanduser()

        model_info.update(
            {
                "executable_exists": executable_path.exists(),
                "model_exists": model_path.exists(),
                "executable_full_path": str(executable_path),
                "model_full_path": str(model_path),
            }
        )

        return model_info

    def get_model_stats(self) -> Dict[str, Any]:
        """Get statistics about all models"""
        all_models = self.get_all_models()
        available_models = self.get_available_models()

        return {
            "total_models": len(all_models),
            "available_models": len(available_models),
            "unavailable_models": len(all_models) - len(available_models),
            "current_model": self.current_model,
            "model_list": {"available": available_models, "all": all_models},
        }

    def auto_select_model(self) -> Optional[str]:
        """Automatically select the first available model"""
        available = self.get_available_models()
        if available:
            self.set_model(available[0])
            return available[0]
        return None

    def reload_config(self):
        """Reload model configuration from file"""
        self.models_config = self._load_config("models.yaml")
        self._validate_models()
        print("✓ Model configuration reloaded")

        # Check if current model is still valid
        if self.current_model and self.current_model not in self.get_available_models():
            print(f"⚠️  Current model '{self.current_model}' no longer available")
            self.current_model = None
