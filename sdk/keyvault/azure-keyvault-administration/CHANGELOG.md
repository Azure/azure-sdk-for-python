# Release History

## 4.0.0b2 (2020-10-06)
### Added
- `KeyVaultBackupClient.get_backup_status` and `.get_restore_status` enable
  checking the status of a pending operation by its job ID
  ([#13718](https://github.com/Azure/azure-sdk-for-python/issues/13718))

### Breaking Changes
- The `role_assignment_name` parameter of
  `KeyVaultAccessControlClient.create_role_assignment` is now an optional
  keyword-only argument. When this argument isn't passed, the client will
  generate a name for the role assignment.
  ([#13512](https://github.com/Azure/azure-sdk-for-python/issues/13512))

## 4.0.0b1 (2020-09-08)
### Added
- `KeyVaultAccessControlClient` performs role-based access control operations
- `KeyVaultBackupClient` performs full vault backup and full and selective
  restore operations
