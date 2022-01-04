# Release History

## 1.2.0 (Unreleased)

This version and all future versions will require Python 3.7+. Python 2.7 and 3.6 are no longer supported.

### Bugs Fixed

- Fixed a bug with `BlobCheckpointStore.claim_ownership` mutating the `ownership_list` argument to no longer mutate the argument.
- Updated `azure-core` dependecy to 1.20.1 to fix `cchardet` ImportError.

## 1.1.4 (2021-04-07)

This version and all future versions will require Python 2.7 or Python 3.6+, Python 3.5 is no longer supported.

**New features**
- Updated `list_ownership`, `claim_ownership`, `update_checkpoint`, `list_checkpoints` on `BlobCheckpointStore` to support taking `**kwargs`.

## 1.1.3 (2021-03-09)

This version will be the last version to officially support Python 3.5, future versions will require Python 2.7 or Python 3.6+.

**Bug fixes**
- Updated vendor azure-storage-blob dependency to v12.7.1.
  - Fixed storage blob authentication failure due to request date header too old (#16192).

## 1.1.2 (2021-01-11)

**Bug fixes**
- Fixed a bug that `BlobCheckpointStore.list_ownership` and `BlobCheckpointStore.list_checkpoints` triggering `KeyError` due to reading empty metadata of parent node when working with Data Lake enabled Blob Storage.

## 1.1.1 (2020-09-08)

**Bug fixes**
- Fixed a bug that may gradually slow down retrieving checkpoint data from the storage blob if the storage account "File share soft delete" is enabled. #12836

## 1.1.0 (2020-03-09)

**New features**
- Param `api_version` of `BlobCheckpointStore` now supports older versions of Azure Storage Service API.

## 1.0.0 (2020-01-13)
Stable release. No new features or API changes.

## 1.0.0b6 (2019-12-04)

**Breaking changes**

- Renamed `BlobPartitionManager` to `BlobCheckpointStore`.
- Constructor of `BlobCheckpointStore` has been updated to take the storage container details directly rather than an instance of `ContainerClient`.
- A `from_connection_string` constructor has been added for Blob Storage connection strings.
- Module `blobstoragepmaio` is now internal, all imports should be directly from `azure.eventhub.extensions.checkpointstoreblobaio`.
- `BlobCheckpointStore` now has a `close()` function for shutting down an HTTP connection pool, additionally the object can be used in a context manager to manage the connection.

## 1.0.0b5 (2019-11-04)

**New features**

- Added method `list_checkpoints` which list all the checkpoints under given eventhub namespace, eventhub name and consumer group.

## 1.0.0b4 (2019-10-09)
This release has trivial internal changes only. No feature changes.

## 1.0.0b1 (2019-09-10)

**New features**

- `BlobPartitionManager` that uses Azure Blob Storage Block Blob to store EventProcessor checkpoint data

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python/sdk/eventhub/azure-eventhub-checkpointstoreblob-aio/HISTORY.png)
