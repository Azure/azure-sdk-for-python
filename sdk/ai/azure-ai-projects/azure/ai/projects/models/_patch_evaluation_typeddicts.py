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


class ResponseRetrievalItemGenerationParams(TypedDict, total=False):
    """Represents the parameters for response retrieval item generation.

    :ivar type: The type of item generation parameters, always ``response_retrieval``. Required.
     The ResponseRetrieval item generation parameters.
    :vartype type: str or ~azure.ai.projects.models.RESPONSE_RETRIEVAL
    :ivar max_num_turns: The maximum number of turns of chat history to evaluate. Required.
    :vartype max_num_turns: int
    :ivar data_mapping: Mapping from source fields to response_id field, required for retrieving
     chat history. Required.
    :vartype data_mapping: dict[str, str]
    :ivar source: The source from which JSONL content is read. Required. Is either a
     EvalJsonlFileContentSource type or a EvalJsonlFileIdSource type.
    :vartype source: ~azure.ai.projects.models.EvalJsonlFileContentSource or
     ~azure.ai.projects.models.EvalJsonlFileIdSource
    """

    type: Required[Literal["response_retrieval"]]
    """The type of item generation parameters, always ``response_retrieval``. Required. The
     ResponseRetrieval item generation parameters."""
    max_num_turns: int # Required[int] # TODO: In TypeSpec this is required, but samle code does not set it
    """The maximum number of turns of chat history to evaluate. Required."""
    data_mapping: Required[Dict[str, str]]
    """Mapping from source fields to response_id field, required for retrieving chat history.
     Required."""
    source: Required[Union[SourceFileContent, SourceFileID]]
    """The source from which JSONL content is read. Required. Is either a SourceFileContent
     type or a SourceFileID type."""


class AzureAIResponsesEvalRunDataSource(TypedDict, total=False):
    """Represents a data source for evaluation runs that are specific to Continuous Evaluation
    scenarios.

    :ivar type: The type of data source, always ``azure_ai_responses``. Required. Default value is
     "azure_ai_responses".
    :vartype type: str
    :ivar item_generation_params: The parameters for item generation. Required.
    :vartype item_generation_params:
     ~azure.ai.projects.models.ResponseRetrievalItemGenerationParams
    :ivar max_runs_hourly: Maximum number of evaluation runs allowed per hour. Required.
    :vartype max_runs_hourly: int
    :ivar event_configuration_id: The event configuration name associated with this evaluation run.
     Required.
    :vartype event_configuration_id: str
    """

    type: Required[Literal["azure_ai_responses"]]
    """The type of data source, always ``azure_ai_responses``. Required. Default value is
     \"azure_ai_responses\"."""
    item_generation_params: Required[ResponseRetrievalItemGenerationParams]
    """The parameters for item generation. Required."""
    max_runs_hourly: int  # Required[int]  # TODO: In TypeSpec this is required, but samle code does not set it
    """Maximum number of evaluation runs allowed per hour. Required."""
    event_configuration_id: str  # Required[str] # TODO: In TypeSpec this is required, but samle code does not set it
    """The event configuration name associated with this evaluation run. Required."""


class AzureAIDataSourceConfig(TypedDict, total=False):
    """AzureAIDataSourceConfig.

    You probably want to use the sub-classes and not this class directly. Known sub-classes are:
    AzureAIBenchmarkDataSourceConfig

    :ivar schema: The overall object JSON schema for the run data source items. Required.
    :vartype schema: dict[str, any]
    :ivar type: The object type, which is always ``azure_ai_source``. Required. Default value is
     "azure_ai_source".
    :vartype type: str
    :ivar scenario: Data schema scenario. Required. Is one of the following types:
     Literal["red_team"], Literal["responses"], Literal["traces_preview"],
     Literal["synthetic_data_gen_preview"], Literal["benchmark_preview"]
    :vartype scenario: str or str or str or str or str
    """

    type: Required[Literal["azure_ai_source"]]
    """The object type, which is always ``azure_ai_source``. Required. Default value is
     \"azure_ai_source\"."""
    scenario: Required[str]  # TODO: Update typespec to define the below strings as enum
    """Data schema scenario. Required. Is one of the following types: Literal[\"red_team\"],
     Literal[\"responses\"], Literal[\"traces_preview\"], Literal[\"synthetic_data_gen_preview\"],
     Literal[\"benchmark_preview\"]"""


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
