# pylint: disable=line-too-long,useless-suppression
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
    from azure.core.polling import AsyncLROPoller
    from azure.ai.contentunderstanding.models import AnalyzeResult

__all__: list[str] = []  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Patch the generated code to add custom functionality.

    1. Wrap begin_analyze and begin_analyze_binary to return custom LROPoller with .details property
    2. Hide string_encoding parameter and always use "codePoint" (correct for Python)

    Note: content_type default fix is now directly in generated code (search for EMITTER-FIX)
    """
    from ._operations import _ContentUnderstandingClientOperationsMixin
    from ...aio.operations._patch import AnalyzeAsyncLROPoller

    # Store original methods
    original_begin_analyze = _ContentUnderstandingClientOperationsMixin.begin_analyze
    original_begin_analyze_binary = _ContentUnderstandingClientOperationsMixin.begin_analyze_binary

    # Wrap begin_analyze to return custom poller and set string_encoding
    async def begin_analyze_wrapped(
        self,
        analyzer_id: str,
        *,
        processing_location: Any = None,
        content_type: str = "application/json",
        inputs: Any = None,
        model_deployments: Any = None,
        **kwargs: Any
    ) -> "AsyncLROPoller[AnalyzeResult]":
        """Extract content and fields from input.

        :param analyzer_id: The unique identifier of the analyzer. Required.
        :type analyzer_id: str
        :keyword processing_location: The location where the data may be processed. Defaults to
         global. Known values are: "geography", "dataZone", and "global". Default value is None.
        :paramtype processing_location: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword inputs: Inputs to analyze. Currently, only pro mode supports multiple inputs.
         Default value is None.
        :paramtype inputs: list[~azure.ai.contentunderstanding.models.AnalyzeInput]
        :keyword model_deployments: Override default mapping of model names to deployments.
         Ex. { "gpt-4.1": "myGpt41Deployment", "text-embedding-3-large":
         "myTextEmbedding3LargeDeployment" }. Default value is None.
        :paramtype model_deployments: dict[str, str]
        :return: An instance of AnalyzeAsyncLROPoller that returns AnalyzeResult. The AnalyzeResult is
         compatible with MutableMapping. The poller includes a .details property with operation metadata.
        :rtype: ~azure.ai.contentunderstanding.aio.operations.AnalyzeAsyncLROPoller[~azure.ai.contentunderstanding.models.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. note::
           The string_encoding parameter is automatically set to "codePoint" for Python as it
           matches Python's native string indexing behavior (len() and str[i] use code points).
           This ensures ContentSpan offsets work correctly with Python string slicing.
        """
        # Always use codePoint encoding for Python (matches Python's string indexing)
        kwargs["string_encoding"] = "codePoint"
        poller = await original_begin_analyze(
            self,
            analyzer_id,
            processing_location=processing_location,
            content_type=content_type,
            inputs=inputs,
            model_deployments=model_deployments,
            **kwargs
        )
        return AnalyzeAsyncLROPoller(
            self._client,  # type: ignore
            poller._polling_method._initial_response,  # type: ignore  # pylint: disable=protected-access
            poller._polling_method._deserialization_callback,  # type: ignore  # pylint: disable=protected-access
            poller._polling_method,  # pylint: disable=protected-access
        )

    # Wrap begin_analyze_binary to return custom poller and set string_encoding
    async def begin_analyze_binary_wrapped(
        self,
        analyzer_id: str,
        binary_input: bytes,
        *,
        processing_location: Any = None,
        input_range: Any = None,
        content_type: str = "application/octet-stream",
        **kwargs: Any
    ) -> "AsyncLROPoller[AnalyzeResult]":
        """Extract content and fields from input.

        :param analyzer_id: The unique identifier of the analyzer. Required.
        :type analyzer_id: str
        :param binary_input: The binary content of the document to analyze. Required.
        :type binary_input: bytes
        :keyword processing_location: The location where the data may be processed. Defaults to
         global. Known values are: "geography", "dataZone", and "global". Default value is None.
        :paramtype processing_location: str
        :keyword input_range: Range of the input to analyze (ex. ``1-3,5,9-``). Document content uses
         1-based page numbers, while audio visual content uses integer milliseconds. Default value is None.
        :paramtype input_range: str
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/octet-stream".
        :paramtype content_type: str
        :return: An instance of AnalyzeAsyncLROPoller that returns AnalyzeResult. The AnalyzeResult is
         compatible with MutableMapping. The poller includes a .details property with operation metadata.
        :rtype: ~azure.ai.contentunderstanding.aio.operations.AnalyzeAsyncLROPoller[~azure.ai.contentunderstanding.models.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. note::
           The string_encoding parameter is automatically set to "codePoint" for Python as it
           matches Python's native string indexing behavior (len() and str[i] use code points).
           This ensures ContentSpan offsets work correctly with Python string slicing.
        """
        # Always use codePoint encoding for Python (matches Python's string indexing)
        kwargs["string_encoding"] = "codePoint"
        poller = await original_begin_analyze_binary(
            self,
            analyzer_id,
            binary_input,
            processing_location=processing_location,
            input_range=input_range,
            content_type=content_type,
            **kwargs
        )
        return AnalyzeAsyncLROPoller(
            self._client,  # type: ignore
            poller._polling_method._initial_response,  # type: ignore  # pylint: disable=protected-access
            poller._polling_method._deserialization_callback,  # type: ignore  # pylint: disable=protected-access
            poller._polling_method,  # pylint: disable=protected-access
        )

    # Replace the methods
    _ContentUnderstandingClientOperationsMixin.begin_analyze = begin_analyze_wrapped
    _ContentUnderstandingClientOperationsMixin.begin_analyze_binary = begin_analyze_binary_wrapped
