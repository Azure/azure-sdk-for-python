# Release History

## 1.0.0 (2020-11-23)

## 1.0.0b1 (2020-10-13)

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

## 0.61.0 (2020-08-10)

**Features**

  - Model RoleAssignmentCreateParameters has a new parameter condition
  - Model RoleAssignmentCreateParameters has a new parameter description
  - Model RoleAssignmentCreateParameters has a new parameter condition_version
  - Model RoleAssignment has a new parameter condition
  - Model RoleAssignment has a new parameter description
  - Model RoleAssignment has a new parameter condition_version

## 0.60.0 (2019-06-25)

**Breaking changes**

  - Rename elevate_access.post to global_administrator.elevate_access

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if you were importing from the v20xx_yy_zz
API folders. In summary, some modules were incorrectly
visible/importable and have been renamed. This fixed several issues
caused by usage of classes that were not supposed to be used in the
first place.

  - AuthorizationManagementClient cannot be imported from
    `azure.mgmt.authorization.v20xx_yy_zz.authorization_management_client`
    anymore (import from `azure.mgmt.authorization.v20xx_yy_zz`
    works like before)
  - AuthorizationManagementClientConfiguration import has been moved
    from
    `azure.mgmt.authorization.v20xx_yy_zz.authorization_management_client`
    to `azure.mgmt.authorization.v20xx_yy_zz`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using
    `azure.mgmt.authorization.v20xx_yy_zz.models.my_class` (import
    from `azure.mgmt.authorization.v20xx_yy_zz.models` works like
    before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.authorization.v20xx_yy_zz.operations.my_class_operations`
    (import from `azure.mgmt.authorization.v20xx_yy_zz.operations`
    works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.52.0 (2019-05-23)

**Features**

  - Add elevate_access API

## 0.51.1 (2018-11-27)

**Bugfixes**

  - Missing principal_type in role assignment class #3802

## 0.51.0 (2018-11-12)

**Features**

  - Model RoleAssignmentCreateParameters has a new parameter
    principal_type

**Breaking changes**

  - Parameter role_definition_id of model
    RoleAssignmentCreateParameters is now required
  - Parameter principal_id of model RoleAssignmentCreateParameters is
    now required

Role Assignments API version is now 2018-09-01-preview

## 0.50.0 (2018-05-29)

**Features**

  - Support Azure Stack (multi API versionning)
  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

**Bugfixes**

  - Compatibility of the sdist with wheel 0.31.0

## 0.40.0 (2018-03-13)

**Breaking changes**

  - Several properties have been flattened and "properties" attribute is
    not needed anymore (e.g. properties.email_address =>
    email_address)
  - Some method signature change (e.g. create_by_id)

**Features**

  - Adding attributes data_actions / not_data_actions /
    is_data_actions

API version is now 2018-01-01-preview

## 0.30.0 (2017-04-28)

  - Initial Release
  - This wheel package is built with the azure wheel extension
