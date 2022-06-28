# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, List, Optional

from azure.confidentialledger_identity_service.aio._client import (
    ConfidentialLedgerIdentityServiceClient as GeneratedClient,
)

__all__: List[str] = [
    "ConfidentialLedgerIdentityServiceClient"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


class ConfidentialLedgerIdentityServiceClient(GeneratedClient):
    def __init__(self, identity_service_uri: Optional[str] = None, **kwargs: Any) -> None:
        """
        :param identity_service_uri: The Identity Service URL, for example
            https://identity.confidential-ledger.core.azure.com, defaults to None. If not provided,
            "https://identity.confidential-ledger.core.azure.com" will be used.
        :type identity_service_uri: Optional[str], optional
        :keyword api_version: Api Version. Default value is "2022-05-13". Note that overriding this
        default value may result in unsupported behavior.
        :paramtype api_version: str
        """

        if not identity_service_uri:
            identity_service_uri = "https://identity.confidential-ledger.core.azure.com"

        super().__init__(identity_service_uri, **kwargs)
