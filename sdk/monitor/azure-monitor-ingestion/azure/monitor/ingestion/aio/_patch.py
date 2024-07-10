# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
from ._client import LogsIngestionClient as GeneratedClient


class LogsIngestionClient(GeneratedClient):
    """The asynchronous client for uploading logs to Azure Monitor.

    :param endpoint: The Data Collection Endpoint for the Data Collection Rule, for example
     https://dce-name.eastus-2.ingest.monitor.azure.com.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :keyword api_version: Api Version. Default value is "2023-01-01". Note that overriding
     this default value may result in unsupported behavior.
    :paramtype api_version: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/async_samples/sample_authentication_async.py
            :start-after: [START create_client_public_cloud_async]
            :end-before: [END create_client_public_cloud_async]
            :language: python
            :dedent: 4
            :caption: Creating the LogsIngestionClient with DefaultAzureCredential.

    .. admonition:: Example:

       .. literalinclude:: ../samples/async_samples/sample_authentication_async.py
            :start-after: [START create_client_sovereign_cloud_async]
            :end-before: [END create_client_sovereign_cloud_async]
            :language: python
            :dedent: 4
            :caption: Creating the LogsIngestionClient for use with a sovereign cloud (i.e. non-public cloud).
    """


__all__: List[str] = ["LogsIngestionClient"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
