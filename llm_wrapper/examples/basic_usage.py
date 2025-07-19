import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from api.local_llm import LocalLLM


def basic_examples():
    print("🚀 LocalLLM Basic Usage Examples\n")

    # Initialize (auto-selects model and uses default preset)
    llm = LocalLLM()

    print(f"✓ Initialized with model: {llm.current_model()}")
    print(f"✓ Using preset: {llm.current_preset()}\n")

    # Basic generation
    print("=== Basic Generation ===")
    response = llm.generate("What is the meaning of life?", max_tokens=80)
    print(f"🤖 Response: {response}\n")

    # Chat-style interaction
    print("=== Chat Style ===")
    chat_response = llm.chat("Hello! How are you today?")
    print(f"🤖 Chat response: {chat_response}\n")

    # Chat with context
    print("=== Chat with Context ===")
    context = [
        "What's your favorite color?",
        "I don't have personal preferences, but I find blue quite calming.",
        "Why do you find blue calming?",
    ]
    context_response = llm.chat("Tell me more about that.", context=context)
    print(f"🤖 Context response: {context_response}\n")

    # Preset switching with method chaining
    print("=== Preset Switching ===")
    creative_response = llm.creative().generate(
        "Write a haiku about robots", max_tokens=50
    )
    print(f"🎨 Creative: {creative_response}")

    precise_response = llm.precise().generate(
        "Define artificial intelligence", max_tokens=50
    )
    print(f"🎯 Precise: {precise_response}")

    # Custom parameters
    print("\n=== Custom Parameters ===")
    custom_response = llm.set_parameters(temperature=1.5, max_tokens=60).generate(
        "Invent a new word and define it"
    )
    print(f"🔥 High temp: {custom_response}")


def experimentation_example():
    print("\n🧪 Experimentation Features\n")

    llm = LocalLLM()

    # Compare different presets
    print("=== Preset Comparison ===")
    results = llm.experiment(
        "Tell me a joke about programming", presets=["default", "creative", "precise"]
    )

    for setting, response in results.items():
        print(f"{setting}: {response[:60]}...")

    # Compare different temperatures
    print("\n=== Temperature Comparison ===")
    temp_results = llm.experiment(
        "Complete this story: Once upon a time...",
        parameters={"temperature": [0.3, 0.8, 1.2]},
    )

    for setting, response in temp_results.items():
        print(f"{setting}: {response[:60]}...")


def status_example():
    print("\n📊 System Status\n")

    llm = LocalLLM()

    # Show system information
    print("=== System Information ===")
    status = llm.status()
    print(f"Available models: {status['model_stats']['available_models']}")
    print(f"Current model: {status['model_stats']['current_model']}")
    print(f"Current preset: {status['parameter_info']['current_preset']}")
    print(f"Current parameters: {status['parameter_info']['current_parameters']}")


if __name__ == "__main__":
    basic_examples()
    experimentation_example()
    status_example()
