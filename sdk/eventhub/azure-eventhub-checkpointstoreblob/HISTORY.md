# Release History

## 1.0.0 (2020-01-13)
Stable release. No new features or API changes.

## 1.0.0b6 (2019-12-04)

**Breaking changes**

- Renamed `BlobPartitionManager` to `BlobCheckpointStore`.
- Constructor of `BlobCheckpointStore` has been updated to take the storage container details directly rather than an instance of `ContainerClient`.
- A `from_connection_string` constructor has been added for Blob Storage connection strings.
- Module `blobstoragepm` is now internal, all imports should be directly from `azure.eventhub.extensions.checkpointstoreblob`.
- `BlobCheckpointStore` now has a `close()` function for shutting down an HTTP connection pool, additionally the object can be used in a context manager to manage the connection.

## 1.0.0b5 (2019-11-04)

**New features**

- `BlobPartitionManager` that uses Azure Blob Storage Block Blob to store EventProcessor checkpoint data

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python/sdk/eventhub/azure-eventhub-checkpointstoreblob/HISTORY.png)