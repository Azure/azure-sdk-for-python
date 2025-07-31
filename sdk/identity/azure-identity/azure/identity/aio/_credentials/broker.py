# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio  # pylint: disable=do-not-import-asyncio
from types import TracebackType
from typing import Any, Optional, Type

from azure.core.credentials import AccessToken, AccessTokenInfo
from ..._credentials.broker import BrokerCredential as SyncBrokerCredential
from .._internal import AsyncContextManager


class BrokerCredential(AsyncContextManager):
    """An async broker credential that wraps the synchronous BrokerCredential.

    This credential wraps the synchronous BrokerCredential and provides an async interface.
    It handles prerequisite checking and falls back appropriately through the sync credential.
    """

    def __init__(self, **kwargs: Any) -> None:
        self._sync_credential = SyncBrokerCredential(**kwargs)

    async def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:
        """Asynchronously request an access token for `scopes`.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
            For more information about scopes, see
            https://learn.microsoft.com/entra/identity-platform/scopes-oidc.

        :return: An access token with the desired scopes.
        :rtype: ~azure.core.credentials.AccessToken

        :raises CredentialUnavailableError: when the broker credential is unavailable
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self._sync_credential.get_token(*scopes, **kwargs))

    async def get_token_info(self, *scopes: str, **kwargs: Any) -> AccessTokenInfo:
        """Asynchronously request an access token for `scopes`.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
            For more information about scopes, see
            https://learn.microsoft.com/entra/identity-platform/scopes-oidc.

        :return: An AccessTokenInfo instance with information about the token.
        :rtype: ~azure.core.credentials.AccessTokenInfo

        :raises CredentialUnavailableError: when the broker credential is unavailable
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self._sync_credential.get_token_info(*scopes, **kwargs))

    async def __aenter__(self) -> "BrokerCredential":
        await asyncio.get_event_loop().run_in_executor(None, self._sync_credential.__enter__)
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        await asyncio.get_event_loop().run_in_executor(
            None, lambda: self._sync_credential.__exit__(exc_type, exc_value, traceback)
        )

    async def close(self) -> None:
        """Close the credential's transport session."""
        await asyncio.get_event_loop().run_in_executor(None, self._sync_credential.close)
