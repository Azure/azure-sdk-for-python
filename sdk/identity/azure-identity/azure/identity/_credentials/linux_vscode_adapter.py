# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import json
import ctypes as ct
from .._constants import VSCODE_CREDENTIALS_SECTION


def _c_str(string):
    return ct.c_char_p(string.encode('utf-8'))


try:
    _libsecret = ct.cdll.LoadLibrary('libsecret-1.so.0')
    _libsecret.secret_schema_new.argtypes = \
        [ct.c_char_p, ct.c_uint, ct.c_char_p, ct.c_uint, ct.c_char_p, ct.c_uint, ct.c_void_p]
    _libsecret.secret_password_lookup_sync.argtypes = \
        [ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_char_p, ct.c_char_p, ct.c_char_p, ct.c_char_p, ct.c_void_p]
except OSError:
    _libsecret = None


def _get_user_settings_path():
    app_data_folder = os.environ['HOME']
    return os.path.join(app_data_folder, ".config", "Code", "User", "settings.json")


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
    if not _libsecret:
        return None
    schema = _libsecret.secret_schema_new(_c_str("org.freedesktop.Secret.Generic"), 2,
                                          _c_str("service"), 0, _c_str("account"), 0, None)
    p_str = _libsecret.secret_password_lookup_sync(schema, None, None, _c_str("service"), _c_str(service_name),
                                                   _c_str("account"), _c_str(account_name), None)
    return ct.c_char_p(p_str).value.decode('utf-8')


def get_credentials():
    try:
        environment_name = _get_user_settings()
        credentials = _get_refresh_token(VSCODE_CREDENTIALS_SECTION, environment_name)
        return credentials
    except Exception: #pylint: disable=broad-except
        return None
