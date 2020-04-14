# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import sys
import json
import ctypes as ct
import ctypes.wintypes as wt
import win32cred
from azure.core.exceptions import ClientAuthenticationError
from .._constants import (
    VSCODE_CREDENTIALS_SECTION,
    AZURE_VSCODE_CLIENT_ID,
    AZURE_VSCODE_TENANT_ID,
)
from .._internal.aad_client import AadClient

def _read_credential(service_name, account_name):
    target = u"{}/{}".format(service_name, account_name)
    res = win32cred.CredRead(
        TargetName=target, Type=0x1)
    cred = res["CredentialBlob"].decode('utf-16')
    return cred

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
    except: #pylint: disable=broad-except
        return "Azure"

class WinVSCodeCredential(object):
    """Authenticates by redeeming a refresh token previously saved by VS Code

        :keyword str tenant_id: ID of the application's Azure Active Directory tenant. Also called its 'directory' ID.
        :keyword str client_id: the application's client ID

        """
    def __init__(self, **kwargs):
        client_id = kwargs.pop("client_id", AZURE_VSCODE_CLIENT_ID)
        tenant_id = kwargs.pop("tenant_id", AZURE_VSCODE_TENANT_ID)
        self._client = AadClient(tenant_id, client_id, **kwargs)

    def get_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        """Request an access token for `scopes`.

        .. note:: This method is called by Azure SDK clients. It isn't intended for use in application code.

        When this method is called, the credential will try to get the refresh token saved by VS Code. If a refresh
        token can be found, it will redeem the refresh token for an access token and return the access token.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The error's ``message``
          attribute gives a reason. Any error response from Azure Active Directory is available as the error's
          ``response`` attribute.
        """
        environment_name = _get_user_settings()
        refresh_token = _read_credential(VSCODE_CREDENTIALS_SECTION, environment_name)
        if not refresh_token:
            raise ClientAuthenticationError(
                message="No token available."
            )
        token = self._client.obtain_token_by_refresh_token(refresh_token, scopes, **kwargs)
        return token
