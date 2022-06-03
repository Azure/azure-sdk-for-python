# Release History

## 2.0.0b1 (2022-03-14)

**Features**

  - Added operation LabsOperations.begin_create_or_update
  - Added operation LabsOperations.begin_publish
  - Added operation LabsOperations.begin_sync_group
  - Added operation LabsOperations.begin_update
  - Added operation LabsOperations.list_by_resource_group
  - Added operation LabsOperations.list_by_subscription
  - Added operation Operations.list
  - Added operation UsersOperations.begin_create_or_update
  - Added operation UsersOperations.begin_invite
  - Added operation UsersOperations.begin_update
  - Added operation UsersOperations.list_by_lab
  - Added operation group ImagesOperations
  - Added operation group LabPlansOperations
  - Added operation group OperationResultsOperations
  - Added operation group SchedulesOperations
  - Added operation group SkusOperations
  - Added operation group UsagesOperations
  - Added operation group VirtualMachinesOperations
  - Model Lab has a new parameter auto_shutdown_profile
  - Model Lab has a new parameter connection_profile
  - Model Lab has a new parameter description
  - Model Lab has a new parameter lab_plan_id
  - Model Lab has a new parameter network_profile
  - Model Lab has a new parameter roster_profile
  - Model Lab has a new parameter security_profile
  - Model Lab has a new parameter state
  - Model Lab has a new parameter system_data
  - Model Lab has a new parameter title
  - Model Lab has a new parameter virtual_machine_profile
  - Model OperationResult has a new parameter end_time
  - Model OperationResult has a new parameter id
  - Model OperationResult has a new parameter name
  - Model OperationResult has a new parameter percent_complete
  - Model OperationResult has a new parameter start_time
  - Model User has a new parameter additional_usage_quota
  - Model User has a new parameter display_name
  - Model User has a new parameter invitation_sent
  - Model User has a new parameter invitation_state
  - Model User has a new parameter registration_state
  - Model User has a new parameter system_data

**Breaking changes**

  - Model Lab no longer has parameter created_by_object_id
  - Model Lab no longer has parameter created_by_user_principal_name
  - Model Lab no longer has parameter created_date
  - Model Lab no longer has parameter invitation_code
  - Model Lab no longer has parameter latest_operation_result
  - Model Lab no longer has parameter max_users_in_lab
  - Model Lab no longer has parameter unique_identifier
  - Model Lab no longer has parameter usage_quota
  - Model Lab no longer has parameter user_access_mode
  - Model Lab no longer has parameter user_quota
  - Model Resource no longer has parameter location
  - Model Resource no longer has parameter tags
  - Model User no longer has parameter family_name
  - Model User no longer has parameter given_name
  - Model User no longer has parameter latest_operation_result
  - Model User no longer has parameter location
  - Model User no longer has parameter tags
  - Model User no longer has parameter tenant_id
  - Model User no longer has parameter unique_identifier
  - Operation LabsOperations.begin_delete has a new signature
  - Operation LabsOperations.get has a new signature
  - Operation LabsOperations.get has a new signature
  - Operation UsersOperations.begin_delete has a new signature
  - Operation UsersOperations.get has a new signature
  - Operation UsersOperations.get has a new signature
  - Parameter email of model User is now required
  - Parameter email of model User is now required
  - Parameter location of model Lab is now required
  - Parameter status of model OperationResult is now required
  - Removed operation LabsOperations.add_users
  - Removed operation LabsOperations.create_or_update
  - Removed operation LabsOperations.list
  - Removed operation LabsOperations.register
  - Removed operation LabsOperations.update
  - Removed operation Operations.get
  - Removed operation UsersOperations.create_or_update
  - Removed operation UsersOperations.list
  - Removed operation UsersOperations.update
  - Removed operation group EnvironmentSettingsOperations
  - Removed operation group EnvironmentsOperations
  - Removed operation group GalleryImagesOperations
  - Removed operation group GlobalUsersOperations
  - Removed operation group LabAccountsOperations
  - Removed operation group ProviderOperationsOperations

## 1.0.0 (2021-03-31)

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

## 0.1.1 (2019-02-14)

Bug fix: Fixed an enum comment's erroneous wrap around

## 0.1.0 (2019-02-11)

  - Initial Release
