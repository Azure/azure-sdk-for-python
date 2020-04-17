# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import json
from typing import TYPE_CHECKING
# pylint:disable=import-error
import gi  # https://pygobject.readthedocs.io/en/latest/getting_started.html
# pylint: disable=no-name-in-module
gi.require_version("Secret", "1")  # Would require a package gir1.2-secret-1
# pylint: disable=wrong-import-position
from gi.repository import Secret  # Would require a package gir1.2-secret-1
from .._exceptions import CredentialUnavailableError
from .._constants import (
    VSCODE_CREDENTIALS_SECTION,
    AZURE_VSCODE_CLIENT_ID,
)
from .._internal.aad_client import AadClient

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Iterable, Optional
    from azure.core.credentials import AccessToken

_SECRET = Secret.Schema.new("org.freedesktop.Secret.Generic", Secret.SchemaFlags.NONE, {
    "service": Secret.SchemaAttributeType.STRING,
    "account": Secret.SchemaAttributeType.STRING})

def _get_user_settings_path():
    app_data_folder = os.environ['APPDATA']
    return os.path.join(app_data_folder, "Code", "User", "settings.json")


def _get_user_settings():
    path = _get_user_settings_path()
    try:
        with open(path) as file:
            data = json.load(file)
            environment_name = data.get("azure.cloud", "Azure")
            return environment_name
    except IOError:
        return "Azure"


def _get_refresh_token(service_name, account_name):
    return Secret.password_lookup_sync(_SECRET, {"service": service_name,
                                                 "account": account_name})

class LinuxVSCodeCredential(object):
    def __init__(self, **kwargs):
        self._client = kwargs.pop("_client", None) or AadClient("organizations", AZURE_VSCODE_CLIENT_ID, **kwargs)

    def get_token(self, *scopes, **kwargs):
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
        refresh_token = _get_refresh_token(VSCODE_CREDENTIALS_SECTION, environment_name)
        if not refresh_token:
            raise CredentialUnavailableError(
                message="No Azure user is logged in to Visual Studio Code."
            )
        token = self._client.obtain_token_by_refresh_token(refresh_token, scopes, **kwargs)
        return token
