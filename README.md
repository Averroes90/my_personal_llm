# LocalLLM Wrapper

A flexible, modular Python wrapper for local Large Language Model (LLM) inference using llama.cpp. Designed for research, experimentation, and internal AI system integration with minimal corporate controls and maximum flexibility.

## Features

- **Easy Model Management**: Simple switching between different models and quantization levels
- **Flexible Parameter Control**: Preset-based and custom parameter management for experimentation
- **Clean API Interface**: Intuitive methods for generation, chat, and experimentation
- **Prompt Templates**: Pre-built templates for common tasks (analysis, creative writing, code review, etc.)
- **Performance Benchmarking**: Built-in tools for measuring and comparing model performance
- **Method Chaining**: Fluent interface for quick parameter adjustments
- **Future-Ready Architecture**: Modular design prepared for memory optimization and multi-model support

## Quick Start

### Installation

1. **Prerequisites**: Ensure you have llama.cpp built and working with your models
2. **Clone and setup**:
```bash
git clone <your-repo>
cd llm_wrapper
python -m venv llm_wrapper_env
source llm_wrapper_env/bin/activate  # On Windows: llm_wrapper_env\Scripts\activate
pip install -e .
```

3. **Configure your models** in `config/models.yaml`

### Basic Usage

```python
from api.local_llm import LocalLLM

# Initialize (auto-selects available model)
llm = LocalLLM()

# Basic generation
response = llm.generate("What is artificial intelligence?")
print(response)

# Chat-style interaction
chat_response = llm.chat("Hello! How are you today?")
print(chat_response)

# Quick preset switching with method chaining
creative_response = llm.creative().generate("Write a haiku about robots")
precise_response = llm.precise().generate("Define machine learning")

# Custom parameters
custom_response = llm.set_parameters(temperature=1.2, max_tokens=200).generate(
    "Tell me an unusual fact"
)
```

## Configuration

### Models Configuration (`config/models.yaml`)

```yaml
models:
  mistral-7b-base:
    path: "~/llm-local-project/llama.cpp/models/mistral-7b-base.gguf"
    executable: "~/llm-local-project/llama.cpp/build/bin/llama-cli"
    size_gb: 4.1
    description: "Mistral 7B base model - uncensored"
    status: "active"
```

### Parameters Configuration (`config/parameters.yaml`)

```yaml
presets:
  default:
    temperature: 0.8
    top_p: 0.9
    repeat_penalty: 1.15
    repeat_last_n: 64
    max_tokens: 300
    
  creative:
    temperature: 1.0
    top_p: 0.95
    repeat_penalty: 1.1
    repeat_last_n: 64
    max_tokens: 500
    
  precise:
    temperature: 0.3
    top_p: 0.8
    repeat_penalty: 1.2
    repeat_last_n: 64
    max_tokens: 200
```

## Advanced Features

### Prompt Templates

Use pre-built templates for common tasks:

```python
# Research analysis
analysis = llm.use_template(
    "analyze",
    content_type="business proposal",
    content="Your content here..."
)

# Creative writing
story = llm.use_template(
    "story",
    story_type="science fiction",
    topic="AI consciousness",
    tone="mysterious",
    length="short"
)

# Code review
review = llm.use_template(
    "code_review",
    language="python",
    code="def example(): pass"
)

# List available templates
templates = llm.list_templates()
```

### Experimentation and Comparison

Compare different settings easily:

```python
# Compare presets
results = llm.experiment(
    "Tell me about quantum computing",
    presets=["default", "creative", "precise"]
)

# Compare parameters
temp_results = llm.experiment(
    "Write a short poem",
    parameters={"temperature": [0.3, 0.8, 1.2]}
)
```

### Performance Benchmarking

```python
# Quick benchmark
benchmark_results = llm.quick_benchmark("Test prompt")

# Stress test
stress_results = llm.stress_test("Test prompt", iterations=10)

# Generate performance report
report = llm.benchmark_report()
print(report)
```

### Chat with Context

```python
# Maintain conversation context
context = [
    "What's your favorite color?",
    "I don't have personal preferences, but blue is calming.",
    "Why do you find blue calming?"
]

response = llm.chat("Tell me more about that.", context=context)
```

## API Reference

### Core Methods

- `generate(prompt, **kwargs)` - Generate text from a prompt
- `chat(message, context=None, **kwargs)` - Chat-style interaction
- `set_model(model_name)` - Switch active model
- `set_preset(preset_name)` - Switch parameter preset
- `set_parameters(**kwargs)` - Set custom parameters

### Convenience Methods

- `creative()` - Switch to creative preset
- `precise()` - Switch to precise preset  
- `default()` - Switch to default preset

### Template Methods

- `use_template(template_name, **kwargs)` - Generate using template
- `list_templates()` - Get available templates
- `describe_template(template_name)` - Get template description

### Information Methods

- `available_models()` - List available models
- `current_model()` - Get current model name
- `current_preset()` - Get current preset
- `current_parameters()` - Get current parameters
- `status()` - Get comprehensive system status

### Benchmarking Methods

- `quick_benchmark(prompt)` - Run quick performance test
- `benchmark_presets(prompt, presets)` - Compare presets
- `stress_test(prompt, iterations)` - Test consistency
- `benchmark_report()` - Get performance report

## Project Structure

```
llm_wrapper/
├── core/
│   ├── model_manager.py      # Model discovery and management
│   ├── inference_engine.py   # llama.cpp subprocess wrapper
│   └── parameter_manager.py  # Parameter validation and presets
├── config/
│   ├── models.yaml          # Model definitions and paths
│   └── parameters.yaml      # Parameter presets and limits
├── api/
│   └── local_llm.py         # Main API interface
├── utils/
│   ├── prompt_templates.py  # Reusable prompt templates
│   └── benchmarking.py      # Performance measurement tools
├── examples/
│   ├── basic_usage.py       # Basic usage examples
│   └── integration_demo.py  # Advanced integration examples
├── tests/
│   └── test_*.py           # Test scripts
└── pyproject.toml          # Package configuration
```

## Available Prompt Templates

- **analyze** - Systematic content analysis
- **summarize** - Efficient content summarization
- **story** - Creative story generation
- **character** - Character profile creation
- **code_review** - Code quality review
- **explain_code** - Code explanation
- **roleplay** - Character roleplay
- **debate** - Argument generation
- **research_outline** - Research structure creation
- **uncensored_creative** - Open-ended creative expression
- **explore_concept** - Multi-perspective concept exploration

## Integration Examples

### Using in Other Projects

```python
# In your other Python projects
from llm_wrapper.api.local_llm import LocalLLM

class MyAIAssistant:
    def __init__(self):
        self.llm = LocalLLM(model="mistral-7b-base", preset="default")
    
    def analyze_document(self, document):
        return self.llm.use_template(
            "analyze",
            content_type="document",
            content=document
        )
    
    def creative_brainstorm(self, topic):
        return self.llm.creative().generate(
            f"Brainstorm creative ideas about: {topic}",
            max_tokens=400
        )
```

### Research Workflow

```python
# Complete research pipeline
llm = LocalLLM()

# 1. Generate outline
outline = llm.precise().use_template("research_outline", topic="AI Ethics")

# 2. Explore concepts
exploration = llm.creative().use_template("explore_concept", concept="AI bias")

# 3. Analyze findings
analysis = llm.default().use_template("analyze", 
                                     content_type="research notes",
                                     content=exploration)
```

## Development and Testing

### Running Tests

```bash
# Test basic functionality
python test_setup.py
python test_inference.py
python test_parameters.py
python test_models.py
python test_api.py
python test_integration.py

# Run examples
python examples/basic_usage.py
python examples/integration_demo.py
```

### Adding New Models

1. Add model configuration to `config/models.yaml`
2. Ensure model file and executable paths are correct
3. Test with `python test_models.py`

### Creating Custom Templates

```python
# Add to utils/prompt_templates.py
new_template = PromptTemplate(
    name="my_template",
    template="Your template with {variables}",
    description="Template description",
    default_params={"temperature": 0.8}
)
```

## Architecture and Future Expansion

The wrapper is designed with modularity and extensibility in mind:

- **Model Manager**: Ready for multi-model support and SSD offloading
- **Parameter Manager**: Extensible validation and optimization framework  
- **Inference Engine**: Prepared for different backends beyond llama.cpp
- **Memory Management**: Foundation for handling models exceeding RAM limits
- **API Design**: Clean interfaces that won't break with feature additions

Future capabilities being prepared:
- Large model SSD offloading strategies
- Multiple concurrent model support
- Advanced memory optimization
- Integration with other inference engines
- Distributed inference capabilities

## Requirements

- Python 3.10+
- llama.cpp (built and functional)
- PyYAML
- Compatible GGUF model files

## License

[Your chosen license]

## Contributing

[Contribution guidelines]

## Support

[Support information]

---

**Note**: This wrapper is designed for research and educational purposes with minimal censorship constraints. Users are responsible for ensuring appropriate and ethical use of the generated content.