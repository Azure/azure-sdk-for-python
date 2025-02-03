# Release History

## 2.0.0 (2024-10-30)

### Breaking Changes

  - This package now only targets the latest Api-Version available on Azure and removes APIs of other Api-Version. After this change, the package can have much smaller size. If your application requires a specific and non-latest Api-Version, it's recommended to pin this package to the previous released version; If your application always only use latest Api-Version, please ignore this change.
    
## 1.5.0 (2024-07-22)

### Features Added

  - Model NetworkProfile has a new parameter load_balancer_profile

## 1.4.0 (2023-10-23)

### Features Added

  - Model NetworkProfile has a new parameter preconfigured_nsg
  - Model OpenShiftCluster has a new parameter worker_profiles_status
  - Model OpenShiftClusterUpdate has a new parameter worker_profiles_status

## 1.3.0 (2023-08-18)

### Features Added

  - Model NetworkProfile has a new parameter outbound_type

## 1.3.0b1 (2023-02-16)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 1.2.0 (2023-01-17)

### Features Added

  - Added operation group MachinePoolsOperations
  - Added operation group OpenShiftVersionsOperations
  - Added operation group SecretsOperations
  - Added operation group SyncIdentityProvidersOperations
  - Added operation group SyncSetsOperations
  - Model Resource has a new parameter system_data
  - Model TrackedResource has a new parameter system_data

## 1.1.0 (2022-05-10)

**Features**

  - Added operation OpenShiftClustersOperations.list_admin_credentials
  - Model ClusterProfile has a new parameter fips_validated_modules
  - Model MasterProfile has a new parameter disk_encryption_set_id
  - Model MasterProfile has a new parameter encryption_at_host
  - Model OpenShiftCluster has a new parameter system_data
  - Model OpenShiftClusterUpdate has a new parameter system_data
  - Model WorkerProfile has a new parameter disk_encryption_set_id
  - Model WorkerProfile has a new parameter encryption_at_host

## 1.0.0 (2021-05-20)

- GA release

## 1.0.0b1 (2020-12-10)

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

## 0.1.0 (2020-03-28)

* Initial Release
