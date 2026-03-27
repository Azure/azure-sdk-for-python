# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Dict, Any, List, Union
from typing_extensions import Literal, Required, TypedDict
from openai.types.evals.create_eval_completions_run_data_source_param import (
    InputMessagesItemReference,
    SourceFileContent,
    SourceFileID,
)
from ._models import ToolDescription


class AzureAIAgentTarget(TypedDict, total=False):
    """Represents a target specifying an Azure AI agent.

    :ivar type: The type of target, always ``azure_ai_agent``. Required. Default value is
     "azure_ai_agent".
    :vartype type: str
    :ivar name: The unique identifier of the Azure AI agent. Required.
    :vartype name: str
    :ivar version: The version of the Azure AI agent.
    :vartype version: str
    :ivar tool_descriptions: The parameters used to control the sampling behavior of the agent
     during text generation.
    :vartype tool_descriptions: list[~azure.ai.projects.models.ToolDescription]
    """

    type: Required[Literal["azure_ai_agent"]]
    """The type of target, always ``azure_ai_agent``. Required. Default value is \"azure_ai_agent\"."""
    name: Required[str]
    """The unique identifier of the Azure AI agent. Required."""
    version: str
    """The version of the Azure AI agent."""
    tool_descriptions: List[ToolDescription]
    """The parameters used to control the sampling behavior of the agent during text generation."""


class TargetCompletionEvalRunDataSource(TypedDict, total=False):
    """Represents a data source for target-based completion evaluation configuration.

    :ivar type: The type of data source, always ``azure_ai_target_completions``. Required. Default
     value is "azure_ai_target_completions".
    :vartype type: str
    :ivar input_messages: Input messages configuration.
    :vartype input_messages:
     ~azure.ai.projects.models.CreateEvalCompletionsRunDataSourceInputMessagesItemReference
    :ivar source: The source configuration for inline or file data. Required. Is either a
     SourceFileContent type or a SourceFileID type.
    :vartype source: ~azure.ai.projects.models.SourceFileContent or
     ~azure.ai.projects.models.SourceFileID
    :ivar target: The target configuration for the evaluation. Required.
    :vartype target: ~azure.ai.projects.models.Target
    """

    type: Required[Literal["azure_ai_target_completions"]]
    """The type of data source, always ``azure_ai_target_completions``. Required. Default value is
     \"azure_ai_target_completions\"."""
    source: Required[Union[SourceFileContent, SourceFileID]]
    """The source configuration for inline or file data. Required. Is either a
     SourceFileContent type or a SourceFileID type."""
    target: Required[AzureAIAgentTarget]
    """The target configuration for the evaluation. Required."""
    input_messages: Required[InputMessagesItemReference]
    """Input messages configuration."""


class EvalGraderAzureAIEvaluator(TypedDict, total=False):
    """AzureAIEvaluatorGrader.

    :ivar type: The object type, which is always ``azure_ai_evaluator``. Required. Default value is
     "azure_ai_evaluator".
    :vartype type: str
    :ivar name: The name of the grader. Required.
    :vartype name: str
    :ivar evaluator_name: The name of the evaluator. Required.
    :vartype evaluator_name: str
    :ivar evaluator_version: The version of the evaluator. Latest version if not specified.
    :vartype evaluator_version: str
    :ivar initialization_parameters: The initialization parameters for the evaluation. Must support
     structured outputs.
    :vartype initialization_parameters: dict[str, any]
    :ivar data_mapping: The model to use for the evaluation. Must support structured outputs.
    :vartype data_mapping: dict[str, str]
    """

    type: Required[Literal["azure_ai_evaluator"]]
    """The object type, which is always ``azure_ai_evaluator``. Required. Default value is
     \"azure_ai_evaluator\"."""
    name: Required[str]
    """The name of the grader. Required."""
    evaluator_name: Required[str]
    """The name of the evaluator. Required."""
    evaluator_version: str
    """The version of the evaluator. Latest version if not specified."""
    initialization_parameters: Dict[str, Any]
    """The initialization parameters for the evaluation. Must support structured outputs."""
    data_mapping: Dict[str, str]
    """The model to use for the evaluation. Must support structured outputs."""
