# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from enum import Enum


class KeyVaultRoleScope(str, Enum):
    """Collection of well known role scopes. This list is not exhaustive"""

    global_value = "/"  #: use this if you want role assignments to apply to everything on the resource

    keys_value = "/keys"  #: use this if you want role assignments to apply to all keys


class DataActionPermission(str, Enum):
    """Supported permissions for data actions.
    """

    #: Read HSM key metadata.
    read_hsm_key = "Microsoft.KeyVault/managedHsm/keys/read/action"
    #: Update an HSM key.
    write_hsm_key = "Microsoft.KeyVault/managedHsm/keys/write/action"
    #: Read deleted HSM key.
    read_deleted_hsm_key = "Microsoft.KeyVault/managedHsm/keys/deletedKeys/read/action"
    #: Recover deleted HSM key.
    recover_deleted_hsm_key = "Microsoft.KeyVault/managedHsm/keys/deletedKeys/recover/action"
    #: Backup HSM keys.
    backup_hsm_keys = "Microsoft.KeyVault/managedHsm/keys/backup/action"
    #: Restore HSM keys.
    restore_hsm_key = "Microsoft.KeyVault/managedHsm/keys/restore/action"
    #: Delete role assignment.
    delete_role_assignment = "Microsoft.KeyVault/managedHsm/roleAssignments/delete/action"
    #: Get role assignment.
    get_role_assignment = "Microsoft.KeyVault/managedHsm/roleAssignments/read/action"
    #: Create or update role assignment.
    write_role_assignment = "Microsoft.KeyVault/managedHsm/roleAssignments/write/action"
    #: Get role definition.
    read_role_definition = "Microsoft.KeyVault/managedHsm/roleDefinitions/read/action"
    #: Encrypt using an HSM key.
    encrypt_hsm_key = "Microsoft.KeyVault/managedHsm/keys/encrypt/action"
    #: Decrypt using an HSM key.
    decrypt_hsm_key = "Microsoft.KeyVault/managedHsm/keys/decrypt/action"
    #: Wrap using an HSM key.
    wrap_hsm_key = "Microsoft.KeyVault/managedHsm/keys/wrap/action"
    #: Unwrap using an HSM key.
    unwrap_hsm_key = "Microsoft.KeyVault/managedHsm/keys/unwrap/action"
    #: Sign using an HSM key.
    sign_hsm_key = "Microsoft.KeyVault/managedHsm/keys/sign/action"
    #: Verify using an HSM key.
    verify_hsm_key = "Microsoft.KeyVault/managedHsm/keys/verify/action"
    #: Create an HSM key.
    create_hsm_key = "Microsoft.KeyVault/managedHsm/keys/create"
    #: Delete an HSM key.
    delete_hsm_key = "Microsoft.KeyVault/managedHsm/keys/delete"
    #: Export an HSM key.
    export_hsm_key = "Microsoft.KeyVault/managedHsm/keys/export/action"
    #: Import an HSM key.
    import_hsm_key = "Microsoft.KeyVault/managedHsm/keys/import/action"
    #: Purge a deleted HSM key.
    purge_deleted_hsm_key = "Microsoft.KeyVault/managedHsm/keys/deletedKeys/delete"
    #: Download an HSM security domain.
    download_hsm_security_domain = "Microsoft.KeyVault/managedHsm/securitydomain/download/action"
    #: Upload an HSM security domain.
    upload_hsm_security_domain = "Microsoft.KeyVault/managedHsm/securitydomain/upload/action"
    #: Check the status of the HSM security domain exchange file.
    read_hsm_security_domain_status = "Microsoft.KeyVault/managedHsm/securitydomain/upload/read"
    #: Download an HSM security domain transfer key.
    read_hsm_security_domain_transfer_key = "Microsoft.KeyVault/managedHsm/securitydomain/transferkey/read"
    #: Start an HSM backup.
    start_hsm_backup = "Microsoft.KeyVault/managedHsm/backup/start/action"
    #: Start an HSM restore.
    start_hsm_restore = "Microsoft.KeyVault/managedHsm/restore/start/action"
    #: Read an HSM backup status.
    read_hsm_backup_status = "Microsoft.KeyVault/managedHsm/backup/status/action"
    #: Read an HSM restore status.
    read_hsm_restore_status = "Microsoft.KeyVault/managedHsm/restore/status/action"
