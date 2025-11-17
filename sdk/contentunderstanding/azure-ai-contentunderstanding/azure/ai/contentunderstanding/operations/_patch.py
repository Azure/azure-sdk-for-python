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
from typing import Any, Mapping, TypeVar
from azure.core.polling import LROPoller, PollingMethod

PollingReturnType_co = TypeVar("PollingReturnType_co", covariant=True)

__all__ = ["AnalyzeLROPoller"]


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


class AnalyzeLROPoller(LROPoller[PollingReturnType_co]):
    """Custom LROPoller for Content Understanding analyze operations.

    Provides access to operation details including the operation ID.
    """

    @property
    def details(self) -> Mapping[str, Any]:
        """Returns metadata associated with the long-running operation.

        :return: Returns metadata associated with the long-running operation.
        :rtype: Mapping[str, Any]
        """
        try:
            operation_location = self.polling_method()._initial_response.http_response.headers["Operation-Location"]  # type: ignore # pylint: disable=protected-access
            operation_id = _parse_operation_id(operation_location)
            return {"operation_id": operation_id, "operation_type": "analyze"}
        except (KeyError, ValueError) as e:
            return {
                "operation_id": None,
                "operation_type": "analyze",
                "error": f"Could not extract operation details: {str(e)}",
            }

    @classmethod
    def from_continuation_token(
        cls, polling_method: PollingMethod[PollingReturnType_co], continuation_token: str, **kwargs: Any
    ) -> "AnalyzeLROPoller":
        """Create a poller from a continuation token.

        :param polling_method: The polling strategy to adopt
        :type polling_method: ~azure.core.polling.PollingMethod
        :param continuation_token: An opaque continuation token
        :type continuation_token: str
        :return: An instance of AnalyzeLROPoller
        :rtype: AnalyzeLROPoller
        :raises ~azure.core.exceptions.HttpResponseError: If the continuation token is invalid.
        """
        (
            client,
            initial_response,
            deserialization_callback,
        ) = polling_method.from_continuation_token(continuation_token, **kwargs)

        return cls(client, initial_response, deserialization_callback, polling_method)


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize

    :return: None
    :rtype: None
    """
