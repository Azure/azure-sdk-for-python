# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from azure.core.polling import LROPoller
    from azure.ai.contentunderstanding.models import AnalyzeResult

__all__: list[str] = []  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Patch the generated code to add custom functionality.
    
    Wrap begin_analyze and begin_analyze_binary to return custom LROPoller with .details property.
    
    Note: content_type default fix is now directly in generated code (search for EMITTER-FIX)
    """
    from ._operations import _ContentUnderstandingClientOperationsMixin
    from ..operations._patch import AnalyzeLROPoller
    
    # Store original methods
    original_begin_analyze = _ContentUnderstandingClientOperationsMixin.begin_analyze
    original_begin_analyze_binary = _ContentUnderstandingClientOperationsMixin.begin_analyze_binary
    
    # Wrap begin_analyze to return custom LROPoller with .details property
    def begin_analyze_wrapped(
        self,
        analyzer_id: str,
        **kwargs: Any
    ) -> "LROPoller[AnalyzeResult]":
        """Wrapper that returns custom poller with .details property."""
        poller = original_begin_analyze(self, analyzer_id, **kwargs)
        return AnalyzeLROPoller(
            self._client,  # type: ignore
            poller._polling_method._initial_response,  # type: ignore  # pylint: disable=protected-access
            poller._polling_method._deserialization_callback,  # type: ignore  # pylint: disable=protected-access
            poller._polling_method,  # pylint: disable=protected-access
        )
    
    # Wrap begin_analyze_binary to return custom poller
    def begin_analyze_binary_wrapped(
        self,
        analyzer_id: str,
        binary_input: bytes,
        **kwargs: Any
    ) -> "LROPoller[AnalyzeResult]":
        """Wrapper that returns custom poller with .details property."""
        poller = original_begin_analyze_binary(self, analyzer_id, binary_input, **kwargs)
        return AnalyzeLROPoller(
            self._client,  # type: ignore
            poller._polling_method._initial_response,  # type: ignore  # pylint: disable=protected-access
            poller._polling_method._deserialization_callback,  # type: ignore  # pylint: disable=protected-access
            poller._polling_method,  # pylint: disable=protected-access
        )
    
    # Replace the methods
    _ContentUnderstandingClientOperationsMixin.begin_analyze = begin_analyze_wrapped
    _ContentUnderstandingClientOperationsMixin.begin_analyze_binary = begin_analyze_binary_wrapped
