# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from typing import TYPE_CHECKING

from .client_assertion import ClientAssertionCredential
from .._internal import AsyncContextManager
from ..._constants import EnvironmentVariables
from ..._credentials.token_exchange import TokenFileMixin

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any
    from azure.core.credentials import AccessToken


class TokenExchangeCredential(AsyncContextManager, TokenFileMixin):
    def __init__(self, **kwargs: "Any") -> None:
        super().__init__()
        self._credential = ClientAssertionCredential(
            os.environ[EnvironmentVariables.AZURE_TENANT_ID],
            os.environ[EnvironmentVariables.AZURE_CLIENT_ID],
            self.get_service_account_token,
            **kwargs
        )

    async def __aenter__(self):
        await self._credential.__aenter__()
        return self

    async def close(self) -> None:
        await self._credential.close()

    async def get_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        return await self._credential.get_token(*scopes, **kwargs)
