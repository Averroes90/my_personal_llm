from core.inference_engine import InferenceEngine


def test_model_management():
    print("🧪 Testing Model Management System\n")

    # Initialize engine
    engine = InferenceEngine()

    # Test model discovery
    print("=== Model Discovery ===")
    available_models = engine.get_available_models()
    print(f"Available models: {available_models}")

    # Test auto-selection
    print("\n=== Auto Model Selection ===")
    selected = engine.auto_select_model()
    print(f"Auto-selected model: {selected}")

    # Test model info
    print("\n=== Model Information ===")
    model_info = engine.get_model_info()
    print(f"Current model: {model_info['path']}")
    print(f"Size: {model_info.get('size_gb', 'Unknown')} GB")
    print(f"Status: {model_info.get('status', 'Unknown')}")

    # Test system status
    print("\n=== System Status ===")
    status = engine.get_system_status()
    print(f"Total models: {status['model_stats']['total_models']}")
    print(f"Available models: {status['model_stats']['available_models']}")
    print(f"Current preset: {status['parameter_info']['current_preset']}")

    # Test generation with auto-selected model
    print("\n=== Generation Test ===")
    response = engine.generate("Hello, world! How are you today?", max_tokens=50)
    print(f"🤖 Response: {response}")


if __name__ == "__main__":
    test_model_management()
