# Azure Storage libraries for Python

Azure Storage is a Microsoft-managed service providing cloud storage that is highly available, secure, durable, scalable, and redundant.  Azure Storage includes Blobs (objects), Queues, and Files.

- [azure-storage-blob][blobs] is Microsoft's object storage solution for the cloud. Blob storage is optimized for storing massive amounts of unstructured data that does not adhere to a particular data model or definition, such as text or binary data.

- [azure-storage-queue][queues] is a service for storing large numbers of messages.  A queue message can be up to 64 KB in size and a queue may contain millions of messages, up to the total capacity limit of a storage account.

- [azure-storage-file-share][fileshares] offers fully managed file shares in the cloud that are accessible via the industry standard Server Message Block (SMB) protocol.  Azure file shares can be mounted concurrently by cloud or on-premises deployments of Windows, Linux, and macOS.

- [azure-storage-file-datalake][datalake] offers fully directory level operations and permission related operations for hierarchical namespace enabled (HNS) enabled storage accounts.

- [azure-mgmt-storage][management] supports managing Azure Storage resources, including the creation of new storage accounts.

## Contributing

See the [Storage CONTRIBUTING.md][storage_contrib] for details on building,
testing, and contributing to these libraries.

This project welcomes contributions and suggestions.  Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution. For
details, visit [cla.microsoft.com][cla].

This project has adopted the [Microsoft Open Source Code of Conduct][coc].
For more information see the [Code of Conduct FAQ][coc_faq]
or contact [opencode@microsoft.com][coc_contact] with any
additional questions or comments.

<!-- LINKS -->
[blobs]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/storage/azure-storage-blob/README.md
[queues]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/storage/azure-storage-queue/README.md
[fileshares]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/storage/azure-storage-file-share/README.md
[datalake]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/storage/azure-storage-file-datalake/README.md
[management]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/storage/azure-mgmt-storage/
[storage_contrib]: https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md
[cla]: https://cla.microsoft.com
[coc]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
