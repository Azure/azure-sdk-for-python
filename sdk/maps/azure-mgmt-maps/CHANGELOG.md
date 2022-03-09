# Release History

## 2.0.0 (2021-05-08)

**Features**

  - Model CreatorUpdateParameters has a new parameter storage_units
  - Model CreatorUpdateParameters has a new parameter provisioning_state
  - Model MapsOperations has a new parameter next_link
  - Model CreatorList has a new parameter next_link
  - Model MapsAccountKeys has a new parameter secondary_key_last_updated
  - Model MapsAccountKeys has a new parameter primary_key_last_updated
  - Model MapsAccount has a new parameter kind
  - Model MapsAccounts has a new parameter next_link

**Breaking changes**

  - Operation AccountsOperations.create_or_update has a new signature
  - Operation CreatorsOperations.create_or_update has a new signature
  - Parameter properties of model Creator is now required
  - Parameter sku of model MapsAccount is now required
  - Model CreatorProperties has a new required parameter storage_units
  - Model MapsAccountKeys no longer has parameter id
  - Model MapsAccountUpdateParameters has a new signature
  - Model MapsAccountProperties has a new signature
  - Removed operation group PrivateAtlasesOperations

## 1.0.0 (2021-04-23)

- GA release

## 1.0.0b1 (2020-12-01)

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

## 0.1.0 (2018-05-07)

  - Initial Release
