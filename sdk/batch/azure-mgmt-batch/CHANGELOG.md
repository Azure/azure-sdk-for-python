# Release History

## 16.2.0 (2022-06-06)

**Features**

  - Added operation PrivateEndpointConnectionOperations.begin_delete
  - Model BatchAccount has a new parameter network_profile
  - Model BatchAccount has a new parameter node_management_endpoint
  - Model BatchAccountCreateParameters has a new parameter network_profile
  - Model BatchAccountUpdateParameters has a new parameter network_profile
  - Model BatchAccountUpdateParameters has a new parameter public_network_access
  - Model PrivateEndpointConnection has a new parameter group_ids

## 16.1.0 (2022-02-24)

**Features**

  - Added operation BatchAccountOperations.get_detector
  - Added operation BatchAccountOperations.list_detectors
  - Model NetworkConfiguration has a new parameter dynamic_v_net_assignment_scope

## 16.0.0 (2021-07-30)

**Features**

  - Model BatchAccount has a new parameter allowed_authentication_modes
  - Model AutoStorageBaseProperties has a new parameter node_identity_reference
  - Model AutoStorageBaseProperties has a new parameter authentication_mode
  - Model AzureBlobFileSystemConfiguration has a new parameter identity_reference
  - Model BatchAccountUpdateParameters has a new parameter allowed_authentication_modes
  - Model ContainerRegistry has a new parameter identity_reference
  - Model Operation has a new parameter is_data_action
  - Model BatchAccountCreateParameters has a new parameter allowed_authentication_modes
  - Model AutoStorageProperties has a new parameter node_identity_reference
  - Model AutoStorageProperties has a new parameter authentication_mode
  - Model ResourceFile has a new parameter identity_reference
  - Model VirtualMachineConfiguration has a new parameter os_disk
  - Added operation BatchAccountOperations.list_outbound_network_dependencies_endpoints
  - Added operation LocationOperations.list_supported_cloud_service_skus
  - Added operation LocationOperations.list_supported_virtual_machine_skus

**Breaking changes**

  - Rename `BatchManagement` to `BatchManagementClient`

## 15.0.0 (2021-02-01)

- Fix changelog

## 15.0.0b1 (2021-01-28)

**Features**

  - Added new extensions property to VirtualMachineConfiguration on pools to specify virtual machine extensions for nodes
  - Added the ability to specify availability zones using a new property node_placement_configuration on VirtualMachineConfiguration
  - Added a new identity property on Pool to specify a managed identity
  - Added a new user_assigned_identities on BatchAccountIdentity to specify a user managed identity
  - Added certificate operation method PoolOperations.create
  - Added certificate operation method CertificateOperations.create

**Breaking changes**

  - Removed certificate operation method PoolOperations.begin_create. Certificate operations are not long running operations so this was incorrect.
  - Removed certificate operation method CertificateOperations.begin_create. Certificate operations are not long running operations so this was incorrect.

## 14.0.0 (2020-12-22)

- GA release

## 14.0.0b1 (2020-10-23)

This is beta preview version.

This version uses a next-generation code generator that introduces important breaking changes, but also important new features (like unified authentication and async programming).

**General breaking changes**

- Credential system has been completly revamped:

  - `azure.common.credentials` or `msrestazure.azure_active_directory` instances are no longer supported, use the `azure-identity` classes instead: https://pypi.org/project/azure-identity/
  - `credentials` parameter has been renamed `credential`

- The `config` attribute no longer exists on a client, configuration should be passed as kwarg. Example: `MyClient(credential, subscription_id, enable_logging=True)`. For a complete set of
  supported options, see the [parameters accept in init documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)
- You can't import a `version` module anymore, use `__version__` instead
- Operations that used to return a `msrest.polling.LROPoller` now returns a `azure.core.polling.LROPoller` and are prefixed with `begin_`.
- Exceptions tree have been simplified and most exceptions are now `azure.core.exceptions.HttpResponseError` (`CloudError` has been removed).
- Most of the operation kwarg have changed. Some of the most noticeable:

  - `raw` has been removed. Equivalent feature can be found using `cls`, a callback that will give access to internal HTTP response for advanced user
  - For a complete set of
  supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry) for an overview.

## 9.0.0 (2020-05-29)
### REST API version
- This version targets REST API version 2020-05-01.

### Features
- Added ability to access the Batch DataPlane API without needing a public DNS entry for the account via the new `public_network_access` property on `BatchAccount`.
- Added new `PrivateLinkResource` and `PrivateEndpointConnection` resource types. These are both only used when the `public_network_access` property on `BatchAccount` is set to `Disabled`.
  - When `public_network_access` is set to `Disabled` a new `PrivateLinkResource` is visible in that account, which can be used to connect to the account using an ARM Private Endpoint in your VNET.
- Added ability to encrypt `ComputeNode` disk drives using the new `disk_encryption_configuration` property of `VirtualMachineConfiguration`.
- **[Breaking]** The `id` property of `ImageReference` can now only refer to a Shared Image Gallery image.
- **[Breaking]** Pools can now be provisioned without a public IP using the new `public_ip_configuration` property of `NetworkConfiguration`.
  - The `public_ips` property of `NetworkConfiguration` has moved in to `PublicIPAddressConfiguration` as well. This property can only be specified if `IPAddressProvisioningType` is `UserManaged`.
- Adds a new property `identity` of type `BatchAccountIdentity` to `BatchAccount`. This can be used to configure how customer data is encrypted inside the Batch account.
    - This new property is configurable at  the account level on create and update through a new `identity` property on `BatchAccountCreateParameters` and `BatchAccountUpdateParameters`

### Fixes
- [Breaking] Move tags from being an argument on create and update pool parameters to being a part of `BatchAccountCreateParameters` and `BatchAccountUpdateParameters` to properly reflect the REST API

## 8.0.1 (2020-05-26) [Deprecated]
### Notices
- This version targeted an invalid REST API. This version does not honor the associated REST API contract.

### Bugfixes
- Fix issues in PrivateEndpointConnection get and update methods due to mistakes in the Swagger specification causing validation to fail. It is advised to use version 9+ to make use of the features added in this version.

## 8.0.0 (2020-04-10) [Deprecated]
### Notices
- This version targeted an invalid REST API. Currently the PrivateEndpoint get() and update() functions do not function correctly. It is advised to use version 9+ to make use of the features added in this version.

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
