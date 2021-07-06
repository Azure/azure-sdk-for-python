# Release History

## 9.0.0 (2020-12-21)

- GA release

## 9.0.0b1 (2020-10-27)

This is beta preview version.
For detailed changelog please refer to equivalent stable version 4.0.0(https://pypi.org/project/azure-mgmt-devtestlabs/4.0.0/)

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
  - For a complete set of supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry) for an overview.

## 4.0.0 (2019-07-26)

**Breaking changes**

  - Removed operation ServiceRunnersOperations.list

**General breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if from some import. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - DevTestLabsClient cannot be imported from
    `azure.mgmt.devtestlabs.dev_test_labs_management_client`
    anymore (import from `azure.mgmt.devtestlabs` works like before)
  - DevTestLabsManagementClientConfiguration import has been moved from
    `azure.mgmt.devtestlabs.dev_test_labs_management_client` to
    `azure.mgmt.devtestlabs`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.devtestlabs.models.my_class` (import
    from `azure.mgmt.devtestlabs.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.devtestlabs.operations.my_class_operations` (import
    from `azure.mgmt.devtestlabs.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 3.0.0 (2019-02-07)

**Features**

  - Model NotificationChannel has a new parameter email_recipient
  - Model NotificationChannel has a new parameter notification_locale
  - Model ArtifactInstallProperties has a new parameter artifact_title
  - Model GalleryImage has a new parameter plan_id
  - Model GalleryImage has a new parameter is_plan_authorized
  - Model EvaluatePoliciesProperties has a new parameter
    user_object_id
  - Model ArtifactInstallPropertiesFragment has a new parameter
    artifact_title
  - Model Lab has a new parameter announcement
  - Model Lab has a new parameter support
  - Model Lab has a new parameter load_balancer_id
  - Model Lab has a new parameter
    mandatory_artifacts_resource_ids_linux
  - Model Lab has a new parameter extended_properties
  - Model Lab has a new parameter
    mandatory_artifacts_resource_ids_windows
  - Model Lab has a new parameter vm_creation_resource_group
  - Model Lab has a new parameter environment_permission
  - Model Lab has a new parameter network_security_group_id
  - Model Lab has a new parameter public_ip_id
  - Model NotificationSettingsFragment has a new parameter
    email_recipient
  - Model NotificationSettingsFragment has a new parameter
    notification_locale
  - Model LabVirtualMachineCreationParameter has a new parameter
    schedule_parameters
  - Model LabVirtualMachineCreationParameter has a new parameter
    compute_id
  - Model LabVirtualMachineCreationParameter has a new parameter
    data_disk_parameters
  - Model LabVirtualMachineCreationParameter has a new parameter
    last_known_power_state
  - Model LabVirtualMachineCreationParameter has a new parameter
    plan_id
  - Model ShutdownNotificationContent has a new parameter vm_url
  - Model ShutdownNotificationContent has a new parameter
    minutes_until_shutdown
  - Model NotificationSettings has a new parameter email_recipient
  - Model NotificationSettings has a new parameter notification_locale
  - Model LabVirtualMachine has a new parameter plan_id
  - Model LabVirtualMachine has a new parameter schedule_parameters
  - Model LabVirtualMachine has a new parameter
    last_known_power_state
  - Model LabVirtualMachine has a new parameter data_disk_parameters
  - Model ArmTemplate has a new parameter enabled
  - Model CustomImage has a new parameter custom_image_plan
  - Model CustomImage has a new parameter data_disk_storage_info
  - Model CustomImage has a new parameter is_plan_authorized
  - Model CustomImage has a new parameter managed_snapshot_id
  - Model LabVirtualMachineFragment has a new parameter
    schedule_parameters
  - Model LabVirtualMachineFragment has a new parameter compute_id
  - Model LabVirtualMachineFragment has a new parameter
    data_disk_parameters
  - Model LabVirtualMachineFragment has a new parameter
    last_known_power_state
  - Model LabVirtualMachineFragment has a new parameter plan_id
  - Added operation DisksOperations.update
  - Added operation CustomImagesOperations.update
  - Added operation LabsOperations.import_virtual_machine
  - Added operation SecretsOperations.update
  - Added operation EnvironmentsOperations.update
  - Added operation FormulasOperations.update
  - Added operation VirtualMachinesOperations.transfer_disks
  - Added operation VirtualMachinesOperations.un_claim
  - Added operation VirtualMachinesOperations.resize
  - Added operation VirtualMachinesOperations.restart
  - Added operation VirtualMachinesOperations.get_rdp_file_contents
  - Added operation VirtualMachinesOperations.redeploy
  - Added operation group ServiceFabricsOperations
  - Added operation group ServiceFabricSchedulesOperations

**Breaking changes**

  - Model VirtualNetworkFragment no longer has parameter type
  - Model VirtualNetworkFragment no longer has parameter id
  - Model VirtualNetworkFragment no longer has parameter location
  - Model VirtualNetworkFragment no longer has parameter name
  - Model VirtualNetworkFragment no longer has parameter
    external_subnets
  - Model VirtualNetworkFragment no longer has parameter
    provisioning_state
  - Model VirtualNetworkFragment no longer has parameter
    unique_identifier
  - Model PolicyFragment no longer has parameter type
  - Model PolicyFragment no longer has parameter id
  - Model PolicyFragment no longer has parameter location
  - Model PolicyFragment no longer has parameter name
  - Model PolicyFragment no longer has parameter unique_identifier
  - Model PolicyFragment no longer has parameter provisioning_state
  - Model ArtifactSourceFragment no longer has parameter type
  - Model ArtifactSourceFragment no longer has parameter id
  - Model ArtifactSourceFragment no longer has parameter location
  - Model ArtifactSourceFragment no longer has parameter name
  - Model ArtifactSourceFragment no longer has parameter
    unique_identifier
  - Model ArtifactSourceFragment no longer has parameter
    provisioning_state
  - Model LabVirtualMachineCreationParameter no longer has parameter
    applicable_schedule
  - Model LabVirtualMachineCreationParameter no longer has parameter
    compute_vm
  - Model LabVirtualMachineCreationParameter no longer has parameter
    unique_identifier
  - Model LabVirtualMachineCreationParameter no longer has parameter
    provisioning_state
  - Model ApplicableScheduleFragment no longer has parameter location
  - Model ApplicableScheduleFragment no longer has parameter type
  - Model ApplicableScheduleFragment no longer has parameter id
  - Model ApplicableScheduleFragment no longer has parameter name
  - Model ScheduleFragment no longer has parameter type
  - Model ScheduleFragment no longer has parameter id
  - Model ScheduleFragment no longer has parameter location
  - Model ScheduleFragment no longer has parameter name
  - Model ScheduleFragment no longer has parameter unique_identifier
  - Model ScheduleFragment no longer has parameter provisioning_state
  - Model LabVirtualMachineFragment no longer has parameter type
  - Model LabVirtualMachineFragment no longer has parameter id
  - Model LabVirtualMachineFragment no longer has parameter compute_vm
  - Model LabVirtualMachineFragment no longer has parameter location
  - Model LabVirtualMachineFragment no longer has parameter name
  - Model LabVirtualMachineFragment no longer has parameter
    unique_identifier
  - Model LabVirtualMachineFragment no longer has parameter
    provisioning_state
  - Model LabVirtualMachineFragment no longer has parameter
    applicable_schedule
  - Model LabFragment has a new signature
  - Model UserFragment has a new signature
  - Model NotificationChannelFragment has a new signature

## 2.2.0 (2018-02-15)

  - Add "providers" operation group

## 2.1.0 (2017-10-25)

  - Add "operations" operation group

## 2.0.0 (2017-04-27)

  - Major refactoring to follow name conventions + new features.
  - This wheel package is now built with the azure wheel extension

## 1.0.0 (2016-09-13)

  - Initial Release
