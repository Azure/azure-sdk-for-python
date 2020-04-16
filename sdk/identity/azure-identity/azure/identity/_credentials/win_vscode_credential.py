# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import json
import ctypes as ct
from .._exceptions import CredentialUnavailableError
from .._constants import (
    VSCODE_CREDENTIALS_SECTION,
    AZURE_VSCODE_CLIENT_ID,
)
from .._internal.aad_client import AadClient
try:
    import ctypes.wintypes as wt
except (IOError, ValueError):
    pass

SUPPORTED_CREDKEYS = set((
    'Type', 'TargetName', 'Persist',
    'UserName', 'Comment', 'CredentialBlob'))


class _CREDENTIAL(ct.Structure):
    _fields_ = [
        ("Flags", wt.DWORD),
        ("Type", wt.DWORD),
        ("TargetName", ct.c_wchar_p),
        ("Comment", ct.c_wchar_p),
        ("LastWritten", wt.FILETIME),
        ("CredentialBlobSize", wt.DWORD),
        ("CredentialBlob", wt.LPBYTE),
        ("Persist", wt.DWORD),
        ("AttributeCount", wt.DWORD),
        ("Attributes", ct.c_void_p),
        ("TargetAlias", ct.c_wchar_p),
        ("UserName", ct.c_wchar_p)]

    @classmethod
    def from_dict(cls, credential):
        # pylint:disable=attribute-defined-outside-init
        creds = cls()
        pcreds = _PCREDENTIAL(creds)

        ct.memset(pcreds, 0, ct.sizeof(creds))

        for key in SUPPORTED_CREDKEYS:
            if key in credential:
                if key != 'CredentialBlob':
                    setattr(creds, key, credential[key])
                else:
                    blob = credential['CredentialBlob']
                    blob_data = ct.create_unicode_buffer(blob)
                    creds.CredentialBlobSize = \
                        ct.sizeof(blob_data) - \
                        ct.sizeof(ct.c_wchar)
                    creds.CredentialBlob = ct.cast(blob_data, wt.LPBYTE)
        return creds


_PCREDENTIAL = ct.POINTER(_CREDENTIAL)


_advapi = ct.WinDLL('advapi32')
_advapi.CredWriteW.argtypes = [_PCREDENTIAL, wt.DWORD]
_advapi.CredWriteW.restype = wt.BOOL
_advapi.CredReadW.argtypes = [wt.LPCWSTR, wt.DWORD, wt.DWORD, ct.POINTER(_PCREDENTIAL)]
_advapi.CredReadW.restype = wt.BOOL
_advapi.CredFree.argtypes = [_PCREDENTIAL]
_advapi.CredDeleteW.restype = wt.BOOL
_advapi.CredDeleteW.argtypes = [wt.LPCWSTR, wt.DWORD, wt.DWORD]


def _cred_write(credential):
    creds = _CREDENTIAL.from_dict(credential)
    cred_ptr = _PCREDENTIAL(creds)
    _advapi.CredWriteW(cred_ptr, 0)


def _cred_delete(service_name, account_name):
    target = u"{}/{}".format(service_name, account_name)
    _advapi.CredDeleteW(target, 1, 0)


def _read_credential(service_name, account_name):
    target = u"{}/{}".format(service_name, account_name)
    cred_ptr = _PCREDENTIAL()
    if _advapi.CredReadW(target, 1, 0, ct.byref(cred_ptr)):
        cred_blob = cred_ptr.contents.CredentialBlob
        cred_blob_size = cred_ptr.contents.CredentialBlobSize
        password_as_list = [int.from_bytes(cred_blob[pos:pos + 2], 'little')
                            for pos in range(0, cred_blob_size, 2)]
        cred = ''.join(map(chr, password_as_list))
        _advapi.CredFree(cred_ptr)
        return cred
    return None


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
