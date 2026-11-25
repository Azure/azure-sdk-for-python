# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

import json
from typing import Any, IO, Union, overload

from .. import models, types
from .._utils.model_base import SdkJSONEncoder, _serialize
from ._operations import _InferenceClientOperationsMixin as _GeneratedOperations

__all__ = ["_InferenceClientOperationsMixin"]


# TODO: Fix the Python generator to honor @encode(ArrayEncoding.commaDelimited)
# for TypedDict request bodies. It currently applies this encoding only to models.
# Remove this workaround once regenerated code passes the dictionary-list regression tests.
def _prepare_semantic_rerank_request(
    request: Union[models.SemanticRerankingInferenceContent, types.SemanticRerankingInferenceContent, bytes, IO[bytes]],
) -> Union[models.SemanticRerankingInferenceContent, types.SemanticRerankingInferenceContent, bytes, IO[bytes]]:
    if isinstance(request, dict):
        target_paths = request.get("targetPaths")
        if isinstance(target_paths, list):
            body = {**request, "targetPaths": _serialize(target_paths, format="commaDelimited")}
            return json.dumps(body, cls=SdkJSONEncoder, exclude_readonly=True).encode("utf-8")
    return request


class _InferenceClientOperationsMixin(_GeneratedOperations):
    @overload
    def semantic_rerank(
        self,
        request: models.SemanticRerankingInferenceContent,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> models.SemanticRerankingInferenceResult: ...

    @overload
    def semantic_rerank(
        self, request: types.SemanticRerankingInferenceContent, *, content_type: str = "application/json", **kwargs: Any
    ) -> models.SemanticRerankingInferenceResult: ...

    @overload
    def semantic_rerank(
        self, request: Union[bytes, IO[bytes]], *, content_type: str = "application/json", **kwargs: Any
    ) -> models.SemanticRerankingInferenceResult: ...

    def semantic_rerank(
        self,
        request: Union[
            models.SemanticRerankingInferenceContent, types.SemanticRerankingInferenceContent, bytes, IO[bytes]
        ],
        **kwargs: Any
    ) -> models.SemanticRerankingInferenceResult:
        return super().semantic_rerank(_prepare_semantic_rerank_request(request), **kwargs)

    semantic_rerank.__doc__ = _GeneratedOperations.semantic_rerank.__doc__


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
