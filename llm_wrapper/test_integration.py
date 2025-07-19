from api.local_llm import LocalLLM


def test_templates():
    print("🧪 Testing Template Integration\n")

    llm = LocalLLM()

    # Test template listing
    templates = llm.list_templates()
    print(f"✓ Found {len(templates)} templates")

    # Test template usage
    response = llm.use_template(
        "summarize",
        content_type="text",
        content="This is a test document with some content to summarize.",
    )
    print(f"✓ Template generation successful: {len(response)} chars")

    # Test template description
    description = llm.describe_template("analyze")
    print(f"✓ Template description: {description}")


def test_benchmarking():
    print("\n🧪 Testing Benchmarking Integration\n")

    llm = LocalLLM()

    # Test quick benchmark
    results = llm.quick_benchmark("Test prompt for benchmarking")
    print(f"✓ Quick benchmark completed")

    # Test report generation
    report = llm.benchmark_report()
    print(f"✓ Benchmark report generated: {len(report)} chars")


if __name__ == "__main__":
    test_templates()
    test_benchmarking()
    print("\n🎉 All integration tests passed!")
