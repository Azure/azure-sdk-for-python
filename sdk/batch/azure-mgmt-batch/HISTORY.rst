.. :changelog:

Release History
===============

6.0.0 (2019-01-14)
++++++++++++++++++

- **[Breaking]** ResourceFile improvements
    - Added the ability specify an entire Azure Storage container in `ResourceFile`.
    - A new property `HttpUrl` replaces `BlobSource`. This can be any HTTP URL. Previously, this had to be an Azure Blob Storage URL.
    - When constructing a `ResourceFile` you can now choose from one of the following options:
        - `HttpUrl`: Specify an HTTP URL pointing to a specific file to download.
        - `StorageContainerUrl`: Specify an Azure Storage container URL. All blobs matching the `BlobPrefix` in the Storage container will be downloaded.
        - `AutoStorageContainerName`: Specify the name of a container in the Batch registered auto-storage account. All blobs matching the `BlobPrefix` in the Storage container will be downloaded.
- **[Breaking]** Removed `OSDisk` property from `VirtualMachineConfiguration`. This property is no longer supported.
- **[Breaking]** `Application` no longer has a `Packages` property, instead the packages can be retrieved via the new  `ApplicationPackage.List` API.
- **[Breaking]** `TargetOsVersion` is now `OsVersion`, and `CurrentOsVersion` is no longer supported on `CloudServiceConfiguration`.
- Added support on Windows pools for creating users with a specific login mode (either `Batch` or `Interactive`) via `WindowsUserConfiguration.LoginMode`.
- Added support for `ContainerConfiguration` when creating a pool.

5.0.1 (2018-05-25)
++++++++++++++++++

**Bugfixes**

- Compatibility of the sdist with wheel 0.31.0
- msrestazure dependency version range

5.0.0 (2017-11-13)
++++++++++++++++++

- Batch Pools are now ARM resources that can be created, updated and managed using the new client.PoolOperations.
- Batch Certificates are now ARM resources that can be created, updated and managed using the new client.CertificateOperations.

4.1.0 (2017-07-24)
++++++++++++++++++

- New operation to check the availability and validity of a Batch account name.

4.0.0 (2017-05-10)
++++++++++++++++++

- New operation to list the operations available for the Microsoft.Batch provider, includes new `Operation` and `OperationDisplay` models.
- Renamed `AddApplicationParameters` to `ApplicationCreateParameters`.
- Renamed `UpdateApplicationParameters` to `ApplicationUpdateParameters`.
- Removed `core_quota` attribute from `BatchAccount` object, now replaced by separate `dedicated_core_quota` and `low_priority_core_quota`.
- `BatchAccountKeys` object now has additional `account_name` attribute.

3.0.1 (2017-04-19)
++++++++++++++++++

- This wheel package is now built with the azure wheel extension

3.0.0 (2017-03-07)
++++++++++++++++++

- Updated `BatchAccount` model - support for pool allocation in the user's subscription.
- Updated `BatchAccount` model - support for referencing an Azure Key Vault for accounts created with a pool allocation mode of UserSubscription.
- Updated `BatchAccount` model - properties are now read only.
- Updated `ApplicationPackage` model - properties are now read only.
- Updated `BatchAccountKeys` model - properties are now read only.
- Updated `BatchLocationQuota` model - properties are now read only.

2.0.0 (2016-10-04)
++++++++++++++++++

- Renamed `AccountResource` to `BatchAccount`.
- Renamed `AccountOperations` to `BatchAccountOperations`. The `IBatchManagementClient.Account` property was also renamed to `IBatchManagementClient.BatchAccount`.
- Split `Application` and `ApplicationPackage` operations up into two separate operation groups. 
- Updated `Application` and `ApplicationPackage` methods to use the standard `Create`, `Delete`, `Update` syntax. For example creating an `Application` is done via `ApplicationOperations.Create`.
- Renamed `SubscriptionOperations` to `LocationOperations` and changed `SubscriptionOperations.GetSubscriptionQuotas` to be `LocationOperations.GetQuotas`.
- This version targets REST API version 2015-12-01.

1.0.0 (2016-08-09)
++++++++++++++++++

- Initial Release
