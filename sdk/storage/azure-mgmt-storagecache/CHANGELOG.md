# Release History

## 1.0.0 (2021-05-13)

**Features**

  - Added operation StorageTargetsOperations.begin_dns_refresh
  - Added operation StorageTargetsOperations.begin_delete
  - Added operation StorageTargetsOperations.begin_create_or_update
  - Added operation CachesOperations.begin_upgrade_firmware
  - Added operation CachesOperations.begin_start
  - Added operation CachesOperations.begin_create_or_update
  - Added operation CachesOperations.begin_flush
  - Added operation CachesOperations.begin_delete
  - Added operation CachesOperations.begin_stop
  - Added operation CachesOperations.begin_debug_info
  - Added operation group AscOperationsOperations

**Breaking changes**

  - Operation StorageTargetsOperations.get has a new signature
  - Operation StorageTargetsOperations.list_by_cache has a new signature
  - Operation SkusOperations.list has a new signature
  - Operation Operations.list has a new signature
  - Operation UsageModelsOperations.list has a new signature
  - Removed operation StorageTargetsOperations.create_or_update
  - Removed operation StorageTargetsOperations.delete
  - Removed operation StorageTargetsOperations.dns_refresh
  - Removed operation CachesOperations.delete
  - Removed operation CachesOperations.upgrade_firmware
  - Removed operation CachesOperations.start
  - Removed operation CachesOperations.flush
  - Removed operation CachesOperations.debug_info
  - Removed operation CachesOperations.stop
  - Removed operation CachesOperations.create_or_update
  - Removed operation group AscOperations

## 0.3.0 (2020-03-01)

**Features**

  - Model Cache has a new parameter security_settings
  - Model Cache has a new parameter network_settings
  - Model Cache has a new parameter identity
  - Model Cache has a new parameter encryption_settings

## 0.2.0 (2019-11-12)

**Features**

  - Added operation CachesOperations.create_or_update
  - Added operation StorageTargetsOperations.create_or_update

**Breaking changes**

  - Removed operation CachesOperations.create
  - Removed operation StorageTargetsOperations.create
  - Removed operation StorageTargetsOperations.update

## 0.1.0rc1 (2019-09-03)

  - Initial Release
