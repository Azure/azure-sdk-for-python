# Release History

## 7.0.0 (2024-11-04)

### Features Added

  - Client `ManagedServicesClient` added operation group `operations_with_scope`
  - Model `JustInTimeAccessPolicy` added property `managed_by_tenant_approvers`
  - Model `RegistrationAssignment` added property `system_data`
  - Model `RegistrationAssignmentPropertiesRegistrationDefinition` added property `system_data`
  - Model `RegistrationDefinition` added property `system_data`
  - Model `RegistrationDefinitionProperties` added property `managee_tenant_id`
  - Model `RegistrationDefinitionProperties` added property `managee_tenant_name`
  - Added enum `CreatedByType`
  - Added model `EligibleApprover`
  - Added model `SystemData`
  - Model `MarketplaceRegistrationDefinitionsOperations` added parameter `kwargs` in method `__init__`
  - Model `MarketplaceRegistrationDefinitionsWithoutScopeOperations` added parameter `kwargs` in method `__init__`
  - Model `Operations` added parameter `kwargs` in method `__init__`
  - Model `RegistrationAssignmentsOperations` added parameter `kwargs` in method `__init__`
  - Model `RegistrationDefinitionsOperations` added parameter `kwargs` in method `__init__`
  - Added model `OperationsWithScopeOperations`
  - Method `RegistrationAssignmentsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, scope: str, registration_assignment_id: str, request_body: RegistrationAssignment, content_type: str)`
  - Method `RegistrationAssignmentsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, scope: str, registration_assignment_id: str, request_body: IO[bytes], content_type: str)`
  - Method `RegistrationDefinitionsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, registration_definition_id: str, scope: str, request_body: RegistrationDefinition, content_type: str)`
  - Method `RegistrationDefinitionsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, registration_definition_id: str, scope: str, request_body: IO[bytes], content_type: str)`

### Breaking Changes

  - Method `ManagedServicesClient.__init__` parameter `base_url` changed default value from `None` to `str`
  - Method `JustInTimeAccessPolicy.__init__` parameter `maximum_activation_duration` changed default value from `None` to `str`

## 7.0.0b1 (2022-10-31)

### Features Added

  - Added operation group OperationsWithScopeOperations
  - Model JustInTimeAccessPolicy has a new parameter managed_by_tenant_approvers
  - Model RegistrationAssignment has a new parameter system_data
  - Model RegistrationAssignmentPropertiesRegistrationDefinition has a new parameter system_data
  - Model RegistrationDefinition has a new parameter system_data
  - Model RegistrationDefinitionProperties has a new parameter managee_tenant_id
  - Model RegistrationDefinitionProperties has a new parameter managee_tenant_name

### Breaking Changes

  - Operation RegistrationAssignmentsOperations.list has a new parameter filter
  - Operation RegistrationDefinitionsOperations.list has a new parameter filter

## 6.0.0 (2021-04-22)

**Features**

  - Added operation group MarketplaceRegistrationDefinitionsWithoutScopeOperations

## 6.0.0b1 (2020-12-07)

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

## 1.0.0 (2019-07-05)

  - GA Release

## 0.1.0 (2019-05-14)

  - Initial Release
