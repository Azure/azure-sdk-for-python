# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Any, TYPE_CHECKING

from ._client import MetricsClient as GeneratedClient
from .._sdk_moniker import SDK_MONIKER

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


__all__: List[str] = []  # Add all objects you want publicly available to users at this package level


class MetricsClient(GeneratedClient):
    """MetricsClient should be used for performing metrics queries on multiple monitored resources in the
    same region. A credential with authorization at the subscription level is required when using this client.

    :param str endpoint: The regional endpoint to use, for example
        https://eastus.metrics.monitor.azure.com. The region should match the region of the requested
        resources. For global resources, the region should be 'global'. Required.
    :param credential: The credential to authenticate the client.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :keyword str audience: The audience to use when requesting tokens for Microsoft Entra ID. Defaults to the public
        cloud audience (https://metrics.monitor.azure.com).
    :keyword str api_version: The API version to use for this operation. Default value is "2024-02-01".
     Note that overriding this default value may result in unsupported behavior.
    """

    def __init__(self, endpoint: str, credential: "AsyncTokenCredential", **kwargs: Any) -> None:
        self._endpoint = endpoint
        if not self._endpoint.startswith("https://") and not self._endpoint.startswith("http://"):
            self._endpoint = "https://" + self._endpoint
        audience = kwargs.pop("audience", "https://metrics.monitor.azure.com")
        scope = audience.rstrip("/") + "/.default"
        credential_scopes = kwargs.pop("credential_scopes", [scope])

        kwargs.setdefault("sdk_moniker", SDK_MONIKER)
        super().__init__(endpoint=self._endpoint, credential=credential, credential_scopes=credential_scopes, **kwargs)


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
