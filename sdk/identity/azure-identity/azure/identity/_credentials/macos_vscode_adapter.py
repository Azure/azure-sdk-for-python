# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import json
from msal_extensions.osx import Keychain, KeychainError
from .._constants import VSCODE_CREDENTIALS_SECTION


def _get_user_settings_path():
    app_data_folder = os.environ["USER"]
    return os.path.join(app_data_folder, "Library", "Application Support", "Code", "User", "settings.json")


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
    key_chain = Keychain()
    try:
        return key_chain.get_generic_password(service_name, account_name)
    except KeychainError:
        return None


def get_credentials():
    try:
        environment_name = _get_user_settings()
        credentials = _get_refresh_token(VSCODE_CREDENTIALS_SECTION, environment_name)
        return credentials
    except Exception:  # pylint: disable=broad-except
        return None
