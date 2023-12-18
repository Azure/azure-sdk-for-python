# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, List, Union

from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential

from ._client import(
    DocumentIntelligenceClient as DIClientGenerated,
    DocumentIntelligenceAdministrationClient as DIAClientGenerated,
)


class DocumentIntelligenceClient(DIClientGenerated):  # pylint: disable=client-accepts-api-version-keyword
    """DocumentIntelligenceClient.

    :param endpoint: The Document Intelligence service endpoint. Required.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure. Is either a
     AzureKeyCredential type or a TokenCredential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials_async.AsyncTokenCredential
    :keyword api_version: The API version to use for this operation. Default value is
     "2023-10-31-preview". Note that overriding this default value may result in unsupported
     behavior.
    :paramtype api_version: str
    """

    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, AsyncTokenCredential],
        **kwargs: Any,
    ) -> None:
        # The default polling interval should be 5 seconds.
        polling_interval = kwargs.pop("polling_interval", 5)
        super().__init__(
            endpoint=endpoint,
            credential=credential,
            polling_interval=polling_interval,
            **kwargs,
        )


class DocumentIntelligenceAdministrationClient(DIAClientGenerated):  # pylint: disable=client-accepts-api-version-keyword
    """DocumentIntelligenceAdministrationClient.

    :param endpoint: The Document Intelligence service endpoint. Required.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure. Is either a
     AzureKeyCredential type or a TokenCredential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials_async.AsyncTokenCredential
    :keyword api_version: The API version to use for this operation. Default value is
     "2023-10-31-preview". Note that overriding this default value may result in unsupported
     behavior.
    :paramtype api_version: str
    """

    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, AsyncTokenCredential],
        **kwargs: Any,
    ) -> None:
        # The default polling interval should be 5 seconds.
        polling_interval = kwargs.pop("polling_interval", 5)
        super().__init__(
            endpoint=endpoint,
            credential=credential,
            polling_interval=polling_interval,
            **kwargs,
        )


__all__: List[str] = [
    "DocumentIntelligenceClient",
    "DocumentIntelligenceAdministrationClient",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
