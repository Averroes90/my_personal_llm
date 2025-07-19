import yaml
from pathlib import Path


def test_config_loading():
    # Test models config
    models_path = Path("config/models.yaml")
    with open(models_path) as f:
        models = yaml.safe_load(f)

    print("✓ Models config loaded successfully")
    print(f"  Found model: {list(models['models'].keys())[0]}")

    # Test parameters config
    params_path = Path("config/parameters.yaml")
    with open(params_path) as f:
        params = yaml.safe_load(f)

    print("✓ Parameters config loaded successfully")
    print(f"  Found presets: {list(params['presets'].keys())}")


if __name__ == "__main__":
    test_config_loading()
