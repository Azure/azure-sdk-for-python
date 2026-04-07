# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import datetime
from typing import Dict, Any, List, Union
from typing_extensions import Literal, Required, TypedDict
from openai.types.evals.create_eval_completions_run_data_source_param import (
    InputMessagesItemReference,
    SourceFileContent,
    SourceFileID,
)

# **************************************************************************************************
# BEGIN - These are duplicates of full classes implementation in _models.py. Redefined here as TypedDicts
# with "Param" suffix, so they can be used in type annotations for "openai_client.evals" operations
# **************************************************************************************************


# Note all properties on this class where required. Sample code suggest they are all optional. Update it here.
class ModelSamplingConfigParam(TypedDict, total=False):
    """Represents a set of parameters used to control the sampling behavior of a language model
    during text generation.
    """

    temperature: float
    """The temperature parameter for sampling. Required."""
    top_p: float
    """The top-p parameter for nucleus sampling. Required."""
    seed: int
    """The random seed for reproducibility. Required."""
    max_completion_tokens: int
    """The maximum number of tokens allowed in the completion. Required."""


class ToolDescriptionParam(TypedDict, total=False):
    """Description of a tool that can be used by an agent."""

    name: str
    """The name of the tool."""
    description: str
    """A brief description of the tool's purpose."""


class AzureAIAgentTargetParam(TypedDict, total=False):
    """Represents a target specifying an Azure AI agent."""

    type: Required[Literal["azure_ai_agent"]]
    """The type of target, always ``azure_ai_agent``. Required. Default value is \"azure_ai_agent\"."""
    name: Required[str]
    """The unique identifier of the Azure AI agent. Required."""
    version: str
    """The version of the Azure AI agent."""
    tool_descriptions: List[ToolDescriptionParam]
    """The parameters used to control the sampling behavior of the agent during text generation."""


class AzureAIModelTargetParam(TypedDict, total=False):
    """Represents a target specifying an Azure AI model for operations requiring model selection."""

    type: Required[Literal["azure_ai_model"]]
    """The type of target, always ``azure_ai_model``. Required. Default value is \"azure_ai_model\"."""
    model: str
    """The unique identifier of the Azure AI model."""
    sampling_params: ModelSamplingConfigParam
    """The parameters used to control the sampling behavior of the model during text generation."""


# *************************************************************************************************
# END - Typed re-definitions
# *************************************************************************************************


class ResponseRetrievalItemGenerationParams(TypedDict, total=False):
    """Represents the parameters for response retrieval item generation."""

    type: Required[Literal["response_retrieval"]]
    """The type of item generation parameters, always ``response_retrieval``. Required. The
     ResponseRetrieval item generation parameters."""
    max_num_turns: int  # Required[int] # TODO: In TypeSpec this is required, but sample code does not set it
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
    """

    type: Required[Literal["azure_ai_responses"]]
    """The type of data source, always ``azure_ai_responses``. Required. Default value is
     \"azure_ai_responses\"."""
    item_generation_params: Required[ResponseRetrievalItemGenerationParams]
    """The parameters for item generation. Required."""
    max_runs_hourly: int  # Required[int]  # TODO: In TypeSpec this is required, but sample code does not set it
    """Maximum number of evaluation runs allowed per hour. Required."""
    event_configuration_id: str  # Required[str] # TODO: In TypeSpec this is required, but sample code does not set it
    """The event configuration name associated with this evaluation run. Required."""


class AzureAIDataSourceConfig(TypedDict, total=False):
    """AzureAIDataSourceConfig."""

    type: Required[Literal["azure_ai_source"]]
    """The object type, which is always ``azure_ai_source``. Required. Default value is
     \"azure_ai_source\"."""
    scenario: Required[str]  # TODO: Update typespec to define the below strings as enum
    """Data schema scenario. Required. Is one of the following types: Literal[\"red_team\"],
     Literal[\"responses\"], Literal[\"traces_preview\"], Literal[\"synthetic_data_gen_preview\"],
     Literal[\"benchmark_preview\"]"""


class TargetCompletionEvalRunDataSource(TypedDict, total=False):
    """Represents a data source for target-based completion evaluation configuration."""

    type: Required[Literal["azure_ai_target_completions"]]
    """The type of data source, always ``azure_ai_target_completions``. Required. Default value is
     \"azure_ai_target_completions\"."""
    source: Required[Union[SourceFileContent, SourceFileID]]
    """The source configuration for inline or file data. Required. Is either a
     SourceFileContent type or a SourceFileID type."""
    target: Required[Union[AzureAIAgentTargetParam, AzureAIModelTargetParam, dict[str, Any]]]
    """The target configuration for the evaluation. Required."""
    input_messages: Required[InputMessagesItemReference]
    """Input messages configuration."""


class TestingCriterionAzureAIEvaluator(TypedDict, total=False):
    """AzureAIEvaluatorGrader."""

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


class AzureAIBenchmarkPreviewEvalRunDataSource(TypedDict, total=False):
    """Represents a data source for benchmark evaluation runs."""

    type: Required[Literal["azure_ai_benchmark_preview"]]
    """The type of data source, always ``azure_ai_benchmark_preview``. Required. Default value is
     \"azure_ai_benchmark_preview\"."""
    target: Required[Union[AzureAIModelTargetParam, AzureAIAgentTargetParam, dict[str, Any]]]
    """The target model or agent to evaluate against the benchmark. When using ``azure_ai_model``
     target, ``sampling_params`` must not be provided; inference parameters are auto-filled from the
     benchmark specification stored in eval group properties. Required. Is either a
     AzureAIModelTargetParam type or a AzureAIAgentTargetParam type."""
    input_messages: InputMessagesItemReference
    """Input messages configuration."""


class EvalCsvFileIdSource(TypedDict, total=False):
    """Represents a CSV data source by file ID."""

    type: Required[Literal["file_id"]]
    """The type of source, always ``file_id``. Required."""
    id: Required[str]
    """The identifier of the uploaded CSV file. Required."""


class EvalCsvRunDataSource(TypedDict, total=False):
    """Represents a CSV data source for evaluation runs."""

    type: Required[Literal["csv"]]
    """The type of data source, always ``csv``. Required. Default value is \"csv\"."""
    source: Required[EvalCsvFileIdSource]  # EvalCsvFileIdSource
    """The source of the CSV data, either inline content or a file reference. Required."""


class RedTeamEvalRunDataSource(TypedDict, total=False):
    """RedTeamEvalRunDataSource."""

    type: Required[Literal["azure_ai_red_team"]]
    """The type of data source. Always ``azure_ai_red_team``. Required. Default value is
     \"azure_ai_red_team\"."""
    item_generation_params: Required[Any]  # ItemGenerationParams
    """The parameters for item generation. Required."""
    target: Required[Union[AzureAIModelTargetParam, AzureAIAgentTargetParam, dict[str, Any]]]
    """The target configuration for the evaluation. Required."""


class TracesPreviewEvalRunDataSource(TypedDict, total=False):
    """Represents a data source for evaluation runs that operate over Agent traces stored in
    Application Insights.
    """

    type: Required[Literal["azure_ai_traces_preview"]]
    """The type of data source, always ``azure_ai_traces_preview``. Required. Default value is
     \"azure_ai_traces_preview\"."""
    trace_ids: List[str]
    """Collection of Agent trace identifiers that should be evaluated."""
    agent_id: str
    """The agent ID used to filter traces for evaluation."""
    agent_name: str
    """The agent name used to filter traces for evaluation."""
    lookback_hours: int
    """Lookback window (in hours) applied when retrieving traces from Application Insights. For
     scheduled evaluations this is inferred from the recurrence interval."""
    end_time: datetime.datetime
    """Unix timestamp (in seconds) marking the end of the trace query window. Defaults to the
     current time."""
    max_traces: int
    """Sampling limit applied to traces retrieved for evaluation."""
    ingestion_delay_seconds: int
    """The delay to apply for ingestion when querying traces."""
