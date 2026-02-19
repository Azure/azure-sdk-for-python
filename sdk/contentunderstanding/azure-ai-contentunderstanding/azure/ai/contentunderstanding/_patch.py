# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import TYPE_CHECKING, Any, IO, Optional, Union, overload
from azure.core.tracing.decorator import distributed_trace

from ._client import ContentUnderstandingClient as GeneratedClient
from . import models as _models
from .models import AnalyzeLROPoller

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

JSON = dict[str, Any]
_Unset: Any = object()

__all__ = ["ContentUnderstandingClient"]


class ContentUnderstandingClient(GeneratedClient):
    """Custom ContentUnderstandingClient with static patches for analyze operations.

    This wrapper:
    - Hides the string_encoding parameter (always uses "codePoint" for Python)
    - Returns AnalyzeLROPoller with .operation_id property
    - Fixes content_type default for begin_analyze_binary

    :param endpoint: Content Understanding service endpoint. Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Is either a key
     credential type or a token credential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials.TokenCredential
    :keyword api_version: The API version to use for this operation. Default value is "2025-11-01".
     Note that overriding this default value may result in unsupported behavior.
    :paramtype api_version: str
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    """

    @overload  # type: ignore[override]
    def begin_analyze(
        self,
        analyzer_id: str,
        *,
        processing_location: Optional[Union[str, _models.ProcessingLocation]] = None,
        content_type: str = "application/json",
        inputs: Optional[list[_models.AnalyzeInput]] = None,
        model_deployments: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> "AnalyzeLROPoller[_models.AnalyzeResult]":  # pyright: ignore[reportInvalidTypeArguments]
        """Extract content and fields from input.

        :param analyzer_id: The unique identifier of the analyzer. Required.
        :type analyzer_id: str
        :keyword processing_location: The location where the data may be processed. Defaults to
         global. Known values are: "geography", "dataZone", and "global". Default value is None.
        :paramtype processing_location: str or ~azure.ai.contentunderstanding.models.ProcessingLocation
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
        :return: An instance of AnalyzeLROPoller that returns AnalyzeResult. The AnalyzeResult is
         compatible with MutableMapping. The poller includes an .operation_id property.
        :rtype: ~azure.ai.contentunderstanding.models.AnalyzeLROPoller[~azure.ai.contentunderstanding.models.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. note::
           The string_encoding parameter is automatically set to "codePoint" for Python as it
           matches Python's native string indexing behavior (len() and str[i] use code points).
           This ensures ContentSpan offsets work correctly with Python string slicing.
        """

    @overload  # type: ignore[override]
    def begin_analyze(
        self,
        analyzer_id: str,
        body: JSON,
        *,
        processing_location: Optional[Union[str, _models.ProcessingLocation]] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> "AnalyzeLROPoller[_models.AnalyzeResult]":  # pyright: ignore[reportInvalidTypeArguments]
        """Extract content and fields from input.

        :param analyzer_id: The unique identifier of the analyzer. Required.
        :type analyzer_id: str
        :param body: JSON body. Required.
        :type body: JSON
        :keyword processing_location: The location where the data may be processed. Defaults to
         global. Known values are: "geography", "dataZone", and "global". Default value is None.
        :paramtype processing_location: str or ~azure.ai.contentunderstanding.models.ProcessingLocation
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AnalyzeLROPoller that returns AnalyzeResult. The AnalyzeResult is
         compatible with MutableMapping. The poller includes an .operation_id property.
        :rtype: ~azure.ai.contentunderstanding.models.AnalyzeLROPoller[~azure.ai.contentunderstanding.models.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. note::
           The string_encoding parameter is automatically set to "codePoint" for Python as it
           matches Python's native string indexing behavior (len() and str[i] use code points).
           This ensures ContentSpan offsets work correctly with Python string slicing.
        """

    @overload  # type: ignore[override]
    def begin_analyze(
        self,
        analyzer_id: str,
        body: IO[bytes],
        *,
        processing_location: Optional[Union[str, _models.ProcessingLocation]] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> "AnalyzeLROPoller[_models.AnalyzeResult]":  # pyright: ignore[reportInvalidTypeArguments]
        """Extract content and fields from input.

        :param analyzer_id: The unique identifier of the analyzer. Required.
        :type analyzer_id: str
        :param body: Binary stream body. Required.
        :type body: IO[bytes]
        :keyword processing_location: The location where the data may be processed. Defaults to
         global. Known values are: "geography", "dataZone", and "global". Default value is None.
        :paramtype processing_location: str or ~azure.ai.contentunderstanding.models.ProcessingLocation
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: An instance of AnalyzeLROPoller that returns AnalyzeResult. The AnalyzeResult is
         compatible with MutableMapping. The poller includes an .operation_id property.
        :rtype: ~azure.ai.contentunderstanding.models.AnalyzeLROPoller[~azure.ai.contentunderstanding.models.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. note::
           The string_encoding parameter is automatically set to "codePoint" for Python as it
           matches Python's native string indexing behavior (len() and str[i] use code points).
           This ensures ContentSpan offsets work correctly with Python string slicing.
        """

    @distributed_trace
    def begin_analyze(  # type: ignore[override]  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        analyzer_id: str,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        processing_location: Optional[Union[str, _models.ProcessingLocation]] = None,
        content_type: Optional[str] = None,
        inputs: Optional[list[_models.AnalyzeInput]] = None,
        model_deployments: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> "AnalyzeLROPoller[_models.AnalyzeResult]":  # pyright: ignore[reportInvalidTypeArguments]
        """Extract content and fields from input.

        :param analyzer_id: The unique identifier of the analyzer. Required.
        :type analyzer_id: str
        :param body: Is either a JSON type or a IO[bytes] type. Default value is None.
        :type body: JSON or IO[bytes]
        :keyword processing_location: The location where the data may be processed. Defaults to
         global. Known values are: "geography", "dataZone", and "global". Default value is None.
        :paramtype processing_location: str or ~azure.ai.contentunderstanding.models.ProcessingLocation
        :keyword content_type: Body Parameter content-type. Default value is "application/json".
        :paramtype content_type: str
        :keyword inputs: Inputs to analyze. Currently, only pro mode supports multiple inputs.
         Default value is None.
        :paramtype inputs: list[~azure.ai.contentunderstanding.models.AnalyzeInput]
        :keyword model_deployments: Override default mapping of model names to deployments.
         Ex. { "gpt-4.1": "myGpt41Deployment", "text-embedding-3-large":
         "myTextEmbedding3LargeDeployment" }. Default value is None.
        :paramtype model_deployments: dict[str, str]
        :return: An instance of AnalyzeLROPoller that returns AnalyzeResult. The AnalyzeResult is
         compatible with MutableMapping. The poller includes an .operation_id property.
        :rtype: ~azure.ai.contentunderstanding.models.AnalyzeLROPoller[~azure.ai.contentunderstanding.models.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. note::
           The string_encoding parameter is automatically set to "codePoint" for Python as it
           matches Python's native string indexing behavior (len() and str[i] use code points).
           This ensures ContentSpan offsets work correctly with Python string slicing.
        """
        # Set string_encoding to "codePoint" (matches Python's string indexing)
        kwargs["string_encoding"] = "codePoint"

        # Call parent implementation
        # Only pass body if it's not _Unset (let parent construct from inputs if not provided)
        # Ensure content_type is always a string (not None)
        content_type_str: str = content_type if content_type is not None else "application/json"
        if body is not _Unset:
            poller = super().begin_analyze(  # pyright: ignore[reportCallIssue]
                analyzer_id=analyzer_id,
                body=body,
                processing_location=processing_location,
                content_type=content_type_str,
                inputs=inputs,
                model_deployments=model_deployments,
                **kwargs,
            )
        else:
            poller = super().begin_analyze(  # pyright: ignore[reportCallIssue]
                analyzer_id=analyzer_id,
                processing_location=processing_location,
                content_type=content_type_str,
                inputs=inputs,
                model_deployments=model_deployments,
                **kwargs,
            )

        # Wrap in custom poller with .operation_id property (without re-initializing)
        return AnalyzeLROPoller.from_poller(poller)  # pyright: ignore[reportReturnType]

    @distributed_trace
    def begin_analyze_binary(
        self,
        analyzer_id: str,
        binary_input: bytes,
        *,
        processing_location: Optional[Union[str, _models.ProcessingLocation]] = None,
        input_range: Optional[str] = None,
        content_type: str = "application/octet-stream",
        **kwargs: Any,
    ) -> "AnalyzeLROPoller[_models.AnalyzeResult]":  # pyright: ignore[reportInvalidTypeArguments]
        """Extract content and fields from input.

        :param analyzer_id: The unique identifier of the analyzer. Required.
        :type analyzer_id: str
        :param binary_input: The binary content of the document to analyze. Required.
        :type binary_input: bytes
        :keyword processing_location: The location where the data may be processed. Defaults to
         global. Known values are: "geography", "dataZone", and "global". Default value is None.
        :paramtype processing_location: str or ~azure.ai.contentunderstanding.models.ProcessingLocation
        :keyword input_range: Range of the input to analyze (ex. ``1-3,5,9-``). Document content uses
         1-based page numbers, while audio visual content uses integer milliseconds. Default value is None.
        :paramtype input_range: str
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/octet-stream".
        :paramtype content_type: str
        :return: An instance of AnalyzeLROPoller that returns AnalyzeResult. The AnalyzeResult is
         compatible with MutableMapping. The poller includes an .operation_id property.
        :rtype: ~azure.ai.contentunderstanding.models.AnalyzeLROPoller[~azure.ai.contentunderstanding.models.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. note::
           The string_encoding parameter is automatically set to "codePoint" for Python as it
           matches Python's native string indexing behavior (len() and str[i] use code points).
           This ensures ContentSpan offsets work correctly with Python string slicing.
        """
        # Set string_encoding to "codePoint" (matches Python's string indexing)
        kwargs["string_encoding"] = "codePoint"

        # Call parent implementation
        poller = super().begin_analyze_binary(
            analyzer_id=analyzer_id,
            binary_input=binary_input,
            processing_location=processing_location,
            input_range=input_range,
            content_type=content_type,
            **kwargs,
        )

        # Wrap in custom poller with .operation_id property (without re-initializing)
        return AnalyzeLROPoller.from_poller(poller)  # pyright: ignore[reportReturnType]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
