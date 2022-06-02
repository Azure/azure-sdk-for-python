# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Any, TYPE_CHECKING
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy
from ._client import MonitorIngestionClient as GeneratedClient

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential

class LogsIngestionClient(GeneratedClient):
    """Azure Monitor Data Collection Python Client.

    :param endpoint: The Data Collection Endpoint for the Data Collection Rule, for example
     https://dce-name.eastus-2.ingest.monitor.azure.com.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword api_version: Api Version. Default value is "2021-11-01-preview". Note that overriding
     this default value may result in unsupported behavior.
    :paramtype api_version: str
    """
    def __init__(self, endpoint: str, credential: "AsyncTokenCredential", **kwargs: Any) -> None:
        scope = 'https://monitor.azure.com//.default'
        super().__init__(
            endpoint, credential,
            authentication_policy=AsyncBearerTokenCredentialPolicy(credential, scope),
            **kwargs)

__all__: List[str] = ["LogsIngestionClient"]  # Add all objects you want publicly available to users at this package level

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
