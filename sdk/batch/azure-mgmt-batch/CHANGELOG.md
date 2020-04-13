# Release History

## 8.0.0 (2020-04-10)
### REST API version
- This version targets REST API version 2020-03-01.

### Features
- Added ability to access the Batch DataPlane API without needing a public DNS entry for the account via the new `public_network_access` property on `BatchAccount`.
- Added new `PrivateLinkResource` and `PrivateEndpointConnection` resource types. These are both only used when the `public_network_access` property on `BatchAccount` is set to `Disabled`.
  - When `public_network_access` is set to `Disabled` a new `PrivateLinkResource` is visible in that account, which can be used to connect to the account using an ARM Private Endpoint in your VNET.
- Added ability to encrypt `ComputeNode` disk drives using the new `disk_encryption_configuration` property of `VirtualMachineConfiguration`.
- **[Breaking]** The `id` property of `ImageReference` can now only refer to a Shared Image Gallery image.
- **[Breaking]** Pools can now be provisioned without a public IP using the new `public_ip_configuration` property of `NetworkConfiguration`.
  - The `public_ips` property of `NetworkConfiguration` has moved in to `PublicIPAddressConfiguration` as well. This property can only be specified if `IPAddressProvisioningType` is `UserManaged`.


## 7.0.0 (2019-08-05)

  - Added ability to specify a collection of public IPs on
    `NetworkConfiguration` via the new `public_ips` property. This
    guarantees nodes in the Pool will have an IP from the list user
    provided IPs.
  - Added ability to mount remote file-systems on each node of a pool
    via the `mount_configuration` property on `Pool`.
  - Shared Image Gallery images can now be specified on the `id`
    property of `ImageReference` by referencing the image via its ARM
    ID.
  - **[Breaking]** When not specified, the default value for
    `wait_for_success` on `StartTask` is now `True` (was
    `False`).
  - **[Breaking]** When not specified, the default value for `scope`
    on `AutoUserSpecification` is now always `Pool` (was `Task` on
    Windows nodes, `Pool` on Linux nodes).
  - **Breaking** Model signatures are now using only keywords-arguments
    syntax. Each positional argument must be rewritten as a keyword
    argument.
  - Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to
    improve the behavior when unrecognized enum values are encountered.

## 6.0.0 (2019-01-14)

  -   - **[Breaking]** ResourceFile improvements
        
          - Added the ability specify an entire Azure Storage container
            in `ResourceFile`.
        
          - A new property `HttpUrl` replaces `BlobSource`. This can
            be any HTTP URL. Previously, this had to be an Azure Blob
            Storage URL.
        
          -   - When constructing a `ResourceFile` you can now choose
                from one of the following options:
                
                  - `HttpUrl`: Specify an HTTP URL pointing to a
                    specific file to download.
                  - `StorageContainerUrl`: Specify an Azure Storage
                    container URL. All blobs matching the `BlobPrefix`
                    in the Storage container will be downloaded.
                  - `AutoStorageContainerName`: Specify the name of a
                    container in the Batch registered auto-storage
                    account. All blobs matching the `BlobPrefix` in
                    the Storage container will be downloaded.

  - **[Breaking]** Removed `OSDisk` property from
    `VirtualMachineConfiguration`. This property is no longer
    supported.

  - **[Breaking]** `Application` no longer has a `Packages`
    property, instead the packages can be retrieved via the new
    `ApplicationPackage.List` API.

  - **[Breaking]** `TargetOsVersion` is now `OsVersion`, and
    `CurrentOsVersion` is no longer supported on
    `CloudServiceConfiguration`.

  - Added support on Windows pools for creating users with a specific
    login mode (either `Batch` or `Interactive`) via
    `WindowsUserConfiguration.LoginMode`.

  - Added support for `ContainerConfiguration` when creating a pool.

## 5.0.1 (2018-05-25)

**Bugfixes**

  - Compatibility of the sdist with wheel 0.31.0
  - msrestazure dependency version range

## 5.0.0 (2017-11-13)

  - Batch Pools are now ARM resources that can be created, updated and
    managed using the new client.PoolOperations.
  - Batch Certificates are now ARM resources that can be created,
    updated and managed using the new client.CertificateOperations.

## 4.1.0 (2017-07-24)

  - New operation to check the availability and validity of a Batch
    account name.

## 4.0.0 (2017-05-10)

  - New operation to list the operations available for the
    Microsoft.Batch provider, includes new `Operation` and
    `OperationDisplay` models.
  - Renamed `AddApplicationParameters` to
    `ApplicationCreateParameters`.
  - Renamed `UpdateApplicationParameters` to
    `ApplicationUpdateParameters`.
  - Removed `core_quota` attribute from `BatchAccount` object, now
    replaced by separate `dedicated_core_quota` and
    `low_priority_core_quota`.
  - `BatchAccountKeys` object now has additional `account_name`
    attribute.

## 3.0.1 (2017-04-19)

  - This wheel package is now built with the azure wheel extension

## 3.0.0 (2017-03-07)

  - Updated `BatchAccount` model - support for pool allocation in the
    user's subscription.
  - Updated `BatchAccount` model - support for referencing an Azure
    Key Vault for accounts created with a pool allocation mode of
    UserSubscription.
  - Updated `BatchAccount` model - properties are now read only.
  - Updated `ApplicationPackage` model - properties are now read only.
  - Updated `BatchAccountKeys` model - properties are now read only.
  - Updated `BatchLocationQuota` model - properties are now read only.

## 2.0.0 (2016-10-04)

  - Renamed `AccountResource` to `BatchAccount`.
  - Renamed `AccountOperations` to `BatchAccountOperations`. The
    `IBatchManagementClient.Account` property was also renamed to
    `IBatchManagementClient.BatchAccount`.
  - Split `Application` and `ApplicationPackage` operations up into
    two separate operation groups.
  - Updated `Application` and `ApplicationPackage` methods to use
    the standard `Create`, `Delete`, `Update` syntax. For example
    creating an `Application` is done via
    `ApplicationOperations.Create`.
  - Renamed `SubscriptionOperations` to `LocationOperations` and
    changed `SubscriptionOperations.GetSubscriptionQuotas` to be
    `LocationOperations.GetQuotas`.
  - This version targets REST API version 2015-12-01.

## 1.0.0 (2016-08-09)

  - Initial Release
