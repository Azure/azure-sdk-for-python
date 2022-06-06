# Release History

## 1.0.0b3 (2022-06-06)

**Features**

  - Added model AssessmentDayOfWeek
  - Added model AutoBackupDaysOfWeek

## 1.0.0b2 (2022-03-02)

**Features**

  - Added operation SqlVirtualMachinesOperations.begin_redeploy
  - Added operation SqlVirtualMachinesOperations.begin_start_assessment
  - Model AutoBackupSettings has a new parameter days_of_week
  - Model AutoBackupSettings has a new parameter storage_container_name
  - Model AvailabilityGroupListener has a new parameter availability_group_configuration
  - Model AvailabilityGroupListener has a new parameter system_data
  - Model ServerConfigurationsManagementSettings has a new parameter sql_instance_settings
  - Model SqlVirtualMachine has a new parameter assessment_settings
  - Model SqlVirtualMachine has a new parameter system_data
  - Model SqlVirtualMachineGroup has a new parameter system_data
  - Model StorageConfigurationSettings has a new parameter sql_system_db_on_data_disk

**Breaking changes**

  - Operation AvailabilityGroupListenersOperations.get has a new signature

## 1.0.0b1 (2021-05-19)

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

## 0.5.0 (2019-11-27)

**Features**

  - Model SqlVirtualMachine has a new parameter
    storage_configuration_settings
  - Added operation
    SqlVirtualMachinesOperations.list_by_sql_vm_group

## 0.4.0 (2019-07-04)

**Features**

  - Model SqlVirtualMachine has a new parameter sql_management

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if from some import. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - SqlVirtualMachineManagementClient cannot be imported from
    `azure.mgmt.sqlvirtualmachine.sql_virtual_machine_management_client`
    anymore (import from `azure.mgmt.sqlvirtualmachine` works like
    before)
  - SqlVirtualMachineManagementClientConfiguration import has been moved
    from
    `azure.mgmt.sqlvirtualmachine.sql_virtual_machine_management_client`
    to `azure.mgmt.sqlvirtualmachine`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.sqlvirtualmachine.models.my_class`
    (import from `azure.mgmt.sqlvirtualmachine.models` works like
    before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.sqlvirtualmachine.operations.my_class_operations`
    (import from `azure.mgmt.sqlvirtualmachine.operations` works like
    before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.3.0 (2019-06-03)

**Features**

  - sql_image_sku is now writable

## 0.2.0 (2018-12-07)

**Features**

  - Model SqlStorageUpdateSettings has a new parameter
    starting_device_id

**Breaking changes**

  - Model AdditionalFeaturesServerConfigurations no longer has parameter
    backup_permissions_for_azure_backup_svc

## 0.1.0 (2018-11-27)

  - Initial Release
