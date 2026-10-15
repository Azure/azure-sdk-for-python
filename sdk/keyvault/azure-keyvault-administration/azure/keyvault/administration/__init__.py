# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from ._access_control_client import KeyVaultAccessControlClient
from ._backup_client import KeyVaultBackupClient
from ._ekm_client import KeyVaultEkmClient
from ._enums import (
    KeyVaultDataAction,
    KeyVaultEkmConnectivityMode,
    KeyVaultEkmPrivateEndpointConnectionStatus,
    KeyVaultEkmPrivateEndpointOperationStatus,
    KeyVaultEkmPrivateEndpointOperationType,
    KeyVaultEkmPrivateEndpointProvisioningState,
    KeyVaultRoleScope,
    KeyVaultSettingType,
)
from ._internal.client_base import ApiVersion
from ._models import (
    KeyVaultBackupResult,
    KeyVaultEkmConnection,
    KeyVaultEkmPrivateEndpoint,
    KeyVaultEkmPrivateEndpointConnectionState,
    KeyVaultEkmPrivateEndpointOperation,
    KeyVaultEkmPrivateEndpointProperties,
    KeyVaultEkmProxyClientCertificateInfo,
    KeyVaultEkmProxyInfo,
    KeyVaultPermission,
    KeyVaultRoleAssignment,
    KeyVaultRoleAssignmentProperties,
    KeyVaultRoleDefinition,
    KeyVaultSetting,
)
from ._settings_client import KeyVaultSettingsClient

__all__ = [
    "ApiVersion",
    "KeyVaultAccessControlClient",
    "KeyVaultBackupClient",
    "KeyVaultBackupResult",
    "KeyVaultDataAction",
    "KeyVaultEkmClient",
    "KeyVaultEkmConnection",
    "KeyVaultEkmConnectivityMode",
    "KeyVaultEkmPrivateEndpoint",
    "KeyVaultEkmPrivateEndpointConnectionState",
    "KeyVaultEkmPrivateEndpointConnectionStatus",
    "KeyVaultEkmPrivateEndpointOperation",
    "KeyVaultEkmPrivateEndpointOperationStatus",
    "KeyVaultEkmPrivateEndpointOperationType",
    "KeyVaultEkmPrivateEndpointProperties",
    "KeyVaultEkmPrivateEndpointProvisioningState",
    "KeyVaultEkmProxyClientCertificateInfo",
    "KeyVaultEkmProxyInfo",
    "KeyVaultPermission",
    "KeyVaultRoleAssignment",
    "KeyVaultRoleAssignmentProperties",
    "KeyVaultRoleDefinition",
    "KeyVaultRoleScope",
    "KeyVaultSetting",
    "KeyVaultSettingsClient",
    "KeyVaultSettingType",
]

from ._version import VERSION

__version__ = VERSION
