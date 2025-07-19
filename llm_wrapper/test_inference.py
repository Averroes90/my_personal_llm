from core.inference_engine import InferenceEngine


def test_basic_inference():
    # Initialize engine
    engine = InferenceEngine()

    # Set model
    engine.set_model("mistral-7b-base")

    # Test basic generation
    print("🧪 Testing basic generation...")
    prompt = "The quick brown fox"
    response = engine.generate(prompt, max_tokens=50)

    print(f"\n📝 Prompt: {prompt}")
    print(f"🤖 Response: {response}")

    # Test with different parameters
    print("\n🧪 Testing with creative parameters...")
    response2 = engine.generate(
        "Once upon a time in a magical forest", temperature=1.0, max_tokens=100
    )

    print(f"🤖 Creative response: {response2}")


if __name__ == "__main__":
    test_basic_inference()
