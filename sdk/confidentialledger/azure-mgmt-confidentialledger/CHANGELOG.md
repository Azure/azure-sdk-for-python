# Release History

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
