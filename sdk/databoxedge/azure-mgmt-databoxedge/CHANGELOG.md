# Release History

## 3.0.0 (2026-07-13)

### Features Added

  - Client `DataBoxEdgeManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `DataBoxEdgeManagementClient` added method `send_request`
  - Client `DataBoxEdgeManagementClient` added operation group `device_capacity_check`
  - Client `DataBoxEdgeManagementClient` added operation group `device_capacity_info`
  - Client `DataBoxEdgeManagementClient` added operation group `diagnostic_settings`
  - Client `DataBoxEdgeManagementClient` added operation group `support_packages`
  - Model `Alert` added property `properties`
  - Model `ArcAddon` added property `properties`
  - Model `BandwidthSchedule` added property `properties`
  - Model `CloudEdgeManagementRole` added property `properties`
  - Model `Container` added property `properties`
  - Model `DataBoxEdgeDevice` added property `properties`
  - Model `DataBoxEdgeDeviceExtendedInfo` added property `properties`
  - Model `DataBoxEdgeDeviceExtendedInfo` added property `system_data`
  - Model `DataBoxEdgeDevicePatch` added property `properties`
  - Model `EdgeProfileSubscription` added property `properties`
  - Model `FileEventTrigger` added property `properties`
  - Model `IoTAddon` added property `properties`
  - Model `IoTRole` added property `properties`
  - Model `Job` added property `properties`
  - Model `Job` added property `system_data`
  - Model `KubernetesRole` added property `properties`
  - Model `LoadBalancerConfig` added property `ip_range`
  - Model `MECRole` added property `properties`
  - Model `MonitoringMetricConfiguration` added property `properties`
  - Model `NetworkSettings` added property `properties`
  - Model `Node` added property `properties`
  - Model `Operation` added property `properties`
  - Model `Order` added property `kind`
  - Model `Order` added property `properties`
  - Model `PeriodicTimerEventTrigger` added property `properties`
  - Model `SecuritySettings` added property `properties`
  - Model `Share` added property `properties`
  - Enum `SkuName` added member `EDGE_MR_TCP`
  - Enum `SkuName` added member `EP2_128_GPU1_MX1_W`
  - Enum `SkuName` added member `EP2_256_GPU2_MX1`
  - Enum `SkuName` added member `EP2_64_MX1_W`
  - Model `StorageAccount` added property `properties`
  - Model `StorageAccountCredential` added property `properties`
  - Model `UpdateDetails` added property `friendly_version_number`
  - Model `UpdateDetails` added property `installation_impact`
  - Model `UpdateSummary` added property `properties`
  - Model `User` added property `properties`
  - Added enum `AccessLevel`
  - Added model `AlertProperties`
  - Added model `ArcAddonProperties`
  - Added model `BandwidthScheduleProperties`
  - Added model `CloudEdgeManagementRoleProperties`
  - Added model `CloudError`
  - Added model `ClusterCapacityViewData`
  - Added model `ClusterGpuCapacity`
  - Added model `ClusterMemoryCapacity`
  - Added model `ClusterStorageViewData`
  - Added enum `ClusterWitnessType`
  - Added model `ContainerProperties`
  - Added model `DCAccessCodeProperties`
  - Added model `DataBoxEdgeDeviceExtendedInfoProperties`
  - Added model `DataBoxEdgeDeviceProperties`
  - Added model `DataBoxEdgeDevicePropertiesPatch`
  - Added model `DataResidency`
  - Added enum `DataResidencyType`
  - Added model `DeviceCapacityInfo`
  - Added model `DeviceCapacityInfoProperties`
  - Added model `DeviceCapacityRequestInfo`
  - Added model `DeviceCapacityRequestInfoProperties`
  - Added model `DiagnosticProactiveLogCollectionSettings`
  - Added model `DiagnosticRemoteSupportSettings`
  - Added model `DiagnosticRemoteSupportSettingsProperties`
  - Added model `FileTriggerProperties`
  - Added model `HostCapacity`
  - Added enum `InstallationImpact`
  - Added model `IoTAddonProperties`
  - Added model `IoTRoleProperties`
  - Added model `JobProperties`
  - Added model `KubernetesRoleProperties`
  - Added model `MECRoleProperties`
  - Added model `MonitoringMetricConfigurationProperties`
  - Added model `NetworkSettingsProperties`
  - Added model `NodeProperties`
  - Added model `NumaNodeData`
  - Added model `OperationProperties`
  - Added model `OrderProperties`
  - Added model `PeriodicTimerProperties`
  - Added enum `ProactiveDiagnosticsConsent`
  - Added model `ProactiveLogCollectionSettingsProperties`
  - Added model `ProxyResource`
  - Added model `RawCertificateData`
  - Added enum `RemoteApplicationType`
  - Added model `RemoteSupportSettings`
  - Added model `Resource`
  - Added model `SecuritySettingsProperties`
  - Added model `ShareProperties`
  - Added model `StorageAccountCredentialProperties`
  - Added model `StorageAccountProperties`
  - Added model `SubscriptionProperties`
  - Added model `SupportPackageRequestProperties`
  - Added model `TrackedResource`
  - Added model `TriggerSupportPackageRequest`
  - Added model `UpdateSummaryProperties`
  - Added model `UserProperties`
  - Added model `VmMemory`
  - Added model `VmPlacementRequestResult`
  - Model `DevicesOperations` added method `create_or_update`
  - Model `UsersOperations` added parameter `filter` in method `list_by_data_box_edge_device`
  - Added model `DeviceCapacityCheckOperations`
  - Added model `DeviceCapacityInfoOperations`
  - Added model `DiagnosticSettingsOperations`
  - Added model `SupportPackagesOperations`

### Breaking Changes

  - Model `Alert` deleted or renamed its instance variable `alert_type`
  - Model `Alert` deleted or renamed its instance variable `appeared_at_date_time`
  - Model `Alert` deleted or renamed its instance variable `detailed_information`
  - Model `Alert` deleted or renamed its instance variable `error_details`
  - Model `Alert` deleted or renamed its instance variable `recommendation`
  - Model `Alert` deleted or renamed its instance variable `severity`
  - Model `Alert` deleted or renamed its instance variable `title`
  - Model `ArcAddon` deleted or renamed its instance variable `host_platform`
  - Model `ArcAddon` deleted or renamed its instance variable `host_platform_type`
  - Model `ArcAddon` deleted or renamed its instance variable `provisioning_state`
  - Model `ArcAddon` deleted or renamed its instance variable `resource_group_name`
  - Model `ArcAddon` deleted or renamed its instance variable `resource_location`
  - Model `ArcAddon` deleted or renamed its instance variable `resource_name`
  - Model `ArcAddon` deleted or renamed its instance variable `subscription_id`
  - Model `ArcAddon` deleted or renamed its instance variable `version`
  - Model `BandwidthSchedule` deleted or renamed its instance variable `days`
  - Model `BandwidthSchedule` deleted or renamed its instance variable `rate_in_mbps`
  - Model `BandwidthSchedule` deleted or renamed its instance variable `start`
  - Model `BandwidthSchedule` deleted or renamed its instance variable `stop`
  - Model `CloudEdgeManagementRole` deleted or renamed its instance variable `edge_profile`
  - Model `CloudEdgeManagementRole` deleted or renamed its instance variable `local_management_status`
  - Model `CloudEdgeManagementRole` deleted or renamed its instance variable `role_status`
  - Model `Container` deleted or renamed its instance variable `container_status`
  - Model `Container` deleted or renamed its instance variable `created_date_time`
  - Model `Container` deleted or renamed its instance variable `data_format`
  - Model `Container` deleted or renamed its instance variable `refresh_details`
  - Model `DCAccessCode` deleted or renamed its instance variable `auth_code`
  - Model `DataBoxEdgeDevice` deleted or renamed its instance variable `configured_role_types`
  - Model `DataBoxEdgeDevice` deleted or renamed its instance variable `culture`
  - Model `DataBoxEdgeDevice` deleted or renamed its instance variable `data_box_edge_device_status`
  - Model `DataBoxEdgeDevice` deleted or renamed its instance variable `description`
  - Model `DataBoxEdgeDevice` deleted or renamed its instance variable `device_hcs_version`
  - Model `DataBoxEdgeDevice` deleted or renamed its instance variable `device_local_capacity`
  - Model `DataBoxEdgeDevice` deleted or renamed its instance variable `device_model`
  - Model `DataBoxEdgeDevice` deleted or renamed its instance variable `device_software_version`
  - Model `DataBoxEdgeDevice` deleted or renamed its instance variable `device_type`
  - Model `DataBoxEdgeDevice` deleted or renamed its instance variable `edge_profile`
  - Model `DataBoxEdgeDevice` deleted or renamed its instance variable `friendly_name`
  - Model `DataBoxEdgeDevice` deleted or renamed its instance variable `model_description`
  - Model `DataBoxEdgeDevice` deleted or renamed its instance variable `node_count`
  - Model `DataBoxEdgeDevice` deleted or renamed its instance variable `resource_move_details`
  - Model `DataBoxEdgeDevice` deleted or renamed its instance variable `serial_number`
  - Model `DataBoxEdgeDevice` deleted or renamed its instance variable `time_zone`
  - Model `DataBoxEdgeDeviceExtendedInfo` deleted or renamed its instance variable `channel_integrity_key_name`
  - Model `DataBoxEdgeDeviceExtendedInfo` deleted or renamed its instance variable `channel_integrity_key_version`
  - Model `DataBoxEdgeDeviceExtendedInfo` deleted or renamed its instance variable `client_secret_store_id`
  - Model `DataBoxEdgeDeviceExtendedInfo` deleted or renamed its instance variable `client_secret_store_url`
  - Model `DataBoxEdgeDeviceExtendedInfo` deleted or renamed its instance variable `device_secrets`
  - Model `DataBoxEdgeDeviceExtendedInfo` deleted or renamed its instance variable `encryption_key`
  - Model `DataBoxEdgeDeviceExtendedInfo` deleted or renamed its instance variable `encryption_key_thumbprint`
  - Model `DataBoxEdgeDeviceExtendedInfo` deleted or renamed its instance variable `key_vault_sync_status`
  - Model `DataBoxEdgeDeviceExtendedInfo` deleted or renamed its instance variable `resource_key`
  - Model `DataBoxEdgeDevicePatch` deleted or renamed its instance variable `edge_profile`
  - Model `EdgeProfileSubscription` deleted or renamed its instance variable `location_placement_id`
  - Model `EdgeProfileSubscription` deleted or renamed its instance variable `quota_id`
  - Model `EdgeProfileSubscription` deleted or renamed its instance variable `registered_features`
  - Model `EdgeProfileSubscription` deleted or renamed its instance variable `serialized_details`
  - Model `EdgeProfileSubscription` deleted or renamed its instance variable `tenant_id`
  - Model `FileEventTrigger` deleted or renamed its instance variable `custom_context_tag`
  - Model `FileEventTrigger` deleted or renamed its instance variable `sink_info`
  - Model `FileEventTrigger` deleted or renamed its instance variable `source_info`
  - Model `IoTAddon` deleted or renamed its instance variable `host_platform`
  - Model `IoTAddon` deleted or renamed its instance variable `host_platform_type`
  - Model `IoTAddon` deleted or renamed its instance variable `io_t_device_details`
  - Model `IoTAddon` deleted or renamed its instance variable `io_t_edge_device_details`
  - Model `IoTAddon` deleted or renamed its instance variable `provisioning_state`
  - Model `IoTAddon` deleted or renamed its instance variable `version`
  - Model `IoTRole` deleted or renamed its instance variable `compute_resource`
  - Model `IoTRole` deleted or renamed its instance variable `host_platform`
  - Model `IoTRole` deleted or renamed its instance variable `host_platform_type`
  - Model `IoTRole` deleted or renamed its instance variable `io_t_device_details`
  - Model `IoTRole` deleted or renamed its instance variable `io_t_edge_agent_info`
  - Model `IoTRole` deleted or renamed its instance variable `io_t_edge_device_details`
  - Model `IoTRole` deleted or renamed its instance variable `role_status`
  - Model `IoTRole` deleted or renamed its instance variable `share_mappings`
  - Model `Job` deleted or renamed its instance variable `current_stage`
  - Model `Job` deleted or renamed its instance variable `download_progress`
  - Model `Job` deleted or renamed its instance variable `error_manifest_file`
  - Model `Job` deleted or renamed its instance variable `folder`
  - Model `Job` deleted or renamed its instance variable `install_progress`
  - Model `Job` deleted or renamed its instance variable `job_type`
  - Model `Job` deleted or renamed its instance variable `refreshed_entity_id`
  - Model `Job` deleted or renamed its instance variable `total_refresh_errors`
  - Model `KubernetesRole` deleted or renamed its instance variable `host_platform`
  - Model `KubernetesRole` deleted or renamed its instance variable `host_platform_type`
  - Model `KubernetesRole` deleted or renamed its instance variable `kubernetes_cluster_info`
  - Model `KubernetesRole` deleted or renamed its instance variable `kubernetes_role_resources`
  - Model `KubernetesRole` deleted or renamed its instance variable `provisioning_state`
  - Model `KubernetesRole` deleted or renamed its instance variable `role_status`
  - Model `MECRole` deleted or renamed its instance variable `connection_string`
  - Model `MECRole` deleted or renamed its instance variable `controller_endpoint`
  - Model `MECRole` deleted or renamed its instance variable `resource_unique_id`
  - Model `MECRole` deleted or renamed its instance variable `role_status`
  - Model `MonitoringMetricConfiguration` deleted or renamed its instance variable `metric_configurations`
  - Model `NetworkSettings` deleted or renamed its instance variable `network_adapters`
  - Model `Node` deleted or renamed its instance variable `node_chassis_serial_number`
  - Model `Node` deleted or renamed its instance variable `node_display_name`
  - Model `Node` deleted or renamed its instance variable `node_friendly_software_version`
  - Model `Node` deleted or renamed its instance variable `node_hcs_version`
  - Model `Node` deleted or renamed its instance variable `node_instance_id`
  - Model `Node` deleted or renamed its instance variable `node_serial_number`
  - Model `Node` deleted or renamed its instance variable `node_status`
  - Model `Operation` deleted or renamed its instance variable `service_specification`
  - Model `Order` deleted or renamed its instance variable `contact_information`
  - Model `Order` deleted or renamed its instance variable `current_status`
  - Model `Order` deleted or renamed its instance variable `delivery_tracking_info`
  - Model `Order` deleted or renamed its instance variable `order_history`
  - Model `Order` deleted or renamed its instance variable `return_tracking_info`
  - Model `Order` deleted or renamed its instance variable `serial_number`
  - Model `Order` deleted or renamed its instance variable `shipment_type`
  - Model `Order` deleted or renamed its instance variable `shipping_address`
  - Model `PeriodicTimerEventTrigger` deleted or renamed its instance variable `custom_context_tag`
  - Model `PeriodicTimerEventTrigger` deleted or renamed its instance variable `sink_info`
  - Model `PeriodicTimerEventTrigger` deleted or renamed its instance variable `source_info`
  - Model `SecuritySettings` deleted or renamed its instance variable `device_admin_password`
  - Model `Share` deleted or renamed its instance variable `access_protocol`
  - Model `Share` deleted or renamed its instance variable `azure_container_info`
  - Model `Share` deleted or renamed its instance variable `client_access_rights`
  - Model `Share` deleted or renamed its instance variable `data_policy`
  - Model `Share` deleted or renamed its instance variable `description`
  - Model `Share` deleted or renamed its instance variable `monitoring_status`
  - Model `Share` deleted or renamed its instance variable `refresh_details`
  - Model `Share` deleted or renamed its instance variable `share_mappings`
  - Model `Share` deleted or renamed its instance variable `share_status`
  - Model `Share` deleted or renamed its instance variable `user_access_rights`
  - Model `StorageAccount` deleted or renamed its instance variable `blob_endpoint`
  - Model `StorageAccount` deleted or renamed its instance variable `container_count`
  - Model `StorageAccount` deleted or renamed its instance variable `data_policy`
  - Model `StorageAccount` deleted or renamed its instance variable `description`
  - Model `StorageAccount` deleted or renamed its instance variable `storage_account_credential_id`
  - Model `StorageAccount` deleted or renamed its instance variable `storage_account_status`
  - Model `StorageAccountCredential` deleted or renamed its instance variable `account_key`
  - Model `StorageAccountCredential` deleted or renamed its instance variable `account_type`
  - Model `StorageAccountCredential` deleted or renamed its instance variable `alias`
  - Model `StorageAccountCredential` deleted or renamed its instance variable `blob_domain_name`
  - Model `StorageAccountCredential` deleted or renamed its instance variable `connection_string`
  - Model `StorageAccountCredential` deleted or renamed its instance variable `ssl_status`
  - Model `StorageAccountCredential` deleted or renamed its instance variable `storage_account_id`
  - Model `StorageAccountCredential` deleted or renamed its instance variable `user_name`
  - Model `UpdateSummary` deleted or renamed its instance variable `device_last_scanned_date_time`
  - Model `UpdateSummary` deleted or renamed its instance variable `device_version_number`
  - Model `UpdateSummary` deleted or renamed its instance variable `friendly_device_version_name`
  - Model `UpdateSummary` deleted or renamed its instance variable `in_progress_download_job_id`
  - Model `UpdateSummary` deleted or renamed its instance variable `in_progress_download_job_started_date_time`
  - Model `UpdateSummary` deleted or renamed its instance variable `in_progress_install_job_id`
  - Model `UpdateSummary` deleted or renamed its instance variable `in_progress_install_job_started_date_time`
  - Model `UpdateSummary` deleted or renamed its instance variable `last_completed_download_job_date_time`
  - Model `UpdateSummary` deleted or renamed its instance variable `last_completed_download_job_id`
  - Model `UpdateSummary` deleted or renamed its instance variable `last_completed_install_job_date_time`
  - Model `UpdateSummary` deleted or renamed its instance variable `last_completed_install_job_id`
  - Model `UpdateSummary` deleted or renamed its instance variable `last_completed_scan_job_date_time`
  - Model `UpdateSummary` deleted or renamed its instance variable `last_download_job_status`
  - Model `UpdateSummary` deleted or renamed its instance variable `last_install_job_status`
  - Model `UpdateSummary` deleted or renamed its instance variable `ongoing_update_operation`
  - Model `UpdateSummary` deleted or renamed its instance variable `reboot_behavior`
  - Model `UpdateSummary` deleted or renamed its instance variable `total_number_of_updates_available`
  - Model `UpdateSummary` deleted or renamed its instance variable `total_number_of_updates_pending_download`
  - Model `UpdateSummary` deleted or renamed its instance variable `total_number_of_updates_pending_install`
  - Model `UpdateSummary` deleted or renamed its instance variable `total_time_in_minutes`
  - Model `UpdateSummary` deleted or renamed its instance variable `total_update_size_in_bytes`
  - Model `UpdateSummary` deleted or renamed its instance variable `update_titles`
  - Model `UpdateSummary` deleted or renamed its instance variable `updates`
  - Model `UploadCertificateRequest` deleted or renamed its instance variable `authentication_type`
  - Model `UploadCertificateRequest` deleted or renamed its instance variable `certificate`
  - Model `User` deleted or renamed its instance variable `encrypted_password`
  - Model `User` deleted or renamed its instance variable `share_access_rights`
  - Model `User` deleted or renamed its instance variable `user_type`
  - Deleted or renamed model `AddonList`
  - Deleted or renamed model `AlertList`
  - Deleted or renamed model `BandwidthSchedulesList`
  - Deleted or renamed model `ContainerList`
  - Deleted or renamed model `DataBoxEdgeDeviceList`
  - Deleted or renamed model `DataBoxEdgeMoveRequest`
  - Deleted or renamed model `DataBoxEdgeSkuList`
  - Deleted or renamed model `MonitoringMetricConfigurationList`
  - Deleted or renamed model `NodeList`
  - Deleted or renamed model `OperationsList`
  - Deleted or renamed model `OrderList`
  - Deleted or renamed model `ResourceTypeSku`
  - Deleted or renamed model `RoleList`
  - Deleted or renamed model `ShareList`
  - Deleted or renamed model `SkuInformation`
  - Deleted or renamed model `SkuInformationList`
  - Deleted or renamed model `StorageAccountCredentialList`
  - Deleted or renamed model `StorageAccountList`
  - Deleted or renamed model `TriggerList`
  - Deleted or renamed model `UserList`
  - Method `DevicesOperations.list_by_resource_group` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `DevicesOperations.list_by_subscription` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Deleted or renamed method `DevicesOperations.begin_create_or_update`
  - Method `UsersOperations.list_by_data_box_edge_device` deleted or renamed its parameter `expand` of kind `positional_or_keyword`
  - Method `UsersOperations.list_by_data_box_edge_device` re-ordered its parameters from `['self', 'device_name', 'expand', 'resource_group_name', 'kwargs']` to `['self', 'device_name', 'filter', 'resource_group_name', 'kwargs']`

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
