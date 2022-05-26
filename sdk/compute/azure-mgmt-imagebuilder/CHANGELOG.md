# Release History

## 1.1.0 (2022-05-26)

**Features**

  - Model ImageTemplate has a new parameter exact_staging_resource_group
  - Model ImageTemplate has a new parameter staging_resource_group
  - Model ImageTemplate has a new parameter validate
  - Model Resource has a new parameter system_data
  - Model RunOutput has a new parameter system_data
  - Model TrackedResource has a new parameter system_data

## 1.0.0 (2021-12-07)

**Features**

  - Model ImageTemplate has a new parameter system_data
  - Model VirtualNetworkConfig has a new parameter proxy_vm_size
  - Model ImageTemplateVmProfile has a new parameter user_assigned_identities
  - Model ImageTemplatePlatformImageSource has a new parameter exact_version

**Breaking changes**

  - Model Resource no longer has parameter tags
  - Model Resource no longer has parameter location

## 1.0.0b1 (2021-05-25)

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

## 0.4.0 (2020-05-07)

**Features**

  - Model Operation has a new parameter is_data_action
  - Model ImageTemplateSharedImageDistributor has a new parameter exclude_from_latest
  - Model ImageTemplateSharedImageDistributor has a new parameter storage_account_type
  - Model ImageTemplatePlatformImageSource has a new parameter plan_info
  - Model ImageTemplateVmProfile has a new parameter vnet_config
  - Model ImageTemplateVmProfile has a new parameter os_disk_size_gb
  - Added operation VirtualMachineImageTemplatesOperations.cancel

**Breaking changes**

  - Parameter identity of model ImageTemplate is now required

## 0.3.0 (2019-11-19)

**Features**

  - Model ImageTemplatePowerShellCustomizer has a new parameter
    run_elevated
  - Model ImageTemplatePowerShellCustomizer has a new parameter
    sha256_checksum
  - Model ImageTemplate has a new parameter vm_profile
  - Model ImageTemplateFileCustomizer has a new parameter
    sha256_checksum
  - Model ImageTemplateShellCustomizer has a new parameter
    sha256_checksum

**General breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if from some import. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - ImageBuilderClient cannot be imported from
    `azure.mgmt.imagebuilder.image_builder_client` anymore (import
    from `azure.mgmt.imagebuilder` works like before)
  - ImageBuilderClientConfiguration import has been moved from
    `azure.mgmt.imagebuilder.image_builder_client` to
    `azure.mgmt.imagebuilder`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.imagebuilder.models.my_class` (import
    from `azure.mgmt.imagebuilder.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.imagebuilder.operations.my_class_operations` (import
    from `azure.mgmt.imagebuilder.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.2.1 (2019-04-25)

**Bugfixes**

  - Add missing build_timeout_in_minutes
  - Fix some regexp checking

## 0.2.0 (2019-04-12)

  - New API version 2019-05-01-preview

## 0.1.0 (2019-04-09)

  - Initial Release
