from typing import List, Dict, Any, Optional, Union
import json

from azure.ai.evaluation import (
    AzureOpenAIModelConfiguration,
    OpenAIModelConfiguration,
)

from openai import AzureOpenAI, OpenAI

from ._models import _EvaluationCase


class _CritiqueGenerator:
    """Generates critiques for prompts based on evaluation results."""

    def __init__(
        self,
        client: Union[AzureOpenAI, OpenAI],
        model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration],
    ):
        """Initialize with client factory for lazy client creation.

        :param client: OpenAI client instance.
        :type client: Union[AzureOpenAI, OpenAI]
        :param model_config: Model configuration object.
        :type model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration]
        """
        self.client = client
        self._model_config = model_config

    def get_model_name(self) -> str:
        """Get the model name from the configuration.

        :return: Model name or deployment name.
        :rtype: str
        """
        if isinstance(self.client, AzureOpenAI):
            return self._model_config.get("azure_deployment", "")
        return self._model_config.get("model", "")

    def generate_critique(
        self,
        case: _EvaluationCase,
        system_prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Generate a critique for a single evaluation case.

        :param case: Evaluation case to critique.
        :type case: _EvaluationCase
        :param system_prompt: Current system prompt text.
        :type system_prompt: str
        :param tools: Optional list of tool configurations.
        :type tools: Optional[List[Dict[str, Any]]]
        :return: Generated critique text.
        :rtype: str
        """

        critique_prompt = self._build_critique_prompt(case, system_prompt, tools)

        response = self.client.chat.completions.create(
            model=self.get_model_name(),
            messages=[{"role": "user", "content": critique_prompt}],
            temperature=0.3,
        )

        return response.choices[0].message.content or ""

    def aggregate_critiques(self, critiques: List[str]) -> str:
        """Aggregate multiple critiques into a meta-critique.

        :param critiques: List of individual critique messages.
        :type critiques: List[str]
        :return: Aggregated meta-critique text.
        :rtype: str
        """

        if not critiques:
            return "No critiques to aggregate."

        if len(critiques) == 1:
            return critiques[0]

        aggregate_prompt = f"""
You are an expert prompt engineer. I have {len(critiques)} individual critiques of a system prompt. 
Please synthesize them into a single, comprehensive meta-critique that identifies the most important issues and improvements.

Individual Critiques:
{chr(10).join(f"{i+1}. {critique}" for i, critique in enumerate(critiques))}

Provide a synthesized meta-critique that captures the key insights:
"""

        response = self.client.chat.completions.create(
            model=self.get_model_name(),
            messages=[{"role": "user", "content": aggregate_prompt}],
            temperature=0.3,
        )

        return response.choices[0].message.content or ""

    def _build_critique_prompt(
        self,
        case: _EvaluationCase,
        system_prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Build the critique prompt.

        :param case: Evaluation case containing scores and conversation data.
        :type case: _EvaluationCase
        :param system_prompt: Current system prompt text.
        :type system_prompt: str
        :param tools: Optional list of tool configurations.
        :type tools: Optional[List[Dict[str, Any]]]
        :return: Formatted critique prompt text.
        :rtype: str
        """

        score_summary = "\n".join(
            f"- {metric}: {score:.2f}" for metric, score in case.scores.items()
        )

        tools_summary = ""
        if tools:
            tools_summary = f"\n\nTools Available:\n{json.dumps(tools, indent=2)}"

        return f"""
You are an expert prompt engineer. Analyze the following system prompt and its evaluation scores to provide a detailed critique.

System Prompt:
{system_prompt}

Evaluation Scores:
{score_summary}{tools_summary}

Conversation:
{json.dumps(case.conversation, indent=2)}

Please provide a detailed critique focusing on:
1. What aspects of the prompt led to these scores
2. Specific improvements that could be made
3. How the prompt could better handle this type of conversation
4. Any tool usage considerations (if tools are available)

Provide actionable, specific feedback:
"""


class _PromptImprover:
    """Improves prompts based on critiques."""

    def __init__(
        self,
        client: Union[AzureOpenAI, OpenAI],
        model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration],
    ):
        """Initialize with client factory for lazy client creation.

        :param client: OpenAI client instance.
        :type client: Union[AzureOpenAI, OpenAI]
        :param model_config: Model configuration object.
        :type model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration]
        """
        self.client = client
        self._model_config = model_config

    def get_model_name(self) -> str:
        """Get the model name from the configuration.

        :return: Model name or deployment name.
        :rtype: str
        """
        if isinstance(self.client, AzureOpenAI):
            return self._model_config.get("azure_deployment", "")
        return self._model_config.get("model", "")

    def improve_prompt(
        self,
        original_prompt: str,
        meta_critique: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        human_intent: Optional[str] = None,
    ) -> str:
        """Improve a prompt based on the meta-critique and optional human intent.

        :param original_prompt: The original prompt text to improve.
        :type original_prompt: str
        :param meta_critique: Aggregated critique containing improvement suggestions.
        :type meta_critique: str
        :param tools: Optional list of tool configurations to consider.
        :type tools: Optional[List[Dict[str, Any]]]
        :param human_intent: Optional human-specified improvement intent.
        :type human_intent: Optional[str]
        :return: Improved prompt text.
        :rtype: str
        """

        tools_context = ""
        if tools:
            tools_context = f"""
Tools Available:
{json.dumps(tools, indent=2)}

Consider tool usage in your improvements.
"""

        human_intent_context = ""
        if human_intent:
            human_intent_context = f"""
Human Intent for Improvement:
{human_intent}

PRIORITIZE the human intent while also addressing the critique.
"""

        improvement_prompt = f"""
You are an expert prompt engineer. Given an original system prompt and a detailed critique, create an improved version.

Original Prompt:
{original_prompt}

Critique:
{meta_critique}{tools_context}{human_intent_context}

Create an improved system prompt that addresses the issues raised in the critique. 
Return ONLY the improved prompt text, no explanations or additional formatting.
"""

        response = self.client.chat.completions.create(
            model=self.get_model_name(),
            messages=[{"role": "user", "content": improvement_prompt}],
            temperature=0.1,
        )

        return (response.choices[0].message.content or "").strip()
