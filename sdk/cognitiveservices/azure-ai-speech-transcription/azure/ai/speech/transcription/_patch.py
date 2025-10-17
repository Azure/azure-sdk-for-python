# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from copy import deepcopy
from typing import Any

from . import _client


__all__: list[str] = []  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

    def _patched_send_request(self, request, *, stream: bool = False, **kwargs: Any):
        """Prevent the service endpoint from being URL-encoded twice.

        :param request: The network request you want to make.
        :type request: ~azure.core.rest.HttpRequest
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call. Does not do error handling on your response.
        :rtype: ~azure.core.rest.HttpResponse
        """
        request_copy = deepcopy(request)
        path_format_arguments = {
            "endpoint": self._config.endpoint.rstrip("/"),  # pylint: disable=protected-access
        }
        request_copy.url = self._client.format_url(
            request_copy.url, **path_format_arguments
        )  # pylint: disable=protected-access
        return self._client.send_request(request_copy, stream=stream, **kwargs)  # type: ignore[no-any-return] # pylint: disable=protected-access

    # Only patch once even if patch_sdk is invoked multiple times
    if getattr(_client.TranscriptionClient.send_request, "__patched_endpoint_fix__", False) is not True:
        _patched_send_request.__patched_endpoint_fix__ = True  # type: ignore[attr-defined]
        _client.TranscriptionClient.send_request = _patched_send_request
