# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from ._access_control_client import KeyVaultAccessControlClient
from ._backup_client import KeyVaultBackupClient
from ._settings_client import KeyVaultSettingsClient

__all__ = ["KeyVaultAccessControlClient", "KeyVaultBackupClient", "KeyVaultSettingsClient"]
