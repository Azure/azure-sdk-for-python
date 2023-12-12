# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, List, Optional, Union

from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential

from ._client import(
    DocumentIntelligenceClient as DIClientGenerated,
    DocumentIntelligenceAdministrationClient as DIAClientGenerated,
)


class DocumentIntelligenceClient(DIClientGenerated):  # pylint: disable=client-accepts-api-version-keyword
    __doc__ = DIClientGenerated.__doc__  # pylint: disable=client-incorrect-naming-convention # It's a bug in Pylint checker: https://github.com/Azure/azure-sdk-tools/issues/7437

    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, AsyncTokenCredential],
        *,
        polling_interval: Optional[str] = 5,  # The default polling interval should be 5 seconds
        **kwargs: Any,
    ) -> None:
        super().__init__(
            endpoint=endpoint,
            credential=credential,
            polling_interval=polling_interval,
            **kwargs,
        )


class DocumentIntelligenceAdministrationClient(DIAClientGenerated):  # pylint: disable=client-accepts-api-version-keyword
    __doc__ = DIAClientGenerated.__doc__  # pylint: disable=client-incorrect-naming-convention # It's a bug in Pylint checker: https://github.com/Azure/azure-sdk-tools/issues/7437

    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, AsyncTokenCredential],
        *,
        polling_interval: Optional[str] = 5,  # The default polling interval should be 5 seconds
        **kwargs: Any,
    ) -> None:
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
