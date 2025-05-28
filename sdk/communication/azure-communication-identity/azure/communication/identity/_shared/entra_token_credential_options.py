# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=C4763
from typing import Optional

from typing import List, Optional
from sdk.core.corehttp.corehttp.credentials import AsyncTokenCredential, TokenCredential


class AsyncEntraCommunicationTokenCredentialOptions:
    """Options for EntraCommunicationTokenCredential.

    :param str resource_endpoint: The Azure Communication Service resource endpoint URL,
        e.g. https://myResource.communication.azure.com.
    :param ~azure.core.credentials.AsyncTokenCredential token_credential: The Entra ID token credential.
    :param list[str] scopes: The scopes for retrieving the Entra ID access token.
    """

    def __init__(
            self,
            resource_endpoint: str,
            token_credential: AsyncTokenCredential,
            scopes: Optional[List[str]] = None,
    ) -> None:

        if not resource_endpoint:
            raise ValueError("resource_endpoint cannot be empty")
        if not token_credential:
            raise ValueError("token_credential cannot be None")

        self.resource_endpoint = resource_endpoint
        self.token_credential = token_credential
        self.scopes = scopes or ["https://communication.azure.com/clients/.default"]


class EntraCommunicationTokenCredentialOptions:
    """Options for EntraCommunicationTokenCredential (synchronous).

    :param str resource_endpoint: The Azure Communication Service resource endpoint URL,
        e.g. https://myResource.communication.azure.com.
    :param ~azure.core.credentials.TokenCredential token_credential: The Entra ID token credential.
    :param list[str] scopes: The scopes for retrieving the Entra ID access token.
    """

    def __init__(
            self,
            resource_endpoint: str,
            token_credential: TokenCredential,
            scopes: Optional[List[str]] = None,
    ) -> None:

        if not resource_endpoint:
            raise ValueError("resource_endpoint cannot be empty")
        if not token_credential:
            raise ValueError("token_credential cannot be None")

        self.resource_endpoint = resource_endpoint
        self.token_credential = token_credential
        self.scopes = scopes or ["https://communication.azure.com/clients/.default"]