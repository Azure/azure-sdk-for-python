# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Type stub for _patch.py.

Overrides get_openai_client() return type so that evals.create() accepts
Azure-specific grader types in addition to the standard OpenAI graders.
"""

from typing import Any, Iterable, Union, Optional
from httpx import Timeout
from openai import NotGiven, Omit, OpenAI as OpenAIClient
from openai._types import Body, Query, Headers
from openai.resources.evals.evals import Evals
from openai.resources.evals.runs.runs import Runs
from openai.types.evals.run_create_params import DataSource
from openai.types.evals.run_create_response import RunCreateResponse
from openai.types.eval_create_params import DataSourceConfig, TestingCriterion
from openai.types.eval_create_response import EvalCreateResponse
from openai.types.shared_params.metadata import Metadata
from ._client import AIProjectClient as AIProjectClientGenerated
from .models import EvalGraderAzureAIEvaluator, TargetCompletionEvalRunDataSource

class _AzureEvalRuns(Runs):
    def create(
        self,
        eval_id: str,
        *,
        data_source: Union[DataSource, TargetCompletionEvalRunDataSource],  # <=== Azure extention here
        metadata: Optional[Metadata] | Omit = ...,
        name: str | Omit = ...,
        extra_headers: Headers | None = ...,
        extra_query: Query | None = ...,
        extra_body: Body | None = ...,
        timeout: float | Timeout | None | NotGiven = ...,
    ) -> RunCreateResponse: ...

class _AzureEvals(Evals):
    def create(
        self,
        *,
        data_source_config: DataSourceConfig,
        testing_criteria: Iterable[
            Union[
                TestingCriterion,
                EvalGraderAzureAIEvaluator,  # <=== Azure extention here
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
    def runs(self) -> _AzureEvalRuns: ...

class OpenAI(OpenAIClient):
    @property
    def evals(self) -> _AzureEvals: ...

class AIProjectClient(AIProjectClientGenerated):
    def get_openai_client(self, **kwargs: Any) -> OpenAI: ...
