# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, TYPE_CHECKING, Any
from enum import Enum
from azure.core.pipeline.policies import BearerTokenCredentialPolicy
from ._client import MonitorIngestionClient as GeneratedClient

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

class SendLogsStatus(str, Enum):
    SUCCESS = 'Success'
    PARTIAL_FAILURE = 'PartialFailure'

class SendLogsResult():
    """The response for send_logs API.

    :ivar SendLogsStatus status: Inditcates if the result is a success or a partial failure.
    :ivar list failed_logs_index: If there is a failure, returns the index of the request.
    """
    def __init__(self, **kwargs):
        self.status: SendLogsStatus = kwargs.get("status", None)
        self.failed_logs_index: List[int] = kwargs.get('failed_logs_index', None)

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
    def __init__(self, endpoint: str, credential: "TokenCredential", **kwargs: Any) -> None:
        scope = 'https://monitor.azure.com//.default'
        super().__init__(
            endpoint, credential,
            authentication_policy=BearerTokenCredentialPolicy(credential, scope),
            **kwargs)

__all__ = ['LogsIngestionClient', 'SendLogsStatus', 'SendLogsResult']

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
