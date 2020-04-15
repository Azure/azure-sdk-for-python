# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import json
from .._exceptions import CredentialUnavailableError
from .._constants import (
    VSCODE_CREDENTIALS_SECTION,
    AZURE_VSCODE_CLIENT_ID,
)
from .._internal.aad_client import AadClient
try:
    from win32cred import CredRead
except ImportError:
    pass

def _read_credential(service_name, account_name):
    target = u"{}/{}".format(service_name, account_name)
    res = CredRead(TargetName=target, Type=0x1)
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
    except IOError:
        return "Azure"

class WinVSCodeCredential(object):
    """Authenticates by redeeming a refresh token previously saved by VS Code

        """
    def __init__(self, **kwargs):
        self._client = kwargs.pop("client", None) or AadClient("organizations", AZURE_VSCODE_CLIENT_ID, **kwargs)

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
        refresh_token = _read_credential(VSCODE_CREDENTIALS_SECTION, environment_name)
        if not refresh_token:
            raise CredentialUnavailableError(
                message="No token available."
            )
        token = self._client.obtain_token_by_refresh_token(refresh_token, scopes, **kwargs)
        return token
