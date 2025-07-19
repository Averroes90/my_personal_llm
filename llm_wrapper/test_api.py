from api.local_llm import LocalLLM


def test_api_interface():
    print("🧪 Testing Main API Interface\n")

    # Test initialization
    print("=== Initialization ===")
    llm = LocalLLM()
    print(f"✓ Initialized successfully")
    print(f"✓ Current model: {llm.current_model()}")
    print(f"✓ Current preset: {llm.current_preset()}")

    # Test basic generation
    print("\n=== Basic Generation ===")
    response = llm.generate("Hello world", max_tokens=30)
    print(f"✓ Generated: {response[:50]}...")

    # Test method chaining
    print("\n=== Method Chaining ===")
    chained_response = llm.creative().generate("Tell a short story", max_tokens=50)
    print(f"✓ Creative chained: {chained_response[:50]}...")

    # Test chat
    print("\n=== Chat Interface ===")
    chat_response = llm.default().chat("What's 2+2?")
    print(f"✓ Chat response: {chat_response[:50]}...")

    # Test parameter setting
    print("\n=== Parameter Management ===")
    param_response = llm.set_parameters(temperature=0.5).generate(
        "Quick test", max_tokens=20
    )
    print(f"✓ Custom params: {param_response[:50]}...")

    # Test information methods
    print("\n=== Information Methods ===")
    print(f"✓ Available models: {llm.available_models()}")
    print(f"✓ Current parameters: {list(llm.current_parameters().keys())}")

    print("\n🎉 All API tests passed!")


if __name__ == "__main__":
    test_api_interface()
