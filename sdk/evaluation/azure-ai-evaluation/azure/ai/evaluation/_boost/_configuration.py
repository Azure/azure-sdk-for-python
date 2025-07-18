from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Callable, Union

from azure.ai.evaluation._model_configurations import (
    AzureOpenAIModelConfiguration,
    OpenAIModelConfiguration,
)


@dataclass
class _PromptConfiguration:
    """Configuration for prompt settings."""

    system_prompt: str
    tools: List[Dict[str, Any]]


@dataclass
class _RefinementConfig:
    """Configuration for the refinement process."""

    max_iterations: int = 3
    improvement_threshold: float = 0.1  # Fixed: Use consistent default
    early_stopping: bool = True
    verbose: bool = False
    improvement_intent: Optional[str] = None

    def __post_init__(self):
        """Validate configuration values."""
        if self.max_iterations <= 0:
            raise ValueError("max_iterations must be greater than 0")
        if self.improvement_threshold < 0 or self.improvement_threshold > 1:
            raise ValueError("improvement_threshold must be between 0 and 1")


@dataclass
class _AgentBoosterConfig:
    """Main configuration for AgentBooster."""

    model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration]
    refinement: _RefinementConfig
    temp_dir: Optional[str] = None
    evaluators: Optional[List[Callable]] = (
        None  # Custom evaluators; if None, uses default evaluators
    )
