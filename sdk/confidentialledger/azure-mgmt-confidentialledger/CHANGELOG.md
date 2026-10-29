# Release History

## 2.0.0b6 (2026-07-07)

### Features Added

  - Model `LedgerProperties` added property `scitt_configuration`
  - Model `LedgerProperties` added property `storage_usage_bytes`
  - Added model `ConfidentialLedgerFilesExport`
  - Added model `ConfidentialLedgerFilesExportResponse`
  - Operation group `LedgerOperations` added method `begin_files_export`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - Renamed client `ConfidentialLedger` to `ConfidentialLedgerMgmtClient`
  - Deleted or renamed model `ConfidentialLedgerBackup`
  - Deleted or renamed model `ConfidentialLedgerBackupResponse`
  - Deleted or renamed model `ConfidentialLedgerRestore`
  - Deleted or renamed model `ConfidentialLedgerRestoreResponse`
  - Deleted or renamed model `DeploymentType`
  - Deleted or renamed model `LanguageRuntime`
  - Deleted or renamed model `ManagedCCF`
  - Deleted or renamed model `ManagedCCFBackup`
  - Deleted or renamed model `ManagedCCFBackupResponse`
  - Deleted or renamed model `ManagedCCFProperties`
  - Deleted or renamed model `ManagedCCFRestore`
  - Deleted or renamed model `ManagedCCFRestoreResponse`
  - Deleted or renamed model `MemberIdentityCertificate`
  - Deleted or renamed method `LedgerOperations.begin_backup`
  - Deleted or renamed method `LedgerOperations.begin_restore`
  - Deleted or renamed operation group `ManagedCCFOperations`

### Other Changes

  - Deleted model `CertificateTags`/`ConfidentialLedgerList`/`ManagedCCFList`/`ResourceProviderOperationList` which actually were not used by SDK users
  - Renamed operation group `ConfidentialLedgerOperationsMixin` which actually was not used by users to `_ConfidentialLedgerOperationsMixin`

## 1.0.1 (2026-05-07)

### Other Changes

  - Regenerated code with latest code generator tool

## 2.0.0b5 (2025-05-19)

### Features Added

  - Model `LedgerProperties` added property `host_level`
  - Model `LedgerProperties` added property `max_body_size_in_mb`
  - Model `LedgerProperties` added property `subject_name`
  - Model `LedgerProperties` added property `node_count`
  - Model `LedgerProperties` added property `write_lb_address_prefix`
  - Model `LedgerProperties` added property `worker_threads`
  - Model `LedgerProperties` added property `enclave_platform`
  - Model `LedgerProperties` added property `application_type`
  - Model `ManagedCCFProperties` added property `enclave_platform`
  - Added enum `ApplicationType`
  - Added enum `EnclavePlatform`

## 2.0.0b4 (2024-04-22)

### Features Added

  - Added operation LedgerOperations.begin_backup
  - Added operation LedgerOperations.begin_restore
  - Added operation ManagedCCFOperations.begin_backup
  - Added operation ManagedCCFOperations.begin_restore
  - Model LedgerProperties has a new parameter ledger_sku
  - Model ManagedCCFProperties has a new parameter running_state

## 2.0.0b3 (2023-05-17)

### Other Changes

  - Added samples

## 2.0.0b2 (2023-04-20)

### Features Added

  - Added operation group ManagedCCFOperations
  - Model LedgerProperties has a new parameter running_state

### Breaking Changes

  - Model LedgerProperties no longer has parameter ledger_storage_account
  - Parameter location of model ConfidentialLedger is now required

## 2.0.0b1 (2022-11-25)

### Features Added

  - Model LedgerProperties has a new parameter ledger_storage_account

### Breaking Changes

  - Removed operation group ConfidentialLedgerOperationsMixin

## 1.0.0 (2022-05-30)

**Features**

  - Added operation group ConfidentialLedgerOperationsMixin

**Breaking changes**

  - Model LedgerProperties no longer has parameter ledger_storage_account

## 1.0.0b1 (2021-04-28)

* Initial Release
