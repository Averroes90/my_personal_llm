import time
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
from statistics import mean, median, stdev


@dataclass
class BenchmarkResult:
    """Results from a benchmark run"""

    prompt: str
    response: str
    duration: float
    parameters: Dict[str, Any]
    model: str
    timestamp: float


class LLMBenchmark:
    """Benchmarking tools for LLM performance"""

    def __init__(self, llm_instance):
        self.llm = llm_instance
        self.results = []

    def time_generation(self, prompt: str, **kwargs) -> BenchmarkResult:
        """Time a single generation"""
        start_time = time.time()

        response = self.llm.generate(prompt, **kwargs)

        end_time = time.time()
        duration = end_time - start_time

        result = BenchmarkResult(
            prompt=prompt,
            response=response,
            duration=duration,
            parameters=self.llm.current_parameters(),
            model=self.llm.current_model(),
            timestamp=start_time,
        )

        self.results.append(result)
        return result

    def benchmark_presets(
        self, prompt: str, presets: List[str] = None
    ) -> Dict[str, BenchmarkResult]:
        """Benchmark different presets with the same prompt"""
        if presets is None:
            presets = ["default", "creative", "precise"]

        results = {}
        original_preset = self.llm.current_preset()

        try:
            for preset in presets:
                print(f"🔄 Benchmarking preset: {preset}")
                self.llm.set_preset(preset)
                result = self.time_generation(prompt)
                results[preset] = result
                print(f"  ⏱️  {result.duration:.2f}s")
        finally:
            self.llm.set_preset(original_preset)

        return results

    def benchmark_parameters(
        self, prompt: str, parameter_sets: List[Dict[str, Any]]
    ) -> List[BenchmarkResult]:
        """Benchmark different parameter combinations"""
        results = []

        for i, params in enumerate(parameter_sets):
            print(
                f"🔄 Benchmarking parameter set {i+1}/{len(parameter_sets)}: {params}"
            )
            result = self.time_generation(prompt, **params)
            results.append(result)
            print(f"  ⏱️  {result.duration:.2f}s")

        return results

    def stress_test(self, prompt: str, iterations: int = 5, **kwargs) -> Dict[str, Any]:
        """Run multiple iterations to test consistency"""
        print(f"🔄 Running stress test: {iterations} iterations")

        results = []
        for i in range(iterations):
            print(f"  Iteration {i+1}/{iterations}")
            result = self.time_generation(prompt, **kwargs)
            results.append(result)

        durations = [r.duration for r in results]
        response_lengths = [len(r.response) for r in results]

        return {
            "iterations": iterations,
            "total_time": sum(durations),
            "avg_time": mean(durations),
            "median_time": median(durations),
            "std_dev": stdev(durations) if len(durations) > 1 else 0,
            "min_time": min(durations),
            "max_time": max(durations),
            "avg_response_length": mean(response_lengths),
            "results": results,
        }

    def generate_report(self) -> str:
        """Generate a comprehensive benchmark report"""
        if not self.results:
            return "No benchmark results available."

        durations = [r.duration for r in self.results]
        response_lengths = [len(r.response) for r in self.results]

        report = []
        report.append("=" * 50)
        report.append("LLM BENCHMARK REPORT")
        report.append("=" * 50)
        report.append(f"Total runs: {len(self.results)}")
        report.append(f"Average duration: {mean(durations):.2f}s")
        report.append(f"Median duration: {median(durations):.2f}s")
        report.append(
            f"Min/Max duration: {min(durations):.2f}s / {max(durations):.2f}s"
        )
        report.append(f"Average response length: {mean(response_lengths):.0f} chars")

        if len(durations) > 1:
            report.append(f"Standard deviation: {stdev(durations):.2f}s")

        report.append("\nRecent Results:")
        for i, result in enumerate(self.results[-5:], 1):
            report.append(f"{i}. {result.duration:.2f}s - {result.prompt[:50]}...")

        return "\n".join(report)

    def clear_results(self):
        """Clear benchmark history"""
        self.results = []
        print("✓ Benchmark results cleared")


def quick_benchmark(
    llm_instance, prompt: str = "Tell me a short story about robots."
) -> Dict[str, Any]:
    """Quick benchmark for immediate feedback"""
    benchmark = LLMBenchmark(llm_instance)

    print("🚀 Running quick benchmark...")

    # Test all presets
    preset_results = benchmark.benchmark_presets(prompt)

    # Test different temperatures
    temp_results = benchmark.benchmark_parameters(
        prompt, [{"temperature": 0.3}, {"temperature": 0.8}, {"temperature": 1.2}]
    )

    return {
        "preset_results": preset_results,
        "temperature_results": temp_results,
        "summary": benchmark.generate_report(),
    }
