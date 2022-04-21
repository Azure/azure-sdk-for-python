# Release History

## 4.1.1 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

## 4.1.0 (2022-03-28)

### Features Added
- Key Vault API version 7.3 is now the default
- Added support for multi-tenant authentication when using `azure-identity`
  1.8.0 or newer ([#20698](https://github.com/Azure/azure-sdk-for-python/issues/20698))

### Other Changes
- (From 4.1.0b3) Python 2.7 is no longer supported. Please use Python version 3.6 or later.
- (From 4.1.0b3) Updated minimum `azure-core` version to 1.20.0
- (From 4.1.0b2) To support multi-tenant authentication, `get_token` calls during challenge
  authentication requests now pass in a `tenant_id` keyword argument
  ([#20698](https://github.com/Azure/azure-sdk-for-python/issues/20698)). See
  https://aka.ms/azsdk/python/identity/tokencredential for more details on how to integrate
  this parameter if `get_token` is implemented by a custom credential.

## 4.1.0b3 (2022-02-08)

### Other Changes
- Python 2.7 is no longer supported. Please use Python version 3.6 or later.
- Updated minimum `azure-core` version to 1.20.0
- (From 4.1.0b2) To support multi-tenant authentication, `get_token` calls during challenge
  authentication requests now pass in a `tenant_id` keyword argument
  ([#20698](https://github.com/Azure/azure-sdk-for-python/issues/20698))

## 4.1.0b2 (2021-11-11)

### Features Added
- Added support for multi-tenant authentication when using `azure-identity` 1.7.1 or newer
  ([#20698](https://github.com/Azure/azure-sdk-for-python/issues/20698))

### Other Changes
- Updated minimum `azure-core` version to 1.15.0

## 4.1.0b1 (2021-09-09)

### Features Added
- Key Vault API version 7.3-preview is now the default

## 4.0.0 (2021-06-22)
### Changed
- Key Vault API version 7.2 is now the default
- `KeyVaultAccessControlClient.delete_role_assignment` and
  `.delete_role_definition` no longer raise an error  when the resource to be
  deleted is not found
- Raised minimum azure-core version to 1.11.0

### Added
- `KeyVaultAccessControlClient.set_role_definition` accepts an optional
  `assignable_scopes` keyword-only argument

### Breaking Changes
- `KeyVaultAccessControlClient.delete_role_assignment` and
  `.delete_role_definition` return None
- Changed parameter order in `KeyVaultAccessControlClient.set_role_definition`.
  `permissions` is now an optional keyword-only argument
- Renamed `BackupOperation` to `KeyVaultBackupResult`, and removed all but
  its `folder_url` property
- Removed `RestoreOperation` and `SelectiveKeyRestoreOperation` classes
- Removed `KeyVaultBackupClient.begin_selective_restore`. To restore a
  single key, pass the key's name to `KeyVaultBackupClient.begin_restore`:
  ```
  # before (4.0.0b3):
  client.begin_selective_restore(folder_url, sas_token, key_name)

  # after:
  client.begin_restore(folder_url, sas_token, key_name=key_name)
  ```
- Removed `KeyVaultBackupClient.get_backup_status` and `.get_restore_status`. Use
  the pollers returned by `KeyVaultBackupClient.begin_backup` and `.begin_restore`
  to check whether an operation has completed
- `KeyVaultRoleAssignment`'s `principal_id`, `role_definition_id`, and `scope`
  are now properties of a `properties` property
  ```
  # before (4.0.0b3):
  print(KeyVaultRoleAssignment.scope)

  # after:
  print(KeyVaultRoleAssignment.properties.scope)
  ```
- Renamed `KeyVaultPermission` properties:
  - `allowed_actions` -> `actions`
  - `denied_actions` -> `not_actions`
  - `allowed_data_actions` -> `data_actions`
  - `denied_data_actions` -> `denied_data_actions`
- Renamed argument `role_assignment_name` to `name` in
  `KeyVaultAccessControlClient.create_role_assignment`, `.delete_role_assignment`,
  and `.get_role_assignment`
- Renamed argument `role_definition_name` to `name` in
  `KeyVaultAccessControlClient.delete_role_definition` and `.get_role_definition`
- Renamed argument `role_scope` to `scope` in `KeyVaultAccessControlClient` methods

## 4.0.0b3 (2021-02-09)
### Added
- `KeyVaultAccessControlClient` supports managing custom role definitions

### Breaking Changes
- Renamed `KeyVaultBackupClient.begin_full_backup()` to `.begin_backup()`
- Renamed `KeyVaultBackupClient.begin_full_restore()` to `.begin_restore()`
- Renamed `BackupOperation.azure_storage_blob_container_uri` to `.folder_url`
- Renamed `id` property of `BackupOperation`, `RestoreOperation`, and
 `SelectiveKeyRestoreOperation` to `job_id`
- Renamed `blob_storage_uri` parameters of `KeyVaultBackupClient.begin_restore()`
  and `.begin_selective_restore()` to `folder_url`
- Removed redundant `folder_name` parameter from
  `KeyVaultBackupClient.begin_restore()` and `.begin_selective_restore()` (the
  `folder_url` parameter contains the folder name)
- Renamed `KeyVaultPermission` attributes:
  - `actions` -> `allowed_actions`
  - `data_actions` -> `allowed_data_actions`
  - `not_actions` -> `denied_actions`
  - `not_data_actions` -> `denied_data_actions`
- Renamed `KeyVaultRoleAssignment.assignment_id` to `.role_assignment_id`
- Renamed `KeyVaultRoleScope` enum values:
  - `global_value` -> `GLOBAL`
  - `keys_value` -> `KEYS`

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
