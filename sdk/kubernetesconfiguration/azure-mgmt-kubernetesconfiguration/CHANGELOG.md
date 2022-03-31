# Release History

## 2.0.0 (2022-03-31)

**Features**

  - Model Extension has a new parameter installed_version
  - Model FluxConfiguration has a new parameter source_synced_commit_id
  - Model FluxConfiguration has a new parameter source_updated_at
  - Model FluxConfiguration has a new parameter status_updated_at
  - Model KustomizationDefinition has a new parameter name

**Breaking changes**

  - Model FluxConfiguration no longer has parameter last_source_updated_at
  - Model FluxConfiguration no longer has parameter last_source_updated_commit_id

## 1.0.0 (2021-12-06)

**Features**

  - Model ResourceProviderOperation has a new parameter origin
  - Added operation group LocationExtensionTypesOperations
  - Added operation group FluxConfigurationsOperations
  - Added operation group ExtensionsOperations
  - Added operation group OperationStatusOperations
  - Added operation group ClusterExtensionTypeOperations
  - Added operation group FluxConfigOperationStatusOperations
  - Added operation group ClusterExtensionTypesOperations
  - Added operation group ExtensionTypeVersionsOperations

**Breaking changes**

  - Model Resource no longer has parameter system_data
  - Model ProxyResource no longer has parameter system_data

## 1.0.0b1 (2020-12-09)

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

## 0.2.0 (2020-05-12)

**Breaking changes**

  - Operation SourceControlConfigurationsOperations.list has a new signature
  - Operation SourceControlConfigurationsOperations.get has a new signature
  - Operation SourceControlConfigurationsOperations.delete has a new signature
  - Operation SourceControlConfigurationsOperations.create_or_update has a new signature
  - Operation Operations.list has a new signature

## 0.1.0 (2020-04-10)

* Initial Release
