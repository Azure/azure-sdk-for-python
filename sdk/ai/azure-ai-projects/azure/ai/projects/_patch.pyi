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
from openai.types.eval_create_params import DataSourceConfig, TestingCriterion
from openai.types.eval_create_response import EvalCreateResponse
from openai.types.shared_params.metadata import Metadata
from ._client import AIProjectClient as AIProjectClientGenerated
from .models import EvalGraderAzureAIEvaluator

class _AzureEvals(Evals):
    def create(
        self,
        *,
        data_source_config: DataSourceConfig,
        testing_criteria: Iterable[
            Union[
                TestingCriterion,
                EvalGraderAzureAIEvaluator,
            ]
        ],
        metadata: Optional[Metadata] | Omit | None = ...,
        name: str | Omit = ...,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | Timeout | NotGiven | None = ...,
    ) -> EvalCreateResponse: ...

class OpenAI(OpenAIClient):
    @property
    def evals(self) -> _AzureEvals: ...

class AIProjectClient(AIProjectClientGenerated):
    def get_openai_client(self, **kwargs: Any) -> OpenAI: ...
