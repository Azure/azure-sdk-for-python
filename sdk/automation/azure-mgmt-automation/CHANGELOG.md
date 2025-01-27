# Release History

## 1.1.0b4 (2024-11-05)

### Other Changes

  - Update dependencies

## 1.1.0b3 (2022-12-12)

### Features Added

  - Added operation group DeletedAutomationAccountsOperations
  - Added operation group Python3PackageOperations
  - Model HybridRunbookWorkerGroupCreateOrUpdateParameters has a new parameter name
  - Model Operation has a new parameter origin
  - Model Operation has a new parameter service_specification
  - Model OperationDisplay has a new parameter description

### Breaking Changes

  - Model HybridRunbookWorkerGroup no longer has parameter hybrid_runbook_workers
  - Operation DscConfigurationOperations.create_or_update no longer has parameter content_type
  - Operation DscConfigurationOperations.update no longer has parameter content_type
  - Operation HybridRunbookWorkerGroupOperations.update has a new required parameter hybrid_runbook_worker_group_updation_parameters
  - Operation HybridRunbookWorkerGroupOperations.update no longer has parameter parameters

## 1.1.0b2 (2022-07-18)

**Features**

  - Added operation HybridRunbookWorkerGroupOperations.create
  - Added operation group AutomationClientOperationsMixin
  - Added operation group HybridRunbookWorkersOperations
  - Added operation group PrivateEndpointConnectionsOperations
  - Added operation group PrivateLinkResourcesOperations
  - Model AutomationAccount has a new parameter automation_hybrid_service_url
  - Model AutomationAccount has a new parameter disable_local_auth
  - Model AutomationAccount has a new parameter encryption
  - Model AutomationAccount has a new parameter identity
  - Model AutomationAccount has a new parameter private_endpoint_connections
  - Model AutomationAccount has a new parameter public_network_access
  - Model AutomationAccount has a new parameter system_data
  - Model AutomationAccountCreateOrUpdateParameters has a new parameter disable_local_auth
  - Model AutomationAccountCreateOrUpdateParameters has a new parameter encryption
  - Model AutomationAccountCreateOrUpdateParameters has a new parameter identity
  - Model AutomationAccountCreateOrUpdateParameters has a new parameter public_network_access
  - Model AutomationAccountUpdateParameters has a new parameter disable_local_auth
  - Model AutomationAccountUpdateParameters has a new parameter encryption
  - Model AutomationAccountUpdateParameters has a new parameter identity
  - Model AutomationAccountUpdateParameters has a new parameter public_network_access
  - Model HybridRunbookWorker has a new parameter id
  - Model HybridRunbookWorker has a new parameter registered_date_time
  - Model HybridRunbookWorker has a new parameter system_data
  - Model HybridRunbookWorker has a new parameter type
  - Model HybridRunbookWorker has a new parameter vm_resource_id
  - Model HybridRunbookWorker has a new parameter worker_name
  - Model HybridRunbookWorker has a new parameter worker_type
  - Model HybridRunbookWorkerGroup has a new parameter system_data
  - Model HybridRunbookWorkerGroup has a new parameter type
  - Operation DscConfigurationOperations.create_or_update has a new optional and keyword-only parameter content_type
  - Operation DscConfigurationOperations.update has a new optional and keyword-only parameter content_type

**Breaking changes**

  - Model HybridRunbookWorker no longer has parameter registration_time

## 1.1.0b1 (2021-03-16)

**Features**

  - Model SoftwareUpdateConfigurationCollectionItem has a new parameter tasks

## 1.0.0 (2020-12-17)

- GA release

## 1.0.0b1 (2020-11-11)

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

## 0.1.1 (2019-05-13)

**Bugfixes**

  - Remove incorrect "count_type1" parameter from client signature
    #4965

## 0.1.0 (2019-04-16)

  - Initial Release
