# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from enum import Enum

from azure.core import CaseInsensitiveEnumMeta


class KeyVaultRoleScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Collection of well known role scopes. This list is not exhaustive."""

    GLOBAL = "/"  #: use this if you want role assignments to apply to everything on the resource
    KEYS = "/keys"  #: use this if you want role assignments to apply to all keys


class KeyVaultDataAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Supported permissions for data actions."""

    #: Read HSM key metadata.
    READ_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/read/action"
    #: Update an HSM key.
    WRITE_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/write/action"
    #: Read deleted HSM key.
    READ_DELETED_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/deletedKeys/read/action"
    #: Recover deleted HSM key.
    RECOVER_DELETED_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/deletedKeys/recover/action"
    #: Backup HSM keys.
    BACKUP_HSM_KEYS = "Microsoft.KeyVault/managedHsm/keys/backup/action"
    #: Restore HSM keys.
    RESTORE_HSM_KEYS = "Microsoft.KeyVault/managedHsm/keys/restore/action"
    #: Delete role assignment.
    DELETE_ROLE_ASSIGNMENT = "Microsoft.KeyVault/managedHsm/roleAssignments/delete/action"
    #: Get role assignment.
    GET_ROLE_ASSIGNMENT = "Microsoft.KeyVault/managedHsm/roleAssignments/read/action"
    #: Create or update role assignment.
    WRITE_ROLE_ASSIGNMENT = "Microsoft.KeyVault/managedHsm/roleAssignments/write/action"
    #: Get role definition.
    READ_ROLE_DEFINITION = "Microsoft.KeyVault/managedHsm/roleDefinitions/read/action"
    #: Create or update role definition.
    WRITE_ROLE_DEFINITION = "Microsoft.KeyVault/managedHsm/roleDefinitions/write/action"
    #: Delete role definition.
    DELETE_ROLE_DEFINITION = "Microsoft.KeyVault/managedHsm/roleDefinitions/delete/action"
    #: Encrypt using an HSM key.
    ENCRYPT_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/encrypt/action"
    #: Decrypt using an HSM key.
    DECRYPT_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/decrypt/action"
    #: Wrap using an HSM key.
    WRAP_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/wrap/action"
    #: Unwrap using an HSM key.
    UNWRAP_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/unwrap/action"
    #: Sign using an HSM key.
    SIGN_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/sign/action"
    #: Verify using an HSM key.
    VERIFY_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/verify/action"
    #: Create an HSM key.
    CREATE_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/create"
    #: Delete an HSM key.
    DELETE_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/delete"
    #: Export an HSM key.
    EXPORT_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/export/action"
    #: Release an HSM key using Secure Key Release.
    RELEASE_KEY = "Microsoft.KeyVault/managedHsm/keys/release/action"
    #: Import an HSM key.
    IMPORT_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/import/action"
    #: Purge a deleted HSM key.
    PURGE_DELETED_HSM_KEY = "Microsoft.KeyVault/managedHsm/keys/deletedKeys/delete"
    #: Download an HSM security domain.
    DOWNLOAD_HSM_SECURITY_DOMAIN = "Microsoft.KeyVault/managedHsm/securitydomain/download/action"
    #: Check status of HSM security domain download.
    DOWNLOAD_HSM_SECURITY_DOMAIN_STATUS = "Microsoft.KeyVault/managedHsm/securitydomain/download/read"
    #: Upload an HSM security domain.
    UPLOAD_HSM_SECURITY_DOMAIN = "Microsoft.KeyVault/managedHsm/securitydomain/upload/action"
    #: Check the status of the HSM security domain exchange file.
    READ_HSM_SECURITY_DOMAIN_STATUS = "Microsoft.KeyVault/managedHsm/securitydomain/upload/read"
    #: Download an HSM security domain transfer key.
    READ_HSM_SECURITY_DOMAIN_TRANSFER_KEY = "Microsoft.KeyVault/managedHsm/securitydomain/transferkey/read"
    #: Start an HSM backup.
    START_HSM_BACKUP = "Microsoft.KeyVault/managedHsm/backup/start/action"
    #: Start an HSM restore.
    START_HSM_RESTORE = "Microsoft.KeyVault/managedHsm/restore/start/action"
    #: Read an HSM backup status.
    READ_HSM_BACKUP_STATUS = "Microsoft.KeyVault/managedHsm/backup/status/action"
    #: Read an HSM restore status.
    READ_HSM_RESTORE_STATUS = "Microsoft.KeyVault/managedHsm/restore/status/action"
    #: Generate random numbers.
    RANDOM_NUMBERS_GENERATE = "Microsoft.KeyVault/managedHsm/rng/action"


class KeyVaultSettingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type specifier of the setting value."""

    BOOLEAN = "boolean"
