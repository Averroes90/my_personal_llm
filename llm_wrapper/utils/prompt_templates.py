from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class PromptTemplate:
    """A reusable prompt template"""

    name: str
    template: str
    description: str
    default_params: Optional[Dict[str, Any]] = None


class PromptTemplates:
    """Collection of useful prompt templates for different tasks"""

    def __init__(self):
        self.templates = {
            # Research and Analysis
            "analyze": PromptTemplate(
                name="analyze",
                template="Please analyze the following {content_type}:\n\n{content}\n\nProvide a detailed analysis covering:\n1. Key points\n2. Strengths and weaknesses\n3. Implications\n4. Recommendations",
                description="Analyze any type of content systematically",
                default_params={"temperature": 0.7, "max_tokens": 400},
            ),
            "summarize": PromptTemplate(
                name="summarize",
                template="Please provide a concise summary of the following {content_type}:\n\n{content}\n\nSummary:",
                description="Summarize content efficiently",
                default_params={"temperature": 0.5, "max_tokens": 200},
            ),
            # Creative Writing
            "story": PromptTemplate(
                name="story",
                template="Write a {story_type} story about {topic}. The story should be {tone} in tone and approximately {length} long.\n\nStory:",
                description="Generate creative stories with specific parameters",
                default_params={"temperature": 1.0, "max_tokens": 500},
            ),
            "character": PromptTemplate(
                name="character",
                template="Create a detailed character description for {character_type}. Include:\n- Physical appearance\n- Personality traits\n- Background\n- Motivations\n- Unique quirks\n\nCharacter: {name}",
                description="Generate detailed character profiles",
                default_params={"temperature": 0.9, "max_tokens": 300},
            ),
            # Code and Technical
            "code_review": PromptTemplate(
                name="code_review",
                template="Please review the following {language} code:\n\n```{language}\n{code}\n```\n\nProvide feedback on:\n1. Code quality and structure\n2. Potential bugs or issues\n3. Performance considerations\n4. Best practices\n5. Suggestions for improvement",
                description="Review code for quality and improvements",
                default_params={"temperature": 0.4, "max_tokens": 400},
            ),
            "explain_code": PromptTemplate(
                name="explain_code",
                template="Please explain what this {language} code does in simple terms:\n\n```{language}\n{code}\n```\n\nExplanation:",
                description="Explain code functionality clearly",
                default_params={"temperature": 0.6, "max_tokens": 250},
            ),
            # Conversational
            "roleplay": PromptTemplate(
                name="roleplay",
                template="You are {character}. {character_description}\n\nHuman: {message}\n{character}:",
                description="Roleplay as specific characters",
                default_params={"temperature": 0.8, "max_tokens": 200},
            ),
            "debate": PromptTemplate(
                name="debate",
                template="Present arguments {position} the following topic: {topic}\n\nProvide 3-4 strong arguments with evidence and reasoning.\n\nArguments {position} {topic}:",
                description="Generate debate arguments for any position",
                default_params={"temperature": 0.7, "max_tokens": 350},
            ),
            # Research Templates
            "research_outline": PromptTemplate(
                name="research_outline",
                template="Create a detailed research outline for the topic: {topic}\n\nThe outline should include:\n1. Introduction and thesis\n2. Main sections with subsections\n3. Key questions to explore\n4. Potential sources\n5. Conclusion points\n\nOutline:",
                description="Generate comprehensive research outlines",
                default_params={"temperature": 0.6, "max_tokens": 400},
            ),
            # Uncensored/Open Templates
            "uncensored_creative": PromptTemplate(
                name="uncensored_creative",
                template="Write freely and creatively about {topic}. Express your thoughts without restrictions, exploring all angles and perspectives. Let your creativity flow naturally.\n\nTopic: {topic}\n\nResponse:",
                description="Open-ended creative expression",
                default_params={"temperature": 1.1, "max_tokens": 500},
            ),
            "explore_concept": PromptTemplate(
                name="explore_concept",
                template="Explore the concept of {concept} from multiple perspectives. Consider:\n- Different viewpoints and interpretations\n- Historical context\n- Modern applications\n- Controversial aspects\n- Future implications\n\nExploration of {concept}:",
                description="Deep exploration of concepts from all angles",
                default_params={"temperature": 0.8, "max_tokens": 450},
            ),
        }

    def get_template(self, name: str) -> PromptTemplate:
        """Get a specific template"""
        if name not in self.templates:
            available = list(self.templates.keys())
            raise ValueError(f"Template '{name}' not found. Available: {available}")
        return self.templates[name]

    def list_templates(self) -> List[str]:
        """Get list of available template names"""
        return list(self.templates.keys())

    def describe_template(self, name: str) -> str:
        """Get description of a template"""
        template = self.get_template(name)
        return f"{template.name}: {template.description}"

    def format_prompt(self, template_name: str, **kwargs) -> str:
        """Format a template with provided variables"""
        template = self.get_template(template_name)
        try:
            return template.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(
                f"Missing required variable for template '{template_name}': {e}"
            )

    def get_template_params(self, template_name: str) -> Dict[str, Any]:
        """Get default parameters for a template"""
        template = self.get_template(template_name)
        return template.default_params or {}


# Helper functions for easy access
def format_prompt(template_name: str, **kwargs) -> str:
    """Quick access to format a prompt template"""
    templates = PromptTemplates()
    return templates.format_prompt(template_name, **kwargs)


def list_templates() -> List[str]:
    """Quick access to list available templates"""
    templates = PromptTemplates()
    return templates.list_templates()
