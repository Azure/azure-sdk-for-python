from typing import Dict, List, Any, Optional, Callable, Union, TypedDict

from azure.ai.evaluation._model_configurations import (
    AzureOpenAIModelConfiguration,
    OpenAIModelConfiguration,
)


class _PromptConfiguration(TypedDict):
    """Configuration for prompt settings."""

    system_prompt: str
    tools: List[Dict[str, Any]]


class _AgentBoosterConfig(TypedDict):
    """Main configuration for AgentBooster."""

    model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration]
    evaluators: Optional[List[Callable]]  # Default: None (uses default evaluators)

    max_iterations: int  # Default: 3
    # improvement_threshold: float  # Default: 0.1
    # early_stopping: bool  # Default: True
    improvement_intent: Optional[str]  # Default: None
    sample_size: int  # Default: 10
