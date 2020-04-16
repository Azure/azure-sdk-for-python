# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import gi  # https://pygobject.readthedocs.io/en/latest/getting_started.html
# pylint: disable=no-name-in-module
gi.require_version("Secret", "1")  # Would require a package gir1.2-secret-1
# pylint: disable=wrong-import-position
from gi.repository import Secret  # Would require a package gir1.2-secret-1
from ..._exceptions import CredentialUnavailableError
from .._credentials.base import AsyncCredentialBase
from ..._constants import (
    VSCODE_CREDENTIALS_SECTION,
    AZURE_VSCODE_CLIENT_ID,
)
from .._internal.aad_client import AadClient
try:
    from ..._credentials.linux_vscode_credential import _get_user_settings
except ImportError:
    pass


class LinuxVSCodeCredential(AsyncCredentialBase):
    def __init__(self, **kwargs):
        self._client = kwargs.pop("client", None) or AadClient("organizations", AZURE_VSCODE_CLIENT_ID, **kwargs)
        self._schema = Secret.Schema.new("org.freedesktop.Secret.Generic", Secret.SchemaFlags.NONE, {
            "service": Secret.SchemaAttributeType.STRING,
            "account": Secret.SchemaAttributeType.STRING})

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
        refresh_token = Secret.password_lookup_sync(self._schema, {"service": VSCODE_CREDENTIALS_SECTION,
                                                                   "account": environment_name})
        if not refresh_token:
            raise CredentialUnavailableError(
                message="No Azure user is logged in to Visual Studio Code."
            )
        loop = kwargs.pop("loop", None) or asyncio.get_event_loop()
        token = await self._client.obtain_token_by_refresh_token(
            refresh_token, scopes, loop=loop, **kwargs)
        return token
