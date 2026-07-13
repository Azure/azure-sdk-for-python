# Release History

## 1.0.0b7 (2026-07-07)

### Features Added

  - Client `SqlVirtualMachineManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `SqlVirtualMachineManagementClient` added method `send_request`
  - Model `AutoPatchingSettings` added property `additional_vm_patch`
  - Model `AvailabilityGroupListener` moved instance variable `provisioning_state`, `availability_group_name`, `load_balancer_configurations`, `multi_subnet_ip_configurations`, `create_default_availability_group_if_not_exist`, `port` and `availability_group_configuration` under property `properties` whose type is `AvailabilityGroupListenerProperties`
  - Enum `IdentityType` added member `SYSTEM_ASSIGNED_USER_ASSIGNED`
  - Enum `IdentityType` added member `USER_ASSIGNED`
  - Model `ProxyResource` added property `system_data`
  - Model `Resource` added property `system_data`
  - Model `SQLStorageSettings` added property `use_storage_pool`
  - Model `SQLTempDbSettings` added property `use_storage_pool`
  - Model `SqlVirtualMachine` moved instance variable `virtual_machine_resource_id`, `provisioning_state`, `sql_image_offer`, `sql_server_license_type`, `sql_management`, `least_privilege_mode`, `sql_image_sku`, `sql_virtual_machine_group_resource_id`, `wsfc_domain_credentials`, `wsfc_static_ip`, `auto_patching_settings`, `auto_backup_settings`, `key_vault_credential_settings`, `server_configurations_management_settings`, `storage_configuration_settings`, `troubleshooting_status`, `assessment_settings` and `enable_automatic_upgrade` under property `properties` whose type is `SqlVirtualMachineProperties`
  - Model `SqlVirtualMachineGroup` moved instance variable `provisioning_state`, `sql_image_offer`, `sql_image_sku`, `scale_type`, `cluster_manager_type`, `cluster_configuration` and `wsfc_domain_profile` under property `properties` whose type is `SqlVirtualMachineGroupProperties`
  - Model `StorageConfigurationSettings` added property `enable_storage_config_blade`
  - Model `TrackedResource` added property `system_data`
  - Model `WsfcDomainProfile` added property `is_sql_service_account_gmsa`
  - Added enum `AdditionalOsPatch`
  - Added enum `AdditionalVmPatch`
  - Added model `DiskConfigAssessmentRequest`
  - Added enum `OsType`
  - Added model `VirtualMachineIdentity`
  - Added enum `VmIdentityType`
  - Operation group `SqlVirtualMachinesOperations` added method `begin_fetch_dc_assessment`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - Method `AvailabilityGroupListenersOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `SqlVirtualMachinesOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`

### Other Changes

  - Deleted model `AvailabilityGroupListenerListResult`/`OperationListResult`/`SqlVirtualMachineGroupListResult`/`SqlVirtualMachineListResult` which actually were not used by SDK users

## 1.0.0b6 (2023-06-16)

### Other Changes

  - Regular release

## 1.0.0b5 (2023-01-17)

### Features Added

  - Added operation group SqlVirtualMachineTroubleshootOperations
  - Model ServerConfigurationsManagementSettings has a new parameter azure_ad_authentication_settings
  - Model SqlVirtualMachine has a new parameter troubleshooting_status

## 1.0.0b4 (2022-09-26)

### Features Added

  - Model AvailabilityGroupListener has a new parameter multi_subnet_ip_configurations
  - Model SQLInstanceSettings has a new parameter is_ifi_enabled
  - Model SQLInstanceSettings has a new parameter is_lpim_enabled
  - Model SQLTempDbSettings has a new parameter persist_folder
  - Model SQLTempDbSettings has a new parameter persist_folder_path
  - Model SqlVirtualMachine has a new parameter enable_automatic_upgrade
  - Model SqlVirtualMachine has a new parameter least_privilege_mode
  - Model SqlVirtualMachine has a new parameter wsfc_static_ip
  - Model WsfcDomainProfile has a new parameter cluster_subnet_type

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
