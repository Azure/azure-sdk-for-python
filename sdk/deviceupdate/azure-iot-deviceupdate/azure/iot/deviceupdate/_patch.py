# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any

from azure.core.credentials import TokenCredential
from azure.core.rest import HttpRequest, HttpResponse


__all__: list[str] = []


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
    from ._client import DeviceUpdateClient

    generated_init = DeviceUpdateClient.__init__
    generated_send_request = DeviceUpdateClient.send_request

    def __init__(self, endpoint: str, instance_id: str, credential: TokenCredential, **kwargs: Any) -> None:
        generated_init(self, endpoint=endpoint, credential=credential, instance_id=instance_id, **kwargs)

    def send_request(self, request: HttpRequest, **kwargs: Any) -> HttpResponse:
        return generated_send_request(self, request, **kwargs)

    setattr(DeviceUpdateClient, "__init__", __init__)
    setattr(DeviceUpdateClient, "send_request", send_request)
