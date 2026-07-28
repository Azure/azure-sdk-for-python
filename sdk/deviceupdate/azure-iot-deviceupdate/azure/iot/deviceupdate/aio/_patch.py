# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, List, Optional, TYPE_CHECKING

from ._client import DeviceUpdateClient as DeviceUpdateClientGenerated

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class DeviceUpdateClient(DeviceUpdateClientGenerated):
    """Device Update for IoT Hub async client.

    This override preserves the constructor parameter order shipped in 1.0.0
    (``endpoint``, ``instance_id``, ``credential``). The TypeSpec-generated client
    orders the hoisted ``instance_id`` after ``credential``; restoring the original
    order here avoids a breaking change for existing callers.

    :param endpoint: The Device Update for IoT Hub account endpoint. Required.
    :type endpoint: str
    :param instance_id: The Device Update for IoT Hub account instance identifier. Required.
    :type instance_id: str
    :param credential: Credential used to authenticate requests to the service. Required.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :keyword api_version: The API version to use for this operation. Default value is "2026-06-01".
     Note that overriding this default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(
        self,
        endpoint: str,
        instance_id: str,
        credential: "AsyncTokenCredential",
        *,
        api_version: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        if api_version is not None:
            kwargs["api_version"] = api_version
        super().__init__(endpoint=endpoint, credential=credential, instance_id=instance_id, **kwargs)


__all__: List[str] = ["DeviceUpdateClient"]  # Add all objects you want publicly available at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
