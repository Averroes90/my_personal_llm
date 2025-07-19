from core.inference_engine import InferenceEngine


def test_parameter_management():
    print("🧪 Testing Parameter Management System\n")

    # Initialize engine
    engine = InferenceEngine()
    engine.set_model("mistral-7b-base")

    # Test preset switching
    print("=== Testing Presets ===")

    # Test default preset
    print("📋 Using 'default' preset:")
    engine.set_preset("default")
    response1 = engine.generate("Write a short story about robots.", max_tokens=80)
    print(f"🤖 Response: {response1[:100]}...\n")

    # Test creative preset
    print("📋 Using 'creative' preset:")
    engine.set_preset("creative")
    response2 = engine.generate("Write a short story about robots.", max_tokens=80)
    print(f"🤖 Response: {response2[:100]}...\n")

    # Test precise preset
    print("📋 Using 'precise' preset:")
    engine.set_preset("precise")
    response3 = engine.generate("What is artificial intelligence?", max_tokens=60)
    print(f"🤖 Response: {response3[:100]}...\n")

    # Test custom parameter overrides
    print("=== Testing Custom Parameters ===")
    engine.set_preset("default")
    engine.set_parameters(temperature=1.5, max_tokens=100)
    response4 = engine.generate("Invent a new type of animal:", max_tokens=80)
    print(f"🤖 High temp response: {response4[:100]}...\n")

    # Test parameter info
    print("=== Parameter Information ===")
    info = engine.get_parameter_info()
    print(f"Current preset: {info['current_preset']}")
    print(f"Current parameters: {info['current_parameters']}")
    print(f"Custom overrides: {info['custom_overrides']}")


if __name__ == "__main__":
    test_parameter_management()
