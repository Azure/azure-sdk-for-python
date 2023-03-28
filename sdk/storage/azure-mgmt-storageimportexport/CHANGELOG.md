# Release History

## 1.0.0b2 (2022-11-02)

### Features Added

  - Model Export has a new parameter blob_list_blob_path
  - Model JobDetails has a new parameter encryption_key
  - Model JobResponse has a new parameter identity
  - Model JobResponse has a new parameter system_data
  - Model Location has a new parameter additional_shipping_information
  - Model ShippingInformation has a new parameter additional_information

### Breaking Changes

  - Client name is changed from `StorageImportExport` to `StorageImportExport`
  - Model Export no longer has parameter blob_listblob_path
  - Operation BitLockerKeysOperations.list has a new parameter kwargs
  - Operation JobsOperations.create has a new parameter kwargs
  - Operation JobsOperations.delete has a new parameter kwargs
  - Operation JobsOperations.get has a new parameter kwargs
  - Operation JobsOperations.list_by_resource_group has a new parameter kwargs
  - Operation JobsOperations.list_by_subscription has a new parameter kwargs
  - Operation JobsOperations.update has a new parameter kwargs
  - Operation LocationsOperations.get has a new parameter kwargs
  - Operation LocationsOperations.list has a new parameter kwargs
  - Operation Operations.list has a new parameter kwargs

## 1.0.0b1 (2021-05-27)

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


## 0.1.0 (2020-04-11)

* Initial Release
