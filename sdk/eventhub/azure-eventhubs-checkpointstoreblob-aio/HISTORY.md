# Release History

## 2019-12-04 1.0.0b6

**Breaking changes**

- Renamed `BlobPartitionManager` to `BlobCheckpointStore`.
- Constructor of `BlobCheckpointStore` has been updated to take the storage container details directly rather than an instance of `ContainerClient`.
- A `from_connection_string` constructor has been added for Blob Storage connection strings.
- Module `blobstoragepmaio` is now internal, import directly from `azure.eventhub.extensions.checkpointstoreblobaio`.
- `BlobCheckpointStore` now has a `close()` function for shutting down an HTTP connection pool, additionally the object can be used in a context manager to manage the connection.

## 2019-11-04 1.0.0b5

**New features**

- Added method `list_checkpoints` which list all the checkpoints under given eventhub namespace, eventhub name and consumer group.

## 1.0.0b4 (2019-10-09)
This release has trivial internal changes only. No feature changes.

## 1.0.0b1 (2019-09-10)

**New features**

- `BlobPartitionManager` that uses Azure Blob Storage Block Blob to store EventProcessor checkpoint data

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python/sdk/eventhub/azure-eventhubs-checkpointstoreblob-aio/HISTORY.png)