# Release History

## 0.4.0 (2021-02-18)

**Features**

  - Model StorageTarget has a new parameter system_data
  - Model StorageTarget has a new parameter location
  - Model ApiOperationDisplay has a new parameter description
  - Model NamespaceJunction has a new parameter nfs_access_policy
  - Model ApiOperation has a new parameter service_specification
  - Model ApiOperation has a new parameter is_data_action
  - Model ApiOperation has a new parameter origin
  - Model Cache has a new parameter system_data
  - Model Cache has a new parameter directory_services_settings
  - Model StorageTargetResource has a new parameter system_data
  - Model StorageTargetResource has a new parameter location
  - Added operation CachesOperations.debug_info
  - Added operation group AscOperations
**Breaking changes**
  - Parameter target_type of model Nfs3TargetProperties is now required
  - Parameter target_type of model UnknownTargetProperties is now required
  - Parameter target_type of model StorageTargetProperties is now required
  - Parameter target_type of model ClfsTargetProperties is now required
  - Model Nfs3TargetProperties no longer has parameter target_base_type
  - Model StorageTarget no longer has parameter target_type
  - Model UnknownTargetProperties no longer has parameter target_base_type
  - Model StorageTargetProperties no longer has parameter target_base_type
  - Model ClfsTargetProperties no longer has parameter target_base_type
  - Model CacheSecuritySettings has a new signature

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
