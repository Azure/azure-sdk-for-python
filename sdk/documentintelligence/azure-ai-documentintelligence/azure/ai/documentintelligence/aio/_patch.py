# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, List, Union

from azure.core.credentials import AzureKeyCredential, TokenCredential

from ._client import(
    DocumentIntelligenceClient as GeneratedDocumentIntelligenceClient,
    DocumentIntelligenceAdministrationClient as GeneratedDocumentIntelligenceAdministrationClient,
)


class DocumentIntelligenceClient(GeneratedDocumentIntelligenceClient):
    __doc__ = GeneratedDocumentIntelligenceClient.__doc__

    def __init__(self, endpoint: str, credential: Union[AzureKeyCredential, TokenCredential], **kwargs: Any) -> None:
        # The default polling interval should be 5 seconds.
        polling_interval = kwargs.pop("polling_interval", 5)
        super().__init__(
            endpoint=endpoint,
            credential=credential,
            polling_interval=polling_interval,
            **kwargs,
        )


class DocumentIntelligenceAdministrationClient(GeneratedDocumentIntelligenceAdministrationClient):
    __doc__ = GeneratedDocumentIntelligenceAdministrationClient.__doc__

    def __init__(self, endpoint: str, credential: Union[AzureKeyCredential, TokenCredential], **kwargs: Any) -> None:
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
