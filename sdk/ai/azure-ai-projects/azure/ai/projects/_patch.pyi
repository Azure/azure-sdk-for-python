# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Type stub for _patch.py.

Overrides get_openai_client() return type so that evals.create() accepts
Azure-specific grader types in addition to the standard OpenAI graders.
"""

from typing import Any, Dict, Iterable, Union, Optional
from typing_extensions import Literal, Required, TypedDict

import httpx
from openai import OpenAI as OpenAIClient
from openai._types import Body, Omit, Query, Headers, NotGiven
from openai.resources.evals.evals import Evals
from openai.types.eval_create_params import DataSourceConfig, TestingCriterion
from openai.types.eval_create_response import EvalCreateResponse
from openai.types.shared_params.metadata import Metadata
from openai.types.graders import (
    LabelModelGraderParam,
    StringCheckGraderParam,
    TextSimilarityGraderParam,
    PythonGraderParam,
    ScoreModelGraderParam,
)

from ._client import AIProjectClient as AIProjectClientGenerated

class AzureAIGraderCoherenceParam(TypedDict, total=False):
    type: Required[Literal["azure_ai_evaluator"]]
    name: Required[str]
    evaluator_name: str
    initialization_parameters: Dict[str, str]
    data_mapping: Dict[str, str]

class _AzureEvals(Evals):
    def create(
        self,
        *,
        data_source_config: DataSourceConfig,
        testing_criteria: Iterable[
            Union[
                TestingCriterion,
                AzureAIGraderCoherenceParam,
            ]
        ],
        metadata: Optional[Metadata] | Omit = ...,
        name: str | Omit = ...,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = ...,
    ) -> EvalCreateResponse: ...

class OpenAI(OpenAIClient):
    @property
    def evals(self) -> _AzureEvals: ...

class AIProjectClient(AIProjectClientGenerated):
    def get_openai_client(self, **kwargs: Any) -> OpenAI: ...
