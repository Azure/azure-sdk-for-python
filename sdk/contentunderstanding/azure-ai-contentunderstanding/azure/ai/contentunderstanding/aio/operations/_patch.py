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
from typing import Any
from azure.core.polling import AsyncLROPoller
from ... import models as _models

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


class AnalyzeAsyncLROPoller(AsyncLROPoller[_models.AnalyzeResult]):
    """Custom AsyncLROPoller for Content Understanding analyze operations with details property."""

    @property
    def details(self) -> dict[str, Any]:
        """Get operation details including operation ID.

        :return: Dictionary containing operation details
        :rtype: dict[str, Any]
        :raises ValueError: If operation details cannot be extracted
        """
        try:
            initial_response = self._polling_method._initial_response  # type: ignore[attr-defined]  # pylint: disable=protected-access
            operation_location = initial_response.http_response.headers.get("Operation-Location")
            if not operation_location:
                raise ValueError("No Operation-Location header found in initial response")

            operation_id = _parse_operation_id(operation_location)
            return {
                "operation_id": operation_id,
            }
        except Exception as e:
            raise ValueError(f"Could not extract operation details: {e}") from e

    @classmethod
    async def from_continuation_token(
        cls, polling_method: Any, continuation_token: str, **kwargs: Any
    ) -> "AnalyzeAsyncLROPoller":
        """Create a new poller from a continuation token.

        :param polling_method: The polling method to use
        :type polling_method: Any
        :param continuation_token: The continuation token
        :type continuation_token: str
        :return: A new AnalyzeAsyncLROPoller instance
        :rtype: AnalyzeAsyncLROPoller
        """
        client, initial_response, deserialization_callback = await polling_method.from_continuation_token(
            continuation_token, **kwargs
        )
        return cls(client, initial_response, deserialization_callback, polling_method)


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize

    :return: None
    :rtype: None
    """


