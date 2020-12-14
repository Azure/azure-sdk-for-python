# Release History

## 7.0.0b1 (2020-12-07)

This is beta preview version.

This version uses a next-generation code generator that introduces important breaking changes, but also important new features (like unified authentication and async programming).

**General breaking changes**

- Credential system has been completly revamped:

  - `azure.common.credentials` or `msrestazure.azure_active_directory` instances are no longer supported, use the `azure-identity` classes instead: https://pypi.org/project/azure-identity/
  - `credentials` parameter has been renamed `credential`

- The `config` attribute no longer exists on a client, configuration should be passed as kwarg. Example: `MyClient(credential, subscription_id, enable_logging=True)`. For a complete set of
  supported options, see the [parameters accept in init documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)
- You can't import a `version` module anymore, use `__version__` instead
- Operations that used to return a `msrest.polling.LROPoller` now returns a `azure.core.polling.LROPoller` and are prefixed with `begin_`.
- Exceptions tree have been simplified and most exceptions are now `azure.core.exceptions.HttpResponseError` (`CloudError` has been removed).
- Most of the operation kwarg have changed. Some of the most noticeable:

  - `raw` has been removed. Equivalent feature can be found using `cls`, a callback that will give access to internal HTTP response for advanced user
  - For a complete set of
  supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/core/azure-core-tracing-opentelemetry) for an overview.

## 2.0.0 (2020-09-08)

**Features**

  - Model Machine has a new parameter ad_fqdn
  - Model Machine has a new parameter os_sku
  - Model Machine has a new parameter domain_name
  - Model Machine has a new parameter dns_fqdn
  - Model Machine has a new parameter vm_uuid
  - Model MachineProperties has a new parameter ad_fqdn
  - Model MachineProperties has a new parameter os_sku
  - Model MachineProperties has a new parameter domain_name
  - Model MachineProperties has a new parameter dns_fqdn
  - Model MachineProperties has a new parameter vm_uuid

**Breaking changes**

  - Model ErrorResponse has a new signature
  - Model MachineExtensionInstanceViewStatus has a new signature

## 1.0.0 (2020-08-19)

**Features**

  - Model Machine has a new parameter identity
  - Model Machine has a new parameter location_data
  - Model MachineUpdate has a new parameter location_data
  - Added operation group MachineExtensionsOperations

**Breaking changes**

  - Model MachineExtension no longer has parameter tenant_id
  - Model MachineExtension no longer has parameter principal_id
  - Model MachineExtension no longer has parameter type1
  - Model Machine no longer has parameter tenant_id
  - Model Machine no longer has parameter physical_location
  - Model Machine no longer has parameter principal_id
  - Model Machine no longer has parameter type1
  - Model MachineUpdate no longer has parameter physical_location
  - Model Resource no longer has parameter tenant_id
  - Model Resource no longer has parameter principal_id
  - Model Resource no longer has parameter location
  - Model Resource no longer has parameter type1
  - Model Resource no longer has parameter tags
  - Model ErrorResponse has a new signature

## 0.1.1 (2019-10-30)

  - Update project description and title

## 0.1.0 (2019-10-29)

**Breaking changes**

  - Removed MachineExtensionsOperations

## 0.1.0rc1 (2019-10-23)

  - Initial Release
