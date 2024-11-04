# Release History

## 10.0.0 (2024-11-04)

### Features Added

  - Model `Disk` added property `storage_account_id`
  - Enum `HttpStatusCode` added member `AMBIGUOUS`
  - Enum `HttpStatusCode` added member `CONTINUE`
  - Enum `HttpStatusCode` added member `FOUND`
  - Enum `HttpStatusCode` added member `MOVED`
  - Enum `HttpStatusCode` added member `REDIRECT_KEEP_VERB`
  - Enum `HttpStatusCode` added member `REDIRECT_METHOD`
  - Enum `SourceControlType` added member `STORAGE_ACCOUNT`
  - Added enum `ManagedIdentityType`
  - Added model `ServiceRunnerList`

### Breaking Changes

  - Parameter `base_url` of model `DevTestLabsClient` is now required
  - Model `ApplicableScheduleFragment` deleted or renamed its instance variable `lab_vms_shutdown`
  - Model `ApplicableScheduleFragment` deleted or renamed its instance variable `lab_vms_startup`
  - Model `ArtifactSourceFragment` deleted or renamed its instance variable `display_name`
  - Model `ArtifactSourceFragment` deleted or renamed its instance variable `uri`
  - Model `ArtifactSourceFragment` deleted or renamed its instance variable `source_type`
  - Model `ArtifactSourceFragment` deleted or renamed its instance variable `folder_path`
  - Model `ArtifactSourceFragment` deleted or renamed its instance variable `arm_template_folder_path`
  - Model `ArtifactSourceFragment` deleted or renamed its instance variable `branch_ref`
  - Model `ArtifactSourceFragment` deleted or renamed its instance variable `security_token`
  - Model `ArtifactSourceFragment` deleted or renamed its instance variable `status`
  - Model `CustomImageFragment` deleted or renamed its instance variable `vm`
  - Model `CustomImageFragment` deleted or renamed its instance variable `vhd`
  - Model `CustomImageFragment` deleted or renamed its instance variable `description`
  - Model `CustomImageFragment` deleted or renamed its instance variable `author`
  - Model `CustomImageFragment` deleted or renamed its instance variable `managed_image_id`
  - Model `CustomImageFragment` deleted or renamed its instance variable `managed_snapshot_id`
  - Model `CustomImageFragment` deleted or renamed its instance variable `data_disk_storage_info`
  - Model `CustomImageFragment` deleted or renamed its instance variable `custom_image_plan`
  - Model `CustomImageFragment` deleted or renamed its instance variable `is_plan_authorized`
  - Model `DiskFragment` deleted or renamed its instance variable `disk_type`
  - Model `DiskFragment` deleted or renamed its instance variable `disk_size_gi_b`
  - Model `DiskFragment` deleted or renamed its instance variable `leased_by_lab_vm_id`
  - Model `DiskFragment` deleted or renamed its instance variable `disk_blob_name`
  - Model `DiskFragment` deleted or renamed its instance variable `disk_uri`
  - Model `DiskFragment` deleted or renamed its instance variable `host_caching`
  - Model `DiskFragment` deleted or renamed its instance variable `managed_disk_id`
  - Model `DtlEnvironmentFragment` deleted or renamed its instance variable `deployment_properties`
  - Model `DtlEnvironmentFragment` deleted or renamed its instance variable `arm_template_display_name`
  - Model `FormulaFragment` deleted or renamed its instance variable `description`
  - Model `FormulaFragment` deleted or renamed its instance variable `author`
  - Model `FormulaFragment` deleted or renamed its instance variable `os_type`
  - Model `FormulaFragment` deleted or renamed its instance variable `formula_content`
  - Model `FormulaFragment` deleted or renamed its instance variable `vm`
  - Deleted or renamed enum value `HttpStatusCode.CONTINUE_ENUM`
  - Model `LabFragment` deleted or renamed its instance variable `lab_storage_type`
  - Model `LabFragment` deleted or renamed its instance variable `mandatory_artifacts_resource_ids_linux`
  - Model `LabFragment` deleted or renamed its instance variable `mandatory_artifacts_resource_ids_windows`
  - Model `LabFragment` deleted or renamed its instance variable `premium_data_disks`
  - Model `LabFragment` deleted or renamed its instance variable `environment_permission`
  - Model `LabFragment` deleted or renamed its instance variable `announcement`
  - Model `LabFragment` deleted or renamed its instance variable `support`
  - Model `LabFragment` deleted or renamed its instance variable `extended_properties`
  - Parameter `owner_object_id` of model `LabVirtualMachine` is now required
  - Parameter `disallow_public_ip_address` of model `LabVirtualMachine` is now required
  - Parameter `allow_claim` of model `LabVirtualMachine` is now required
  - Parameter `storage_type` of model `LabVirtualMachine` is now required
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `created_by_user_id`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `created_by_user`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `compute_id`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `os_type`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `fqdn`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `artifact_deployment_status`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `virtual_machine_creation_source`
  - Model `LabVirtualMachineCreationParameter` deleted or renamed its instance variable `last_known_power_state`
  - Parameter `owner_object_id` of model `LabVirtualMachineCreationParameter` is now required
  - Parameter `disallow_public_ip_address` of model `LabVirtualMachineCreationParameter` is now required
  - Parameter `allow_claim` of model `LabVirtualMachineCreationParameter` is now required
  - Parameter `storage_type` of model `LabVirtualMachineCreationParameter` is now required
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `notes`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `owner_object_id`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `owner_user_principal_name`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `created_by_user_id`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `created_by_user`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `created_date`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `compute_id`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `custom_image_id`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `os_type`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `size`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `user_name`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `password`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `ssh_key`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `is_authentication_with_ssh_key`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `fqdn`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `lab_subnet_name`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `lab_virtual_network_id`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `disallow_public_ip_address`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `artifacts`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `artifact_deployment_status`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `gallery_image_reference`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `plan_id`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `network_interface`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `expiration_date`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `allow_claim`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `storage_type`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `virtual_machine_creation_source`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `environment_id`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `data_disk_parameters`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `schedule_parameters`
  - Model `LabVirtualMachineFragment` deleted or renamed its instance variable `last_known_power_state`
  - Model `NotificationChannelFragment` deleted or renamed its instance variable `web_hook_url`
  - Model `NotificationChannelFragment` deleted or renamed its instance variable `email_recipient`
  - Model `NotificationChannelFragment` deleted or renamed its instance variable `notification_locale`
  - Model `NotificationChannelFragment` deleted or renamed its instance variable `description`
  - Model `NotificationChannelFragment` deleted or renamed its instance variable `events`
  - Model `PolicyFragment` deleted or renamed its instance variable `description`
  - Model `PolicyFragment` deleted or renamed its instance variable `status`
  - Model `PolicyFragment` deleted or renamed its instance variable `fact_name`
  - Model `PolicyFragment` deleted or renamed its instance variable `fact_data`
  - Model `PolicyFragment` deleted or renamed its instance variable `threshold`
  - Model `PolicyFragment` deleted or renamed its instance variable `evaluator_type`
  - Model `ScheduleFragment` deleted or renamed its instance variable `status`
  - Model `ScheduleFragment` deleted or renamed its instance variable `task_type`
  - Model `ScheduleFragment` deleted or renamed its instance variable `weekly_recurrence`
  - Model `ScheduleFragment` deleted or renamed its instance variable `daily_recurrence`
  - Model `ScheduleFragment` deleted or renamed its instance variable `hourly_recurrence`
  - Model `ScheduleFragment` deleted or renamed its instance variable `time_zone_id`
  - Model `ScheduleFragment` deleted or renamed its instance variable `notification_settings`
  - Model `ScheduleFragment` deleted or renamed its instance variable `target_resource_id`
  - Model `SecretFragment` deleted or renamed its instance variable `value`
  - Model `ServiceFabricFragment` deleted or renamed its instance variable `external_service_fabric_id`
  - Model `ServiceFabricFragment` deleted or renamed its instance variable `environment_id`
  - Model `UserFragment` deleted or renamed its instance variable `identity`
  - Model `UserFragment` deleted or renamed its instance variable `secret_store`
  - Model `VirtualNetworkFragment` deleted or renamed its instance variable `allowed_subnets`
  - Model `VirtualNetworkFragment` deleted or renamed its instance variable `description`
  - Model `VirtualNetworkFragment` deleted or renamed its instance variable `external_provider_resource_id`
  - Model `VirtualNetworkFragment` deleted or renamed its instance variable `subnet_overrides`
  - Deleted or renamed model `ArmTemplateParameterPropertiesFragment`
  - Deleted or renamed model `ArtifactDeploymentStatusPropertiesFragment`
  - Deleted or renamed model `ArtifactInstallPropertiesFragment`
  - Deleted or renamed model `ArtifactParameterPropertiesFragment`
  - Deleted or renamed model `AttachNewDataDiskOptionsFragment`
  - Deleted or renamed model `BulkCreationParametersFragment`
  - Deleted or renamed model `ComputeDataDiskFragment`
  - Deleted or renamed model `ComputeVmInstanceViewStatusFragment`
  - Deleted or renamed model `ComputeVmPropertiesFragment`
  - Deleted or renamed model `CustomImagePropertiesCustomFragment`
  - Deleted or renamed model `CustomImagePropertiesFromPlanFragment`
  - Deleted or renamed model `CustomImagePropertiesFromVmFragment`
  - Deleted or renamed model `DataDiskPropertiesFragment`
  - Deleted or renamed model `DataDiskStorageTypeInfoFragment`
  - Deleted or renamed model `DayDetailsFragment`
  - Deleted or renamed model `EnvironmentDeploymentPropertiesFragment`
  - Deleted or renamed model `EventFragment`
  - Deleted or renamed model `ExternalSubnetFragment`
  - Deleted or renamed model `FormulaPropertiesFromVmFragment`
  - Deleted or renamed model `GalleryImageReferenceFragment`
  - Deleted or renamed model `HourDetailsFragment`
  - Deleted or renamed model `InboundNatRuleFragment`
  - Deleted or renamed model `LabAnnouncementPropertiesFragment`
  - Deleted or renamed model `LabSupportPropertiesFragment`
  - Deleted or renamed model `LabVirtualMachineCreationParameterFragment`
  - Deleted or renamed model `LinuxOsInfoFragment`
  - Deleted or renamed model `NetworkInterfacePropertiesFragment`
  - Deleted or renamed model `NotificationSettingsFragment`
  - Deleted or renamed model `PortFragment`
  - Deleted or renamed model `ScheduleCreationParameterFragment`
  - Deleted or renamed model `SharedPublicIpAddressConfigurationFragment`
  - Deleted or renamed model `SubnetFragment`
  - Deleted or renamed model `SubnetOverrideFragment`
  - Deleted or renamed model `SubnetSharedPublicIpAddressConfigurationFragment`
  - Deleted or renamed model `UserIdentityFragment`
  - Deleted or renamed model `UserSecretStoreFragment`
  - Deleted or renamed model `WeekDetailsFragment`
  - Deleted or renamed model `WindowsOsInfoFragment`
  - Method `ArtifactSourcesOperations.update` deleted or renamed its parameter `artifact_source` of kind `positional_or_keyword`
  - Method `CustomImagesOperations.update` deleted or renamed its parameter `custom_image` of kind `positional_or_keyword`
  - Method `DisksOperations.update` deleted or renamed its parameter `disk` of kind `positional_or_keyword`
  - Method `EnvironmentsOperations.update` deleted or renamed its parameter `dtl_environment` of kind `positional_or_keyword`
  - Method `FormulasOperations.update` deleted or renamed its parameter `formula` of kind `positional_or_keyword`
  - Method `GlobalSchedulesOperations.update` deleted or renamed its parameter `schedule` of kind `positional_or_keyword`
  - Method `LabsOperations.update` deleted or renamed its parameter `lab` of kind `positional_or_keyword`
  - Method `NotificationChannelsOperations.update` deleted or renamed its parameter `notification_channel` of kind `positional_or_keyword`
  - Method `PoliciesOperations.update` deleted or renamed its parameter `policy` of kind `positional_or_keyword`
  - Method `SchedulesOperations.update` deleted or renamed its parameter `schedule` of kind `positional_or_keyword`
  - Method `SecretsOperations.update` deleted or renamed its parameter `value` of kind `positional_or_keyword`
  - Method `ServiceFabricSchedulesOperations.update` deleted or renamed its parameter `schedule` of kind `positional_or_keyword`
  - Method `ServiceFabricsOperations.update` deleted or renamed its parameter `service_fabric` of kind `positional_or_keyword`
  - Method `UsersOperations.update` deleted or renamed its parameter `user` of kind `positional_or_keyword`
  - Method `VirtualMachineSchedulesOperations.update` deleted or renamed its parameter `schedule` of kind `positional_or_keyword`
  - Method `VirtualMachinesOperations.update` deleted or renamed its parameter `lab_virtual_machine` of kind `positional_or_keyword`
  - Method `VirtualNetworksOperations.update` deleted or renamed its parameter `virtual_network` of kind `positional_or_keyword`
  - Operation DisksOperations.update has a new parameter tags
  - Operation DisksOperations.update no longer has parameter disk
  - Operation UsersOperations.update has a new parameter tags
  - Operation UsersOperations.update no longer has parameter user
  - Operation SchedulesOperations.update has a new parameter tags
  - Operation SchedulesOperations.update no longer has parameter schedule
  - Operation GlobalSchedulesOperations.update has a new parameter tags
  - Operation GlobalSchedulesOperations.update no longer has parameter schedule
  - Operation ArtifactSourcesOperations.update has a new parameter tags
  - Operation ArtifactSourcesOperations.update no longer has parameter artifact_source
  - Operation CustomImagesOperations.update has a new parameter tags
  - Operation CustomImagesOperations.update no longer has parameter custom_image
  - Operation VirtualMachinesOperations.update has a new parameter tags
  - Operation VirtualMachinesOperations.update no longer has parameter lab_virtual_machine
  - Operation ServiceFabricsOperations.update has a new parameter tags
  - Operation ServiceFabricsOperations.update no longer has parameter service_fabric
  - Operation VirtualMachineSchedulesOperations.update has a new parameter tags
  - Operation VirtualMachineSchedulesOperations.update no longer has parameter schedule
  - Operation VirtualNetworksOperations.update has a new parameter tags
  - Operation VirtualNetworksOperations.update no longer has parameter virtual_network
  - Operation LabsOperations.update has a new parameter tags
  - Operation LabsOperations.update no longer has parameter lab
  - Operation ServiceFabricSchedulesOperations.update has a new parameter tags
  - Operation ServiceFabricSchedulesOperations.update no longer has parameter schedule
  - Operation PoliciesOperations.update has a new parameter tags
  - Operation PoliciesOperations.update no longer has parameter policy
  - Operation FormulasOperations.update has a new parameter tags
  - Operation FormulasOperations.update no longer has parameter formula
  - Operation EnvironmentsOperations.update has a new parameter tags
  - Operation EnvironmentsOperations.update no longer has parameter dtl_environment
  - Operation NotificationChannelsOperations.update has a new parameter tags
  - Operation NotificationChannelsOperations.update no longer has parameter notification_channel

## 10.0.0b1 (2022-10-28)

### Features Added

  - Model Disk has a new parameter storage_account_id

### Breaking Changes

  - Model ApplicableScheduleFragment no longer has parameter lab_vms_shutdown
  - Model ApplicableScheduleFragment no longer has parameter lab_vms_startup
  - Model ArtifactSourceFragment no longer has parameter arm_template_folder_path
  - Model ArtifactSourceFragment no longer has parameter branch_ref
  - Model ArtifactSourceFragment no longer has parameter display_name
  - Model ArtifactSourceFragment no longer has parameter folder_path
  - Model ArtifactSourceFragment no longer has parameter security_token
  - Model ArtifactSourceFragment no longer has parameter source_type
  - Model ArtifactSourceFragment no longer has parameter status
  - Model ArtifactSourceFragment no longer has parameter uri
  - Model CustomImageFragment no longer has parameter author
  - Model CustomImageFragment no longer has parameter custom_image_plan
  - Model CustomImageFragment no longer has parameter data_disk_storage_info
  - Model CustomImageFragment no longer has parameter description
  - Model CustomImageFragment no longer has parameter is_plan_authorized
  - Model CustomImageFragment no longer has parameter managed_image_id
  - Model CustomImageFragment no longer has parameter managed_snapshot_id
  - Model CustomImageFragment no longer has parameter vhd
  - Model CustomImageFragment no longer has parameter vm
  - Model DiskFragment no longer has parameter disk_blob_name
  - Model DiskFragment no longer has parameter disk_size_gi_b
  - Model DiskFragment no longer has parameter disk_type
  - Model DiskFragment no longer has parameter disk_uri
  - Model DiskFragment no longer has parameter host_caching
  - Model DiskFragment no longer has parameter leased_by_lab_vm_id
  - Model DiskFragment no longer has parameter managed_disk_id
  - Model DtlEnvironmentFragment no longer has parameter arm_template_display_name
  - Model DtlEnvironmentFragment no longer has parameter deployment_properties
  - Model FormulaFragment no longer has parameter author
  - Model FormulaFragment no longer has parameter description
  - Model FormulaFragment no longer has parameter formula_content
  - Model FormulaFragment no longer has parameter os_type
  - Model FormulaFragment no longer has parameter vm
  - Model LabFragment no longer has parameter announcement
  - Model LabFragment no longer has parameter environment_permission
  - Model LabFragment no longer has parameter extended_properties
  - Model LabFragment no longer has parameter lab_storage_type
  - Model LabFragment no longer has parameter mandatory_artifacts_resource_ids_linux
  - Model LabFragment no longer has parameter mandatory_artifacts_resource_ids_windows
  - Model LabFragment no longer has parameter premium_data_disks
  - Model LabFragment no longer has parameter support
  - Model LabVirtualMachineCreationParameter no longer has parameter artifact_deployment_status
  - Model LabVirtualMachineCreationParameter no longer has parameter compute_id
  - Model LabVirtualMachineCreationParameter no longer has parameter created_by_user
  - Model LabVirtualMachineCreationParameter no longer has parameter created_by_user_id
  - Model LabVirtualMachineCreationParameter no longer has parameter fqdn
  - Model LabVirtualMachineCreationParameter no longer has parameter last_known_power_state
  - Model LabVirtualMachineCreationParameter no longer has parameter os_type
  - Model LabVirtualMachineCreationParameter no longer has parameter virtual_machine_creation_source
  - Model LabVirtualMachineFragment no longer has parameter allow_claim
  - Model LabVirtualMachineFragment no longer has parameter artifact_deployment_status
  - Model LabVirtualMachineFragment no longer has parameter artifacts
  - Model LabVirtualMachineFragment no longer has parameter compute_id
  - Model LabVirtualMachineFragment no longer has parameter created_by_user
  - Model LabVirtualMachineFragment no longer has parameter created_by_user_id
  - Model LabVirtualMachineFragment no longer has parameter created_date
  - Model LabVirtualMachineFragment no longer has parameter custom_image_id
  - Model LabVirtualMachineFragment no longer has parameter data_disk_parameters
  - Model LabVirtualMachineFragment no longer has parameter disallow_public_ip_address
  - Model LabVirtualMachineFragment no longer has parameter environment_id
  - Model LabVirtualMachineFragment no longer has parameter expiration_date
  - Model LabVirtualMachineFragment no longer has parameter fqdn
  - Model LabVirtualMachineFragment no longer has parameter gallery_image_reference
  - Model LabVirtualMachineFragment no longer has parameter is_authentication_with_ssh_key
  - Model LabVirtualMachineFragment no longer has parameter lab_subnet_name
  - Model LabVirtualMachineFragment no longer has parameter lab_virtual_network_id
  - Model LabVirtualMachineFragment no longer has parameter last_known_power_state
  - Model LabVirtualMachineFragment no longer has parameter network_interface
  - Model LabVirtualMachineFragment no longer has parameter notes
  - Model LabVirtualMachineFragment no longer has parameter os_type
  - Model LabVirtualMachineFragment no longer has parameter owner_object_id
  - Model LabVirtualMachineFragment no longer has parameter owner_user_principal_name
  - Model LabVirtualMachineFragment no longer has parameter password
  - Model LabVirtualMachineFragment no longer has parameter plan_id
  - Model LabVirtualMachineFragment no longer has parameter schedule_parameters
  - Model LabVirtualMachineFragment no longer has parameter size
  - Model LabVirtualMachineFragment no longer has parameter ssh_key
  - Model LabVirtualMachineFragment no longer has parameter storage_type
  - Model LabVirtualMachineFragment no longer has parameter user_name
  - Model LabVirtualMachineFragment no longer has parameter virtual_machine_creation_source
  - Model NotificationChannelFragment no longer has parameter description
  - Model NotificationChannelFragment no longer has parameter email_recipient
  - Model NotificationChannelFragment no longer has parameter events
  - Model NotificationChannelFragment no longer has parameter notification_locale
  - Model NotificationChannelFragment no longer has parameter web_hook_url
  - Model PolicyFragment no longer has parameter description
  - Model PolicyFragment no longer has parameter evaluator_type
  - Model PolicyFragment no longer has parameter fact_data
  - Model PolicyFragment no longer has parameter fact_name
  - Model PolicyFragment no longer has parameter status
  - Model PolicyFragment no longer has parameter threshold
  - Model ScheduleFragment no longer has parameter daily_recurrence
  - Model ScheduleFragment no longer has parameter hourly_recurrence
  - Model ScheduleFragment no longer has parameter notification_settings
  - Model ScheduleFragment no longer has parameter status
  - Model ScheduleFragment no longer has parameter target_resource_id
  - Model ScheduleFragment no longer has parameter task_type
  - Model ScheduleFragment no longer has parameter time_zone_id
  - Model ScheduleFragment no longer has parameter weekly_recurrence
  - Model SecretFragment no longer has parameter value
  - Model ServiceFabricFragment no longer has parameter environment_id
  - Model ServiceFabricFragment no longer has parameter external_service_fabric_id
  - Model UserFragment no longer has parameter identity
  - Model UserFragment no longer has parameter secret_store
  - Model VirtualNetworkFragment no longer has parameter allowed_subnets
  - Model VirtualNetworkFragment no longer has parameter description
  - Model VirtualNetworkFragment no longer has parameter external_provider_resource_id
  - Model VirtualNetworkFragment no longer has parameter subnet_overrides
  - Operation ArtifactSourcesOperations.update has a new parameter tags
  - Operation ArtifactSourcesOperations.update no longer has parameter artifact_source
  - Operation CustomImagesOperations.update has a new parameter tags
  - Operation CustomImagesOperations.update no longer has parameter custom_image
  - Operation DisksOperations.update has a new parameter tags
  - Operation DisksOperations.update no longer has parameter disk
  - Operation EnvironmentsOperations.update has a new parameter tags
  - Operation EnvironmentsOperations.update no longer has parameter dtl_environment
  - Operation FormulasOperations.update has a new parameter tags
  - Operation FormulasOperations.update no longer has parameter formula
  - Operation GlobalSchedulesOperations.update has a new parameter tags
  - Operation GlobalSchedulesOperations.update no longer has parameter schedule
  - Operation LabsOperations.update has a new parameter tags
  - Operation LabsOperations.update no longer has parameter lab
  - Operation NotificationChannelsOperations.update has a new parameter tags
  - Operation NotificationChannelsOperations.update no longer has parameter notification_channel
  - Operation PoliciesOperations.update has a new parameter tags
  - Operation PoliciesOperations.update no longer has parameter policy
  - Operation SchedulesOperations.update has a new parameter tags
  - Operation SchedulesOperations.update no longer has parameter schedule
  - Operation SecretsOperations.update no longer has parameter value
  - Operation ServiceFabricSchedulesOperations.update has a new parameter tags
  - Operation ServiceFabricSchedulesOperations.update no longer has parameter schedule
  - Operation ServiceFabricsOperations.update has a new parameter tags
  - Operation ServiceFabricsOperations.update no longer has parameter service_fabric
  - Operation UsersOperations.update has a new parameter tags
  - Operation UsersOperations.update no longer has parameter user
  - Operation VirtualMachineSchedulesOperations.update has a new parameter tags
  - Operation VirtualMachineSchedulesOperations.update no longer has parameter schedule
  - Operation VirtualMachinesOperations.update has a new parameter tags
  - Operation VirtualMachinesOperations.update no longer has parameter lab_virtual_machine
  - Operation VirtualNetworksOperations.update has a new parameter tags
  - Operation VirtualNetworksOperations.update no longer has parameter virtual_network

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
