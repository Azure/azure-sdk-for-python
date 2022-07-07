# Release History

## 1.3.0 (2022-07-07)

**Features**

  - Added operation CachesOperations.begin_pause_priming_job
  - Added operation CachesOperations.begin_resume_priming_job
  - Added operation CachesOperations.begin_space_allocation
  - Added operation CachesOperations.begin_start_priming_job
  - Added operation CachesOperations.begin_stop_priming_job
  - Model ApiOperationPropertiesServiceSpecification has a new parameter log_specifications
  - Model Cache has a new parameter priming_jobs
  - Model Cache has a new parameter space_allocation
  - Model Cache has a new parameter upgrade_settings
  - Model StorageTarget has a new parameter allocation_percentage

## 1.2.0 (2022-03-22)

**Features**

  - Added operation StorageTargetOperations.begin_invalidate
  - Added operation group AscUsagesOperations
  - Model Cache has a new parameter zones

## 1.1.0 (2021-09-30)

**Features**

  - Model StorageTarget has a new parameter state

## 1.0.0 (2021-07-29)

**Features**

  - Model CacheEncryptionSettings has a new parameter rotation_to_latest_key_version_enabled
  - Model CacheIdentity has a new parameter user_assigned_identities
  - Added operation group StorageTargetOperations

**Breaking changes**

  - Operation StorageTargetsOperations.begin_delete has a new signature

## 1.0.0b1 (2021-05-13)

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
