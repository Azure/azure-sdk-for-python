# Release History

## 1.1.0b2 (2023-10-23)

### Features Added

  - Added operation AzureBareMetalInstancesOperations.begin_restart
  - Added operation AzureBareMetalInstancesOperations.begin_shutdown
  - Added operation AzureBareMetalInstancesOperations.begin_start
  - Added operation group AzureBareMetalStorageInstancesOperations
  - Model Operation has a new parameter action_type
  - Model Operation has a new parameter origin
  - Model Resource has a new parameter system_data
  - Model TrackedResource has a new parameter system_data

## 1.1.0b1 (2022-11-09)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 1.0.0 (2021-10-14)

**Features**

  - Model AzureBareMetalInstance has a new parameter system_data
  - Added operation AzureBareMetalInstancesOperations.list_by_resource_group

**Breaking changes**

  - Model Display no longer has parameter origin
  - Removed operation AzureBareMetalInstancesOperations.list
  - Removed operation AzureBareMetalInstancesOperations.begin_shutdown
  - Removed operation AzureBareMetalInstancesOperations.begin_start
  - Removed operation AzureBareMetalInstancesOperations.begin_restart
  - Removed operation AzureBareMetalInstancesOperations.begin_delete

## 1.0.0b2 (2021-06-28)

* Fix dependencies

## 1.0.0b1 (2020-09-22)

* Initial Release
