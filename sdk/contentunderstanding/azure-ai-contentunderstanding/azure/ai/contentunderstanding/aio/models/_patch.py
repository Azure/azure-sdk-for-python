# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import re
from typing import Any, TypeVar
from azure.core.polling import AsyncLROPoller, AsyncPollingMethod

PollingReturnType_co = TypeVar("PollingReturnType_co", covariant=True)

__all__ = ["AnalyzeAsyncLROPoller"]


def _parse_operation_id(operation_location_header: str) -> str:
    """Parse operation ID from Operation-Location header for analyze operations.

    :param operation_location_header: The Operation-Location header value
    :type operation_location_header: str
    :return: The extracted operation ID
    :rtype: str
    :raises ValueError: If operation ID cannot be extracted
    """
    # Pattern: https://endpoint/.../analyzerResults/{operation_id}?api-version=...
    regex = r".*/analyzerResults/([^?/]+)"

    match = re.search(regex, operation_location_header)
    if not match:
        raise ValueError(f"Could not extract operation ID from: {operation_location_header}")

    return match.group(1)


class AnalyzeAsyncLROPoller(AsyncLROPoller[PollingReturnType_co]):
    """Custom AsyncLROPoller for Content Understanding analyze operations.

    Provides access to the operation ID for tracking and diagnostics.
    """

    @property
    def operation_id(self) -> str:
        """Returns the operation ID for this long-running operation.

        The operation ID can be used with get_result_file() to retrieve
        intermediate or final result files from the service.

        :return: The operation ID
        :rtype: str
        :raises ValueError: If the operation ID cannot be extracted
        """
        try:
            operation_location = self.polling_method()._initial_response.http_response.headers["Operation-Location"]  # type: ignore # pylint: disable=protected-access
            return _parse_operation_id(operation_location)
        except (KeyError, ValueError) as e:
            raise ValueError(f"Could not extract operation ID: {str(e)}") from e

    @classmethod
    def from_poller(cls, poller: AsyncLROPoller[PollingReturnType_co]) -> "AnalyzeAsyncLROPoller":
        """Wrap an existing AsyncLROPoller without re-initializing the polling method.

        This avoids duplicate HTTP requests that would occur if we created a new
        AsyncLROPoller instance (which calls polling_method.initialize() again).

        :param poller: The existing AsyncLROPoller to wrap
        :type poller: ~azure.core.polling.AsyncLROPoller
        :return: An AnalyzeAsyncLROPoller wrapping the same polling state
        :rtype: AnalyzeAsyncLROPoller
        """
        # Create instance without calling __init__ to avoid re-initialization
        instance: AnalyzeAsyncLROPoller = object.__new__(cls)
        # Copy all attributes from the original poller
        instance.__dict__.update(poller.__dict__)
        return instance

    @classmethod
    async def from_continuation_token(  # type: ignore[override]  # pylint: disable=invalid-overridden-method
        cls,
        polling_method: AsyncPollingMethod[PollingReturnType_co],
        continuation_token: str,
        **kwargs: Any,
    ) -> AsyncLROPoller[PollingReturnType_co]:
        """Create a poller from a continuation token.

        :param polling_method: The polling strategy to adopt
        :type polling_method: ~azure.core.polling.AsyncPollingMethod
        :param continuation_token: An opaque continuation token
        :type continuation_token: str
        :return: An instance of AnalyzeAsyncLROPoller
        :rtype: AsyncLROPoller[PollingReturnType_co]
        :raises ~azure.core.exceptions.HttpResponseError: If the continuation token is invalid.
        """
        result = await polling_method.from_continuation_token(continuation_token, **kwargs)  # type: ignore[misc]
        (
            client,
            initial_response,
            deserialization_callback,
        ) = result

        return cls(client, initial_response, deserialization_callback, polling_method)


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize

    :return: None
    :rtype: None
    """
