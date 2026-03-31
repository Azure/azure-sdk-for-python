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
# BEGIN TODO: These are duplicates of full classes in _models.py... what should we do about these?
# **************************************************************************************************


class TypedDictModelSamplingParams(TypedDict, total=False):
    """Represents a set of parameters used to control the sampling behavior of a language model
    during text generation.

    :ivar temperature: The temperature parameter for sampling. Required.
    :vartype temperature: float
    :ivar top_p: The top-p parameter for nucleus sampling. Required.
    :vartype top_p: float
    :ivar seed: The random seed for reproducibility. Required.
    :vartype seed: int
    :ivar max_completion_tokens: The maximum number of tokens allowed in the completion. Required.
    :vartype max_completion_tokens: int
    """

    temperature: Required[float]
    """The temperature parameter for sampling. Required."""
    top_p: Required[float]
    """The top-p parameter for nucleus sampling. Required."""
    seed: Required[int]
    """The random seed for reproducibility. Required."""
    max_completion_tokens: Required[int]
    """The maximum number of tokens allowed in the completion. Required."""


class TypedDictTarget(TypedDict, total=False):
    """Base class for targets with discriminator support.

    You probably want to use the sub-classes and not this class directly. Known sub-classes are:
    TypedDictAzureAIAgentTarget, TypedDictAzureAIModelTarget

    :ivar type: The type of target. Required. Default value is None.
    :vartype type: str
    """

    type: Required[str]
    """The type of target. Required. Default value is None."""


class TypedDictAzureAIAgentTarget(TypedDict, total=False):
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
    :vartype tool_descriptions: list[dict[str, any]]
    """

    type: Required[Literal["azure_ai_agent"]]
    """The type of target, always ``azure_ai_agent``. Required. Default value is \"azure_ai_agent\"."""
    name: Required[str]
    """The unique identifier of the Azure AI agent. Required."""
    version: str
    """The version of the Azure AI agent."""
    tool_descriptions: List[Dict[str, Any]]
    """The parameters used to control the sampling behavior of the agent during text generation."""


class TypedDictAzureAIModelTarget(TypedDict, total=False):
    """Represents a target specifying an Azure AI model for operations requiring model selection.

    :ivar type: The type of target, always ``azure_ai_model``. Required. Default value is
     "azure_ai_model".
    :vartype type: str
    :ivar model: The unique identifier of the Azure AI model.
    :vartype model: str
    :ivar sampling_params: The parameters used to control the sampling behavior of the model during
     text generation.
    :vartype sampling_params: ~azure.ai.projects.models.TypedDictModelSamplingParams
    """

    type: Required[Literal["azure_ai_model"]]
    """The type of target, always ``azure_ai_model``. Required. Default value is \"azure_ai_model\"."""
    model: str
    """The unique identifier of the Azure AI model."""
    sampling_params: TypedDictModelSamplingParams
    """The parameters used to control the sampling behavior of the model during text generation."""


# *************************************************************************************************
# END TODO
# *************************************************************************************************


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
    max_runs_hourly: int  # Required[int]  # TODO: In TypeSpec this is required, but sample code does not set it
    """Maximum number of evaluation runs allowed per hour. Required."""
    event_configuration_id: str  # Required[str] # TODO: In TypeSpec this is required, but sample code does not set it
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
    :vartype target: ~azure.ai.projects.models.TypedDictAzureAIAgentTarget
    """

    type: Required[Literal["azure_ai_target_completions"]]
    """The type of data source, always ``azure_ai_target_completions``. Required. Default value is
     \"azure_ai_target_completions\"."""
    source: Required[Union[SourceFileContent, SourceFileID]]
    """The source configuration for inline or file data. Required. Is either a
     SourceFileContent type or a SourceFileID type."""
    target: Required[TypedDictAzureAIAgentTarget]
    """The target configuration for the evaluation. Required."""
    input_messages: Required[InputMessagesItemReference]
    """Input messages configuration."""


class AzureAIModelTarget(TypedDict, total=False):
    """Represents a target specifying an Azure AI model for operations requiring model selection.

    :ivar type: The type of target, always ``azure_ai_model``. Required. Default value is
     "azure_ai_model".
    :vartype type: str
    :ivar model: The unique identifier of the Azure AI model.
    :vartype model: str
    :ivar sampling_params: The parameters used to control the sampling behavior of the model during
     text generation.
    :vartype sampling_params: ~azure.ai.projects.models.ModelSamplingParams
    """

    type: Required[Literal["azure_ai_model"]]
    """The type of target, always ``azure_ai_model``. Required. Default value is
     \"azure_ai_model\"."""
    model: str
    """The unique identifier of the Azure AI model."""
    sampling_params: TypedDictModelSamplingParams
    """The parameters used to control the sampling behavior of the model during text generation."""


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


class AzureAIBenchmarkPreviewEvalRunDataSource(TypedDict, total=False):
    """Represents a data source for benchmark evaluation runs.

    :ivar type: The type of data source, always ``azure_ai_benchmark_preview``. Required. Default
     value is "azure_ai_benchmark_preview".
    :vartype type: str
    :ivar input_messages: Input messages configuration.
    :vartype input_messages:
     ~azure.ai.projects.models.CreateEvalCompletionsRunDataSourceInputMessagesItemReference
    :ivar target: The target model or agent to evaluate against the benchmark. When using
     ``azure_ai_model`` target, ``sampling_params`` must not be provided; inference parameters are
     auto-filled from the benchmark specification stored in eval group properties. Required. Is
     either a AzureAIModelTarget type or a AzureAIAgentTarget type.
    :vartype target: ~azure.ai.projects.models.AzureAIModelTarget or
     ~azure.ai.projects.models.AzureAIAgentTarget
    """

    type: Required[Literal["azure_ai_benchmark_preview"]]
    """The type of data source, always ``azure_ai_benchmark_preview``. Required. Default value is
     \"azure_ai_benchmark_preview\"."""
    target: Required[Union[TypedDictAzureAIModelTarget, TypedDictAzureAIAgentTarget]]
    """The target model or agent to evaluate against the benchmark. When using ``azure_ai_model``
     target, ``sampling_params`` must not be provided; inference parameters are auto-filled from the
     benchmark specification stored in eval group properties. Required. Is either a
     AzureAIModelTarget type or a AzureAIAgentTarget type."""
    input_messages: InputMessagesItemReference
    """Input messages configuration."""


class EvalCsvFileIdSource(TypedDict, total=False):
    """Represents a CSV data source by file ID.

    :ivar type: The type of source, always ``file_id``. Required.
    :vartype type: str
    :ivar id: The identifier of the uploaded CSV file. Required.
    :vartype id: str
    """

    type: Required[Literal["file_id"]]
    """The type of source, always ``file_id``. Required."""
    id: Required[str]
    """The identifier of the uploaded CSV file. Required."""


class EvalCsvRunDataSource(TypedDict, total=False):
    """Represents a CSV data source for evaluation runs.

    :ivar type: The type of data source, always ``csv``. Required. Default value is "csv".
    :vartype type: str
    :ivar source: The source of the CSV data, either inline content or a file reference. Required.
    :vartype source: ~azure.ai.projects.models.EvalCsvFileIdSource
    """

    type: Required[Literal["csv"]]
    """The type of data source, always ``csv``. Required. Default value is \"csv\"."""
    source: Required[EvalCsvFileIdSource]  # EvalCsvFileIdSource
    """The source of the CSV data, either inline content or a file reference. Required."""


class RedTeamEvalRunDataSource(TypedDict, total=False):
    """RedTeamEvalRunDataSource.

    :ivar type: The type of data source. Always ``azure_ai_red_team``. Required. Default value is
     "azure_ai_red_team".
    :vartype type: str
    :ivar item_generation_params: The parameters for item generation. Required.
    :vartype item_generation_params: ~azure.ai.projects.models.ItemGenerationParams
    :ivar target: The target configuration for the evaluation. Required.
    :vartype target: ~azure.ai.projects.models.TypedDictTarget
    """

    type: Required[Literal["azure_ai_red_team"]]
    """The type of data source. Always ``azure_ai_red_team``. Required. Default value is
     \"azure_ai_red_team\"."""
    item_generation_params: Required[Any]  # ItemGenerationParams
    """The parameters for item generation. Required."""
    target: Required[TypedDictTarget]
    """The target configuration for the evaluation. Required."""


class TracesPreviewEvalRunDataSource(TypedDict, total=False):
    """Represents a data source for evaluation runs that operate over Agent traces stored in
    Application Insights.

    :ivar type: The type of data source, always ``azure_ai_traces_preview``. Required. Default
     value is "azure_ai_traces_preview".
    :vartype type: str
    :ivar trace_ids: Collection of Agent trace identifiers that should be evaluated.
    :vartype trace_ids: list[str]
    :ivar agent_id: The agent ID used to filter traces for evaluation.
    :vartype agent_id: str
    :ivar agent_name: The agent name used to filter traces for evaluation.
    :vartype agent_name: str
    :ivar lookback_hours: Lookback window (in hours) applied when retrieving traces from
     Application Insights. For scheduled evaluations this is inferred from the recurrence interval.
    :vartype lookback_hours: int
    :ivar end_time: Unix timestamp (in seconds) marking the end of the trace query window. Defaults
     to the current time.
    :vartype end_time: ~datetime.datetime
    :ivar max_traces: Sampling limit applied to traces retrieved for evaluation.
    :vartype max_traces: int
    :ivar ingestion_delay_seconds: The delay to apply for ingestion when querying traces.
    :vartype ingestion_delay_seconds: int
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
