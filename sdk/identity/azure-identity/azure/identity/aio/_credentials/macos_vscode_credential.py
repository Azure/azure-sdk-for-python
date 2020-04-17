# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING
import asyncio
from ..._exceptions import CredentialUnavailableError
from .._credentials.base import AsyncCredentialBase
from ..._constants import (
    VSCODE_CREDENTIALS_SECTION,
    AZURE_VSCODE_CLIENT_ID,
)
from .._internal.aad_client import AadClient
from ..._credentials.macos_vscode_credential import _get_user_settings, _get_refresh_token
if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Iterable, Optional
    from azure.core.credentials import AccessToken


class MacOSVSCodeCredential(AsyncCredentialBase):
    """Authenticates by redeeming a refresh token previously saved by VS Code

            """
    def __init__(self, **kwargs):
        self._client = kwargs.pop("_client", None) or AadClient("organizations", AZURE_VSCODE_CLIENT_ID, **kwargs)

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

        The first time this method is called, the credential will redeem its authorization code. On subsequent calls
        the credential will return a cached access token or redeem a refresh token, if it acquired a refresh token upon
        redeeming the authorization code.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises ~azure.identity.CredentialUnavailableError: fail to get refresh token.
        """
        if not scopes:
            raise ValueError("'get_token' requires at least one scope")

        environment_name = _get_user_settings()
        refresh_token = _get_refresh_token(VSCODE_CREDENTIALS_SECTION, environment_name)
        if not refresh_token:
            raise CredentialUnavailableError(
                message="No Azure user is logged in to Visual Studio Code."
            )
        token = await self._client.obtain_token_by_refresh_token(
            refresh_token, scopes, **kwargs)
        return token
