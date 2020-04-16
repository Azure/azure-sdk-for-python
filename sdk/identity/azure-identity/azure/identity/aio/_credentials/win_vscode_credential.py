# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
from ..._exceptions import CredentialUnavailableError
from .._credentials.base import AsyncCredentialBase
from ..._constants import (
    VSCODE_CREDENTIALS_SECTION,
    AZURE_VSCODE_CLIENT_ID,
)
from .._internal.aad_client import AadClient
try:
    from ..._credentials.win_vscode_credential import _read_credential, _get_user_settings
except ImportError:
    pass


class WinVSCodeCredential(AsyncCredentialBase):
    """Authenticates by redeeming a refresh token previously saved by VS Code

        """
    def __init__(self, **kwargs):
        self._client = kwargs.pop("client", None) or AadClient("organizations", AZURE_VSCODE_CLIENT_ID, **kwargs)

    async def __aenter__(self):
        if self._client:
            await self._client.__aenter__()
        return self

    async def close(self):
        """Close the credential's transport session."""

        if self._client:
            await self._client.__aexit__()

    async def get_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        """Request an access token for `scopes`.

        .. note:: This method is called by Azure SDK clients. It isn't intended for use in application code.

        When this method is called, the credential will try to get the refresh token saved by VS Code. If a refresh
        token can be found, it will redeem the refresh token for an access token and return the access token.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises ~azure.identity.CredentialUnavailableError: fail to get refresh token.
        """
        if not scopes:
            raise ValueError("'get_token' requires at least one scope")

        environment_name = _get_user_settings()
        refresh_token = _read_credential(VSCODE_CREDENTIALS_SECTION, environment_name)
        if not refresh_token:
            raise CredentialUnavailableError(
                message="No Azure user is logged in to Visual Studio Code."
            )
        loop = kwargs.pop("loop", None) or asyncio.get_event_loop()
        token = await self._client.obtain_token_by_refresh_token(
            refresh_token, scopes, loop=loop, **kwargs)
        return token
