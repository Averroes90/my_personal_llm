import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from api.local_llm import LocalLLM


def template_demo():
    print("🎨 Template Demo\n")

    llm = LocalLLM()

    # Research template
    print("=== Research Analysis ===")
    analysis = llm.use_template(
        "analyze",
        content_type="business proposal",
        content="Launch a new AI-powered coding assistant that helps developers write better code faster.",
    )
    print(f"📊 Analysis: {analysis[:200]}...\n")

    # Creative template
    print("=== Creative Story ===")
    story = llm.use_template(
        "story",
        story_type="science fiction",
        topic="AI consciousness",
        tone="mysterious",
        length="short",
    )
    print(f"📚 Story: {story[:200]}...\n")

    # Code review template
    print("=== Code Review ===")
    code_review = llm.use_template(
        "code_review",
        language="python",
        code="def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)",
    )
    print(f"💻 Review: {code_review[:200]}...\n")


def benchmarking_demo():
    print("⚡ Benchmarking Demo\n")

    llm = LocalLLM()

    # Quick benchmark
    print("=== Quick Benchmark ===")
    results = llm.quick_benchmark("Explain quantum computing in simple terms.")

    print("Preset comparison:")
    for preset, result in results["preset_results"].items():
        print(f"  {preset}: {result.duration:.2f}s")

    print("\nTemperature comparison:")
    for result in results["temperature_results"]:
        temp = result.parameters.get("temperature", "unknown")
        print(f"  temp {temp}: {result.duration:.2f}s")

    # Stress test
    print("\n=== Stress Test ===")
    stress_results = llm.stress_test("Quick test prompt", iterations=3)
    print(f"Average time: {stress_results['avg_time']:.2f}s")
    print(f"Standard deviation: {stress_results['std_dev']:.2f}s")


def real_world_example():
    print("🌍 Real-World Integration Example\n")

    llm = LocalLLM()

    # Simulate a research workflow
    print("=== Research Workflow ===")

    # Step 1: Generate outline
    outline = llm.precise().use_template(
        "research_outline", topic="The impact of AI on software development"
    )
    print(f"📋 Outline generated: {len(outline)} characters")

    # Step 2: Creative exploration
    exploration = llm.creative().use_template(
        "explore_concept", concept="AI pair programming"
    )
    print(f"🧠 Exploration generated: {len(exploration)} characters")

    # Step 3: Generate supporting content
    summary = llm.default().use_template(
        "summarize",
        content_type="research findings",
        content=exploration[:500],  # Use part of exploration as content
    )
    print(f"📝 Summary generated: {len(summary)} characters")

    print(f"\n✓ Complete research workflow executed")


if __name__ == "__main__":
    template_demo()
    print("\n" + "=" * 60 + "\n")
    benchmarking_demo()
    print("\n" + "=" * 60 + "\n")
    real_world_example()
