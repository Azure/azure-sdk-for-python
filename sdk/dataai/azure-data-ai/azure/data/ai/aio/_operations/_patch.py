# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, IO, Union, overload

from ... import models, types
from ..._operations._patch import _prepare_semantic_rerank_request
from ._operations import _InferenceClientOperationsMixin as _GeneratedOperations

__all__ = ["_InferenceClientOperationsMixin"]


class _InferenceClientOperationsMixin(_GeneratedOperations):
    @overload
    async def semantic_rerank(
        self,
        request: models.SemanticRerankingInferenceContent,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> models.SemanticRerankingInferenceResult: ...

    @overload
    async def semantic_rerank(
        self, request: types.SemanticRerankingInferenceContent, *, content_type: str = "application/json", **kwargs: Any
    ) -> models.SemanticRerankingInferenceResult: ...

    @overload
    async def semantic_rerank(
        self, request: Union[bytes, IO[bytes]], *, content_type: str = "application/json", **kwargs: Any
    ) -> models.SemanticRerankingInferenceResult: ...

    async def semantic_rerank(
        self,
        request: Union[
            models.SemanticRerankingInferenceContent, types.SemanticRerankingInferenceContent, bytes, IO[bytes]
        ],
        **kwargs: Any
    ) -> models.SemanticRerankingInferenceResult:
        return await super().semantic_rerank(_prepare_semantic_rerank_request(request), **kwargs)

    semantic_rerank.__doc__ = _GeneratedOperations.semantic_rerank.__doc__


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
