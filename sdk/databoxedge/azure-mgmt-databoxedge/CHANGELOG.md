# Release History

## 3.0.0 (2026-07-13)

### Features Added

  - Client `DataBoxEdgeManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `DataBoxEdgeManagementClient` added method `send_request`
  - Client `DataBoxEdgeManagementClient` added operation group `device_capacity_check`
  - Client `DataBoxEdgeManagementClient` added operation group `device_capacity_info`
  - Client `DataBoxEdgeManagementClient` added operation group `diagnostic_settings`
  - Client `DataBoxEdgeManagementClient` added operation group `support_packages`
  - Model `DataBoxEdgeDeviceExtendedInfo` added property `system_data`
  - Model `Job` added property `system_data`
  - Model `LoadBalancerConfig` added property `ip_range`
  - Model `Order` added property `kind`
  - Enum `SkuName` added member `EDGE_MR_TCP`
  - Enum `SkuName` added member `EP2_128_GPU1_MX1_W`
  - Enum `SkuName` added member `EP2_256_GPU2_MX1`
  - Enum `SkuName` added member `EP2_64_MX1_W`
  - Model `UpdateDetails` added property `friendly_version_number`
  - Model `UpdateDetails` added property `installation_impact`
  - Added enum `AccessLevel`
  - Added model `CloudError`
  - Added model `ClusterCapacityViewData`
  - Added model `ClusterGpuCapacity`
  - Added model `ClusterMemoryCapacity`
  - Added model `ClusterStorageViewData`
  - Added enum `ClusterWitnessType`
  - Added model `DataResidency`
  - Added enum `DataResidencyType`
  - Added model `DeviceCapacityInfo`
  - Added model `DeviceCapacityInfoProperties`
  - Added model `DeviceCapacityRequestInfo`
  - Added model `DeviceCapacityRequestInfoProperties`
  - Added model `DiagnosticProactiveLogCollectionSettings`
  - Added model `DiagnosticRemoteSupportSettings`
  - Added model `DiagnosticRemoteSupportSettingsProperties`
  - Added model `HostCapacity`
  - Added enum `InstallationImpact`
  - Added model `NumaNodeData`
  - Added enum `ProactiveDiagnosticsConsent`
  - Added model `ProactiveLogCollectionSettingsProperties`
  - Added model `ProxyResource`
  - Added enum `RemoteApplicationType`
  - Added model `RemoteSupportSettings`
  - Added model `Resource`
  - Added model `SupportPackageRequestProperties`
  - Added model `TrackedResource`
  - Added model `TriggerSupportPackageRequest`
  - Added model `VmMemory`
  - Added model `VmPlacementRequestResult`
  - Operation group `DevicesOperations` added method `create_or_update`
  - Added operation group `DeviceCapacityCheckOperations`
  - Added operation group `DeviceCapacityInfoOperations`
  - Added operation group `DiagnosticSettingsOperations`
  - Added operation group `SupportPackagesOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Model `Alert` moved instance variables `alert_type`, `appeared_at_date_time`, `detailed_information`, `error_details`, `recommendation`, `severity` and `title` under property `properties` whose type is `AlertProperties`
  - Model `ArcAddon` moved instance variables `host_platform`, `host_platform_type`, `provisioning_state`, `resource_group_name`, `resource_location`, `resource_name`, `subscription_id` and `version` under property `properties` whose type is `ArcAddonProperties`
  - Model `BandwidthSchedule` moved instance variables `days`, `rate_in_mbps`, `start` and `stop` under property `properties` whose type is `BandwidthScheduleProperties`
  - Model `CloudEdgeManagementRole` moved instance variables `edge_profile`, `local_management_status` and `role_status` under property `properties` whose type is `CloudEdgeManagementRoleProperties`
  - Model `Container` moved instance variables `container_status`, `created_date_time`, `data_format` and `refresh_details` under property `properties` whose type is `ContainerProperties`
  - Model `DCAccessCode` moved instance variable `auth_code` under property `properties` whose type is `DCAccessCodeProperties`
  - Model `DataBoxEdgeDevice` moved instance variables `configured_role_types`, `culture`, `data_box_edge_device_status`, `description`, `device_hcs_version`, `device_local_capacity`, `device_model`, `device_software_version`, `device_type`, `edge_profile`, `friendly_name`, `model_description`, `node_count`, `resource_move_details`, `serial_number` and `time_zone` under property `properties` whose type is `DataBoxEdgeDeviceProperties`
  - Model `DataBoxEdgeDeviceExtendedInfo` moved instance variables `channel_integrity_key_name`, `channel_integrity_key_version`, `client_secret_store_id`, `client_secret_store_url`, `device_secrets`, `encryption_key`, `encryption_key_thumbprint`, `key_vault_sync_status` and `resource_key` under property `properties` whose type is `DataBoxEdgeDeviceExtendedInfoProperties`
  - Model `DataBoxEdgeDevicePatch` moved instance variable `edge_profile` under property `properties` whose type is `DataBoxEdgeDevicePropertiesPatch`
  - Model `EdgeProfileSubscription` moved instance variables `location_placement_id`, `quota_id`, `registered_features`, `serialized_details` and `tenant_id` under property `properties` whose type is `SubscriptionProperties`
  - Model `FileEventTrigger` moved instance variables `custom_context_tag`, `sink_info` and `source_info` under property `properties` whose type is `FileTriggerProperties`
  - Model `IoTAddon` moved instance variables `host_platform`, `host_platform_type`, `io_t_device_details`, `io_t_edge_device_details`, `provisioning_state` and `version` under property `properties` whose type is `IoTAddonProperties`
  - Model `IoTRole` moved instance variables `compute_resource`, `host_platform`, `host_platform_type`, `io_t_device_details`, `io_t_edge_agent_info`, `io_t_edge_device_details`, `role_status` and `share_mappings` under property `properties` whose type is `IoTRoleProperties`
  - Model `Job` moved instance variables `current_stage`, `download_progress`, `error_manifest_file`, `folder`, `install_progress`, `job_type`, `refreshed_entity_id` and `total_refresh_errors` under property `properties` whose type is `JobProperties`
  - Model `KubernetesRole` moved instance variables `host_platform`, `host_platform_type`, `kubernetes_cluster_info`, `kubernetes_role_resources`, `provisioning_state` and `role_status` under property `properties` whose type is `KubernetesRoleProperties`
  - Model `MECRole` moved instance variables `connection_string`, `controller_endpoint`, `resource_unique_id` and `role_status` under property `properties` whose type is `MECRoleProperties`
  - Model `MonitoringMetricConfiguration` moved instance variable `metric_configurations` under property `properties` whose type is `MonitoringMetricConfigurationProperties`
  - Model `NetworkSettings` moved instance variable `network_adapters` under property `properties` whose type is `NetworkSettingsProperties`
  - Model `Node` moved instance variables `node_chassis_serial_number`, `node_display_name`, `node_friendly_software_version`, `node_hcs_version`, `node_instance_id`, `node_serial_number` and `node_status` under property `properties` whose type is `NodeProperties`
  - Model `Operation` moved instance variable `service_specification` under property `properties` whose type is `OperationProperties`
  - Model `Order` moved instance variables `contact_information`, `current_status`, `delivery_tracking_info`, `order_history`, `return_tracking_info`, `serial_number`, `shipment_type` and `shipping_address` under property `properties` whose type is `OrderProperties`
  - Model `PeriodicTimerEventTrigger` moved instance variables `custom_context_tag`, `sink_info` and `source_info` under property `properties` whose type is `PeriodicTimerProperties`
  - Model `SecuritySettings` moved instance variable `device_admin_password` under property `properties` whose type is `SecuritySettingsProperties`
  - Model `Share` moved instance variables `access_protocol`, `azure_container_info`, `client_access_rights`, `data_policy`, `description`, `monitoring_status`, `refresh_details`, `share_mappings`, `share_status` and `user_access_rights` under property `properties` whose type is `ShareProperties`
  - Model `StorageAccount` moved instance variables `blob_endpoint`, `container_count`, `data_policy`, `description`, `storage_account_credential_id` and `storage_account_status` under property `properties` whose type is `StorageAccountProperties`
  - Model `StorageAccountCredential` moved instance variables `account_key`, `account_type`, `alias`, `blob_domain_name`, `connection_string`, `ssl_status`, `storage_account_id` and `user_name` under property `properties` whose type is `StorageAccountCredentialProperties`
  - Model `UpdateSummary` moved instance variables `device_last_scanned_date_time`, `device_version_number`, `friendly_device_version_name`, `in_progress_download_job_id`, `in_progress_download_job_started_date_time`, `in_progress_install_job_id`, `in_progress_install_job_started_date_time`, `last_completed_download_job_date_time`, `last_completed_download_job_id`, `last_completed_install_job_date_time`, `last_completed_install_job_id`, `last_completed_scan_job_date_time`, `last_download_job_status`, `last_install_job_status`, `ongoing_update_operation`, `reboot_behavior`, `total_number_of_updates_available`, `total_number_of_updates_pending_download`, `total_number_of_updates_pending_install`, `total_time_in_minutes`, `total_update_size_in_bytes`, `update_titles` and `updates` under property `properties` whose type is `UpdateSummaryProperties`
  - Model `UploadCertificateRequest` moved instance variables `authentication_type` and `certificate` under property `properties` whose type is `RawCertificateData`
  - Model `User` moved instance variables `encrypted_password`, `share_access_rights` and `user_type` under property `properties` whose type is `UserProperties`
  - Method `DevicesOperations.list_by_resource_group` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `DevicesOperations.list_by_subscription` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Renamed method `DevicesOperations.begin_create_or_update` to `create_or_update`
  - Method `UsersOperations.list_by_data_box_edge_device` renamed its parameter `expand` to `filter`

### Other Changes

  - Deleted model `AddonList`/`AlertList`/`BandwidthSchedulesList`/`ContainerList`/`DataBoxEdgeDeviceList`/`DataBoxEdgeSkuList`/`MonitoringMetricConfigurationList`/`NodeList`/`OperationsList`/`OrderList`/`RoleList`/`ShareList`/`SkuInformationList`/`StorageAccountCredentialList`/`StorageAccountList`/`TriggerList`/`UserList` which actually were not used by SDK users
  - Deleted model `DataBoxEdgeMoveRequest`/`ResourceTypeSku`/`SkuInformation` which actually were not used by SDK users

## 3.0.0b2 (2026-05-26)

### Features Added

  - Client `DataBoxEdgeManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `DataBoxEdgeManagementClient` added method `send_request`
  - Client `DataBoxEdgeManagementClient` added operation group `diagnostic_settings`
  - Client `DataBoxEdgeManagementClient` added operation group `device_capacity_check`
  - Client `DataBoxEdgeManagementClient` added operation group `support_packages`
  - Client `DataBoxEdgeManagementClient` added operation group `device_capacity_info`
  - Model `DataBoxEdgeDeviceExtendedInfo` added property `system_data`
  - Model `Job` added property `system_data`
  - Model `LoadBalancerConfig` added property `ip_range`
  - Model `Order` added property `kind`
  - Enum `SkuName` added member `EDGE_MR_TCP`
  - Enum `SkuName` added member `EP2_128_GPU1_MX1_W`
  - Enum `SkuName` added member `EP2_256_GPU2_MX1`
  - Enum `SkuName` added member `EP2_64_MX1_W`
  - Model `UpdateDetails` added property `friendly_version_number`
  - Model `UpdateDetails` added property `installation_impact`
  - Added enum `AccessLevel`
  - Added model `CloudError`
  - Added model `ClusterCapacityViewData`
  - Added model `ClusterGpuCapacity`
  - Added model `ClusterMemoryCapacity`
  - Added model `ClusterStorageViewData`
  - Added enum `ClusterWitnessType`
  - Added model `DataResidency`
  - Added enum `DataResidencyType`
  - Added model `DeviceCapacityInfo`
  - Added model `DeviceCapacityInfoProperties`
  - Added model `DeviceCapacityRequestInfo`
  - Added model `DeviceCapacityRequestInfoProperties`
  - Added model `DiagnosticProactiveLogCollectionSettings`
  - Added model `DiagnosticRemoteSupportSettings`
  - Added model `DiagnosticRemoteSupportSettingsProperties`
  - Added model `HostCapacity`
  - Added enum `InstallationImpact`
  - Added model `NumaNodeData`
  - Added enum `ProactiveDiagnosticsConsent`
  - Added model `ProactiveLogCollectionSettingsProperties`
  - Added model `ProxyResource`
  - Added enum `RemoteApplicationType`
  - Added model `RemoteSupportSettings`
  - Added model `Resource`
  - Added model `SupportPackageRequestProperties`
  - Added model `TrackedResource`
  - Added model `TriggerSupportPackageRequest`
  - Added model `VmMemory`
  - Added model `VmPlacementRequestResult`
  - Operation group `DevicesOperations` added method `create_or_update`
  - Added operation group `DeviceCapacityCheckOperations`
  - Added operation group `DeviceCapacityInfoOperations`
  - Added operation group `DiagnosticSettingsOperations`
  - Added operation group `SupportPackagesOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - Model `DCAccessCode` moved instance variable `auth_code` under property `properties` whose type is `DCAccessCodeProperties`
  - Model `DataBoxEdgeDevicePatch` moved instance variable `edge_profile` under property `properties` whose type is `DataBoxEdgeDevicePropertiesPatch`
  - Model `EdgeProfileSubscription` moved instance variable `tenant_id`, `location_placement_id`, `quota_id`, `serialized_details` and `registered_features` under property `properties` whose type is `SubscriptionProperties`
  - Model `FileEventTrigger` moved instance variable `source_info`, `sink_info` and `custom_context_tag` under property `properties` whose type is `FileTriggerProperties`
  - Model `PeriodicTimerEventTrigger` moved instance variable `source_info`, `sink_info` and `custom_context_tag` under property `properties` whose type is `PeriodicTimerProperties`
  - Model `UploadCertificateRequest` moved instance variable `authentication_type` and `certificate` under property `properties` whose type is `RawCertificateData`
  - Method `DevicesOperations.list_by_resource_group` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `DevicesOperations.list_by_subscription` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Deleted or renamed method `DevicesOperations.begin_create_or_update`
  - Method `UsersOperations.list_by_data_box_edge_device` renamed its parameter `expand` to `filter`

### Other Changes

  - Deleted model `AddonList`/`AlertList`/`BandwidthSchedulesList`/`ContainerList`/`DataBoxEdgeDeviceList`/`DataBoxEdgeSkuList`/`MonitoringMetricConfigurationList`/`NodeList`/`OperationsList`/`OrderList`/`RoleList`/`ShareList`/`SkuInformationList`/`StorageAccountCredentialList`/`StorageAccountList`/`TriggerList`/`UserList` which actually were not used by SDK users
  - Deleted model `DataBoxEdgeMoveRequest`/`ResourceTypeSku`/`SkuInformation` which actually were not used by SDK users

## 3.0.0b1 (2025-08-06)

### Breaking Changes

- This package now only targets the latest Api-Version available on Azure and removes APIs of other Api-Version. After this change, the package can have much smaller size. If your application requires a specific and non-latest Api-Version, it's recommended to pin this package to the previous released version; If your application always only use latest Api-Version, please ignore this change.

## 2.0.0 (2025-02-19)

### Features Added

  - Model DataBoxEdgeSku has a new parameter capabilities
  
### Breaking Changes
  - Removed subfolders of some unused Api-Versions for smaller package size. If your application requires a specific and non-latest Api-Version, it's recommended to pin this package to the previous released version; If your application always only use latest Api-Version, please ignore this change.
  
## 2.0.0b1 (2023-02-13)

### Features Added

  - Added operation DevicesOperations.create_or_update
  - Added operation group DeviceCapacityCheckOperations
  - Added operation group DeviceCapacityInfoOperations
  - Added operation group DiagnosticSettingsOperations
  - Added operation group SupportPackagesOperations
  - Model DataBoxEdgeDevice has a new parameter data_residency
  - Model DataBoxEdgeDevice has a new parameter system_data_properties_system_data
  - Model DataBoxEdgeDeviceExtendedInfo has a new parameter cloud_witness_container_name
  - Model DataBoxEdgeDeviceExtendedInfo has a new parameter cloud_witness_storage_account_name
  - Model DataBoxEdgeDeviceExtendedInfo has a new parameter cloud_witness_storage_endpoint
  - Model DataBoxEdgeDeviceExtendedInfo has a new parameter cluster_witness_type
  - Model DataBoxEdgeDeviceExtendedInfo has a new parameter file_share_witness_location
  - Model DataBoxEdgeDeviceExtendedInfo has a new parameter file_share_witness_username
  - Model DataBoxEdgeDeviceExtendedInfo has a new parameter system_data
  - Model DataBoxEdgeSku has a new parameter capabilities
  - Model Order has a new parameter kind
  - Model Order has a new parameter order_id
  - Model UpdateDetails has a new parameter friendly_version_number
  - Model UpdateDetails has a new parameter installation_impact
  - Model UpdateSummary has a new parameter last_successful_install_job_date_time
  - Model UpdateSummary has a new parameter last_successful_scan_job_time
  - Operation UsersOperations.list_by_data_box_edge_device has a new optional parameter filter

### Breaking Changes

  - Operation UsersOperations.list_by_data_box_edge_device no longer has parameter expand
  - Parameter user_type of model User is now required
  - Removed operation DevicesOperations.begin_create_or_update

## 1.0.0 (2021-04-22)

**Features**

  - Model Share has a new parameter system_data
  - Model NodeList has a new parameter next_link
  - Model Operation has a new parameter is_data_action
  - Model IoTRole has a new parameter system_data
  - Model IoTRole has a new parameter compute_resource
  - Model Order has a new parameter shipment_type
  - Model Order has a new parameter system_data
  - Model Role has a new parameter system_data
  - Model DataBoxEdgeDevice has a new parameter kind
  - Model DataBoxEdgeDevice has a new parameter edge_profile
  - Model DataBoxEdgeDevice has a new parameter identity
  - Model DataBoxEdgeDevice has a new parameter resource_move_details
  - Model DataBoxEdgeDevice has a new parameter system_data
  - Model StorageAccountCredential has a new parameter system_data
  - Model UpdateSummary has a new parameter last_download_job_status
  - Model UpdateSummary has a new parameter last_completed_install_job_id
  - Model UpdateSummary has a new parameter total_time_in_minutes
  - Model UpdateSummary has a new parameter last_completed_download_job_id
  - Model UpdateSummary has a new parameter last_install_job_status
  - Model UpdateSummary has a new parameter updates
  - Model UpdateSummary has a new parameter system_data
  - Model DataBoxEdgeDeviceExtendedInfo has a new parameter channel_integrity_key_name
  - Model DataBoxEdgeDeviceExtendedInfo has a new parameter channel_integrity_key_version
  - Model DataBoxEdgeDeviceExtendedInfo has a new parameter key_vault_sync_status
  - Model DataBoxEdgeDeviceExtendedInfo has a new parameter client_secret_store_id
  - Model DataBoxEdgeDeviceExtendedInfo has a new parameter device_secrets
  - Model DataBoxEdgeDeviceExtendedInfo has a new parameter client_secret_store_url
  - Model FileEventTrigger has a new parameter system_data
  - Model DataBoxEdgeSku has a new parameter shipment_types
  - Model Alert has a new parameter system_data
  - Model Container has a new parameter system_data
  - Model User has a new parameter system_data
  - Model Trigger has a new parameter system_data
  - Model NetworkSettings has a new parameter system_data
  - Model PeriodicTimerEventTrigger has a new parameter system_data
  - Model BandwidthSchedule has a new parameter system_data
  - Model OrderStatus has a new parameter tracking_information
  - Model StorageAccount has a new parameter system_data
  - Model DataBoxEdgeDevicePatch has a new parameter identity
  - Model DataBoxEdgeDevicePatch has a new parameter edge_profile
  - Added operation DevicesOperations.generate_certificate
  - Added operation DevicesOperations.update_extended_information
  - Added operation OrdersOperations.list_dc_access_code
  - Added operation group AddonsOperations
  - Added operation group MonitoringConfigOperations

**Breaking changes**

  - Operation UsersOperations.list_by_data_box_edge_device has a new signature
  - Parameter data_policy of model StorageAccount is now required
  - Model SkuInformation no longer has parameter resource_type
  - Model SkuInformation no longer has parameter capabilities
  - Model SkuInformation no longer has parameter size
  - Model DataBoxEdgeSku no longer has parameter restrictions
  - Model ResourceTypeSku has a new signature

## 1.0.0b1 (2020-12-08)

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

## 0.2.0 (2020-11-02)

**Features**

  - Model IoTRole has a new parameter host_platform_type
  - Model IoTRole has a new parameter io_tedge_agent_info
  - Model Job has a new parameter refreshed_entity_id
  - Model MountPointMap has a new parameter mount_type
  - Model OrderStatus has a new parameter additional_order_details
  - Added operation group ContainersOperations

## 0.1.0 (2020-01-08)

  - Initial Release
