# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import json
from typing import TYPE_CHECKING
import ctypes as ct
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

def _c_str(string):
    return ct.c_char_p(string.encode('utf-8'))

_libsecret = ct.cdll.LoadLibrary('libsecret-1.so.0')
_libsecret.secret_schema_new.argtypes = \
    [ct.c_char_p, ct.c_uint, ct.c_char_p, ct.c_uint, ct.c_char_p, ct.c_uint, ct.c_void_p]
_libsecret.secret_password_lookup_sync.argtypes = \
    [ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_char_p, ct.c_char_p, ct.c_char_p, ct.c_char_p, ct.c_void_p]

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
    schema = _libsecret.secret_schema_new(_c_str("org.freedesktop.Secret.Generic"), 2,
                                          _c_str("service"), 0, _c_str("account"), 0, None)
    return _libsecret.secret_password_lookup_sync(schema, None, None, _c_str("service"), _c_str(service_name),
                                                  _c_str("account"), _c_str(account_name), None)

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
