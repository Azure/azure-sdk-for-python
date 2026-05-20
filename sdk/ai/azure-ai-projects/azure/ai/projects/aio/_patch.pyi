# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Type stub for _patch.py (async client).

Overrides get_openai_client() return type so that evals.create() accepts
Azure-specific grader types in addition to the standard OpenAI graders.
"""

from typing import Any, Iterable, List, Union, Optional
from httpx import Timeout
from openai import NotGiven, Omit, AsyncOpenAI as AsyncOpenAIClient
from openai._types import Body, Query, Headers
from openai.resources.evals.evals import AsyncEvals
from openai.resources.evals.runs.runs import AsyncRuns
from openai.types.evals.create_eval_jsonl_run_data_source_param import CreateEvalJSONLRunDataSourceParam
from openai.types.evals.create_eval_completions_run_data_source_param import CreateEvalCompletionsRunDataSourceParam
from openai.types.evals.run_create_params import DataSourceCreateEvalResponsesRunDataSource
from openai.types.evals.run_create_response import RunCreateResponse
from openai.types.eval_create_params import (
    DataSourceConfigCustom,
    DataSourceConfigLogs,
    DataSourceConfigStoredCompletions,
    TestingCriterionLabelModel,
    TestingCriterionTextSimilarity,
    TestingCriterionPython,
    TestingCriterionScoreModel,
)
from openai.types.graders.string_check_grader_param import StringCheckGraderParam
from openai.types.eval_create_response import EvalCreateResponse
from openai.types.shared_params.metadata import Metadata
from ._client import AIProjectClient as AIProjectClientGenerated
from .operations import TelemetryOperations
from ..models import (
    AzureAIBenchmarkPreviewEvalRunDataSource,
    AzureAIDataSourceConfig,
    AzureAIResponsesEvalRunDataSource,
    EvalCsvRunDataSource,
    TestingCriterionAzureAIEvaluator,
    RedTeamEvalRunDataSource,
    TargetCompletionEvalRunDataSource,
    TracesPreviewEvalRunDataSource,
)

class _AzureAsyncEvalRuns(AsyncRuns):
    async def create(
        self,
        eval_id: str,
        *,
        data_source: Union[
            CreateEvalJSONLRunDataSourceParam,
            CreateEvalCompletionsRunDataSourceParam,
            DataSourceCreateEvalResponsesRunDataSource,
            AzureAIBenchmarkPreviewEvalRunDataSource,
            AzureAIResponsesEvalRunDataSource,
            EvalCsvRunDataSource,
            RedTeamEvalRunDataSource,
            TargetCompletionEvalRunDataSource,
            TracesPreviewEvalRunDataSource,
        ],
        metadata: Optional[Metadata] | Omit = ...,
        name: str | Omit = ...,
        extra_headers: Headers | None = ...,
        extra_query: Query | None = ...,
        extra_body: Body | None = ...,
        timeout: float | Timeout | None | NotGiven = ...,
    ) -> RunCreateResponse: ...

class _AzureAsyncEvals(AsyncEvals):
    async def create(
        self,
        *,
        data_source_config: Union[
            DataSourceConfigCustom, DataSourceConfigLogs, DataSourceConfigStoredCompletions, AzureAIDataSourceConfig
        ],
        testing_criteria: Iterable[
            Union[
                TestingCriterionLabelModel,
                StringCheckGraderParam,
                TestingCriterionTextSimilarity,
                TestingCriterionPython,
                TestingCriterionScoreModel,
                TestingCriterionAzureAIEvaluator,
            ]
        ],
        metadata: Optional[Metadata] | Omit | None = ...,
        name: str | Omit = ...,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | Timeout | NotGiven | None = ...,
    ) -> EvalCreateResponse: ...
    @property
    def runs(self) -> _AzureAsyncEvalRuns: ...

class AsyncOpenAI(AsyncOpenAIClient):
    @property
    def evals(self) -> _AzureAsyncEvals: ...

class AIProjectClient(AIProjectClientGenerated):
    telemetry: TelemetryOperations
    def get_openai_client(
        self, agent_name: Optional[str] = None, **kwargs: Any  # pylint: disable=unused-argument
    ) -> AsyncOpenAI: ...

# To make mypy happy... otherwise imports of the below result in mypy "attr-defined" error
__all__: List[str] = ["AIProjectClient"]

def patch_sdk() -> None: ...
