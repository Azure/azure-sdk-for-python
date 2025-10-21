# Release History

## 3.0.0 (2025-10-21)

### Features Added

  - Model `DataBoxEdgeDeviceExtendedInfo` added property `system_data`
  - Model `DataBoxEdgeDevicePatch` added property `properties`
  - Model `EdgeProfileSubscription` added property `properties`
  - Model `FileEventTrigger` added property `properties`
  - Model `Job` added property `system_data`
  - Model `LoadBalancerConfig` added property `ip_range`
  - Model `Order` added property `kind`
  - Model `PeriodicTimerEventTrigger` added property `properties`
  - Enum `SkuName` added member `EDGE_MR_TCP`
  - Enum `SkuName` added member `EP2_128_GPU1_MX1_W`
  - Enum `SkuName` added member `EP2_256_2T4_W`
  - Enum `SkuName` added member `EP2_256_GPU2_MX1`
  - Enum `SkuName` added member `EP2_64_1VPU_W`
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
  - Added model `DCAccessCodeProperties`
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
  - Added model `MetricDimension_V1`
  - Added model `MetricSpecification_V1`
  - Added model `NumaNodeData`
  - Added model `PeriodicTimerProperties`
  - Added enum `ProactiveDiagnosticsConsent`
  - Added model `ProactiveLogCollectionSettingsProperties`
  - Added model `ProxyResource`
  - Added model `RawCertificateData`
  - Added enum `RemoteApplicationType`
  - Added model `RemoteSupportSettings`
  - Added model `Resource`
  - Added model `SubscriptionProperties`
  - Added model `SupportPackageRequestProperties`
  - Added model `TrackedResource`
  - Added model `TriggerSupportPackageRequest`
  - Added model `VmMemory`
  - Added model `VmPlacementRequestResult`
  - Model `DevicesOperations` added method `create_or_update`
  - Model `UsersOperations` added parameter `filter` in method `list_by_data_box_edge_device`
  - Added model `DeviceCapacityCheckOperations`
  - Added model `DeviceCapacityInfoOperations`
  - Added model `DiagnosticSettingsOperations`
  - Added model `SupportPackagesOperations`

### Breaking Changes

  - Deleted or renamed client `DataBoxEdgeManagementClient`
  - Model `DCAccessCode` deleted or renamed its instance variable `auth_code`
  - Model `DataBoxEdgeDevicePatch` deleted or renamed its instance variable `edge_profile`
  - Model `EdgeProfileSubscription` deleted or renamed its instance variable `tenant_id`
  - Model `EdgeProfileSubscription` deleted or renamed its instance variable `location_placement_id`
  - Model `EdgeProfileSubscription` deleted or renamed its instance variable `quota_id`
  - Model `EdgeProfileSubscription` deleted or renamed its instance variable `serialized_details`
  - Model `EdgeProfileSubscription` deleted or renamed its instance variable `registered_features`
  - Model `FileEventTrigger` deleted or renamed its instance variable `source_info`
  - Model `FileEventTrigger` deleted or renamed its instance variable `sink_info`
  - Model `FileEventTrigger` deleted or renamed its instance variable `custom_context_tag`
  - Model `PeriodicTimerEventTrigger` deleted or renamed its instance variable `source_info`
  - Model `PeriodicTimerEventTrigger` deleted or renamed its instance variable `sink_info`
  - Model `PeriodicTimerEventTrigger` deleted or renamed its instance variable `custom_context_tag`
  - Deleted or renamed enum value `SkuName.EP2_256_2_T4_W`
  - Deleted or renamed enum value `SkuName.EP2_64_1_VPU_W`
  - Deleted or renamed enum value `TimeGrain.PT12_H`
  - Deleted or renamed enum value `TimeGrain.PT15_M`
  - Deleted or renamed enum value `TimeGrain.PT1_D`
  - Deleted or renamed enum value `TimeGrain.PT1_H`
  - Deleted or renamed enum value `TimeGrain.PT1_M`
  - Deleted or renamed enum value `TimeGrain.PT30_M`
  - Deleted or renamed enum value `TimeGrain.PT5_M`
  - Deleted or renamed enum value `TimeGrain.PT6_H`
  - Model `UploadCertificateRequest` deleted or renamed its instance variable `authentication_type`
  - Model `UploadCertificateRequest` deleted or renamed its instance variable `certificate`
  - Deleted or renamed model `AddonList`
  - Deleted or renamed model `AlertList`
  - Deleted or renamed model `BandwidthSchedulesList`
  - Deleted or renamed model `ContainerList`
  - Deleted or renamed model `DataBoxEdgeDeviceList`
  - Deleted or renamed model `DataBoxEdgeMoveRequest`
  - Deleted or renamed model `DataBoxEdgeSkuList`
  - Deleted or renamed model `MetricDimensionV1`
  - Deleted or renamed model `MetricSpecificationV1`
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
  - Method `UsersOperations.begin_delete` re-ordered its parameters from `['self', 'device_name', 'name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'name', 'kwargs']`
  - Method `UsersOperations.list_by_data_box_edge_device` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'expand', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'filter', 'kwargs']`
  - Method `UsersOperations.get` re-ordered its parameters from `['self', 'device_name', 'name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'name', 'kwargs']`
  - Method `UsersOperations.begin_create_or_update` re-ordered its parameters from `['self', 'device_name', 'name', 'resource_group_name', 'user', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'name', 'user', 'kwargs']`
  - Method `StorageAccountsOperations.begin_delete` re-ordered its parameters from `['self', 'device_name', 'storage_account_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'storage_account_name', 'kwargs']`
  - Method `StorageAccountsOperations.list_by_data_box_edge_device` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'kwargs']`
  - Method `StorageAccountsOperations.get` re-ordered its parameters from `['self', 'device_name', 'storage_account_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'storage_account_name', 'kwargs']`
  - Method `StorageAccountsOperations.begin_create_or_update` re-ordered its parameters from `['self', 'device_name', 'storage_account_name', 'resource_group_name', 'storage_account', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'storage_account_name', 'storage_account', 'kwargs']`
  - Method `MonitoringConfigOperations.begin_delete` re-ordered its parameters from `['self', 'device_name', 'role_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'role_name', 'kwargs']`
  - Method `MonitoringConfigOperations.list` re-ordered its parameters from `['self', 'device_name', 'role_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'role_name', 'kwargs']`
  - Method `MonitoringConfigOperations.get` re-ordered its parameters from `['self', 'device_name', 'role_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'role_name', 'kwargs']`
  - Method `MonitoringConfigOperations.begin_create_or_update` re-ordered its parameters from `['self', 'device_name', 'role_name', 'resource_group_name', 'monitoring_metric_configuration', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'role_name', 'monitoring_metric_configuration', 'kwargs']`
  - Method `OperationsStatusOperations.get` re-ordered its parameters from `['self', 'device_name', 'name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'name', 'kwargs']`
  - Method `JobsOperations.get` re-ordered its parameters from `['self', 'device_name', 'name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'name', 'kwargs']`
  - Method `RolesOperations.begin_delete` re-ordered its parameters from `['self', 'device_name', 'name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'name', 'kwargs']`
  - Method `RolesOperations.list_by_data_box_edge_device` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'kwargs']`
  - Method `RolesOperations.get` re-ordered its parameters from `['self', 'device_name', 'name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'name', 'kwargs']`
  - Method `RolesOperations.begin_create_or_update` re-ordered its parameters from `['self', 'device_name', 'name', 'resource_group_name', 'role', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'name', 'role', 'kwargs']`
  - Method `SharesOperations.begin_delete` re-ordered its parameters from `['self', 'device_name', 'name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'name', 'kwargs']`
  - Method `SharesOperations.begin_refresh` re-ordered its parameters from `['self', 'device_name', 'name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'name', 'kwargs']`
  - Method `SharesOperations.list_by_data_box_edge_device` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'kwargs']`
  - Method `SharesOperations.get` re-ordered its parameters from `['self', 'device_name', 'name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'name', 'kwargs']`
  - Method `SharesOperations.begin_create_or_update` re-ordered its parameters from `['self', 'device_name', 'name', 'resource_group_name', 'share', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'name', 'share', 'kwargs']`
  - Method `ContainersOperations.begin_delete` re-ordered its parameters from `['self', 'device_name', 'storage_account_name', 'container_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'storage_account_name', 'container_name', 'kwargs']`
  - Method `ContainersOperations.begin_refresh` re-ordered its parameters from `['self', 'device_name', 'storage_account_name', 'container_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'storage_account_name', 'container_name', 'kwargs']`
  - Method `ContainersOperations.get` re-ordered its parameters from `['self', 'device_name', 'storage_account_name', 'container_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'storage_account_name', 'container_name', 'kwargs']`
  - Method `ContainersOperations.begin_create_or_update` re-ordered its parameters from `['self', 'device_name', 'storage_account_name', 'container_name', 'resource_group_name', 'container', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'storage_account_name', 'container_name', 'container', 'kwargs']`
  - Method `ContainersOperations.list_by_storage_account` re-ordered its parameters from `['self', 'device_name', 'storage_account_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'storage_account_name', 'kwargs']`
  - Method `OrdersOperations.begin_delete` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'kwargs']`
  - Method `OrdersOperations.list_dc_access_code` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'kwargs']`
  - Method `OrdersOperations.list_by_data_box_edge_device` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'kwargs']`
  - Method `OrdersOperations.get` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'kwargs']`
  - Method `OrdersOperations.begin_create_or_update` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'order', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'order', 'kwargs']`
  - Method `TriggersOperations.begin_delete` re-ordered its parameters from `['self', 'device_name', 'name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'name', 'kwargs']`
  - Method `TriggersOperations.list_by_data_box_edge_device` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'filter', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'filter', 'kwargs']`
  - Method `TriggersOperations.get` re-ordered its parameters from `['self', 'device_name', 'name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'name', 'kwargs']`
  - Method `TriggersOperations.begin_create_or_update` re-ordered its parameters from `['self', 'device_name', 'name', 'resource_group_name', 'trigger', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'name', 'trigger', 'kwargs']`
  - Method `AddonsOperations.begin_delete` re-ordered its parameters from `['self', 'device_name', 'role_name', 'addon_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'role_name', 'addon_name', 'kwargs']`
  - Method `AddonsOperations.list_by_role` re-ordered its parameters from `['self', 'device_name', 'role_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'role_name', 'kwargs']`
  - Method `AddonsOperations.get` re-ordered its parameters from `['self', 'device_name', 'role_name', 'addon_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'role_name', 'addon_name', 'kwargs']`
  - Method `AddonsOperations.begin_create_or_update` re-ordered its parameters from `['self', 'device_name', 'role_name', 'addon_name', 'resource_group_name', 'addon', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'role_name', 'addon_name', 'addon', 'kwargs']`
  - Method `AlertsOperations.list_by_data_box_edge_device` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'kwargs']`
  - Method `AlertsOperations.get` re-ordered its parameters from `['self', 'device_name', 'name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'name', 'kwargs']`
  - Method `DevicesOperations.begin_delete` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'kwargs']`
  - Method `DevicesOperations.begin_create_or_update_security_settings` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'security_settings', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'security_settings', 'kwargs']`
  - Method `DevicesOperations.upload_certificate` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'parameters', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'parameters', 'kwargs']`
  - Method `DevicesOperations.begin_install_updates` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'kwargs']`
  - Method `DevicesOperations.get_network_settings` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'kwargs']`
  - Method `DevicesOperations.generate_certificate` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'kwargs']`
  - Method `DevicesOperations.begin_scan_for_updates` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'kwargs']`
  - Method `DevicesOperations.get` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'kwargs']`
  - Method `DevicesOperations.get_extended_information` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'kwargs']`
  - Method `DevicesOperations.update` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'parameters', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'parameters', 'kwargs']`
  - Method `DevicesOperations.get_update_summary` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'kwargs']`
  - Method `DevicesOperations.update_extended_information` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'parameters', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'parameters', 'kwargs']`
  - Method `DevicesOperations.begin_download_updates` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'kwargs']`
  - Method `BandwidthSchedulesOperations.begin_delete` re-ordered its parameters from `['self', 'device_name', 'name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'name', 'kwargs']`
  - Method `BandwidthSchedulesOperations.list_by_data_box_edge_device` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'kwargs']`
  - Method `BandwidthSchedulesOperations.get` re-ordered its parameters from `['self', 'device_name', 'name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'name', 'kwargs']`
  - Method `BandwidthSchedulesOperations.begin_create_or_update` re-ordered its parameters from `['self', 'device_name', 'name', 'resource_group_name', 'parameters', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'name', 'parameters', 'kwargs']`
  - Method `StorageAccountCredentialsOperations.begin_delete` re-ordered its parameters from `['self', 'device_name', 'name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'name', 'kwargs']`
  - Method `StorageAccountCredentialsOperations.list_by_data_box_edge_device` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'kwargs']`
  - Method `StorageAccountCredentialsOperations.get` re-ordered its parameters from `['self', 'device_name', 'name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'name', 'kwargs']`
  - Method `StorageAccountCredentialsOperations.begin_create_or_update` re-ordered its parameters from `['self', 'device_name', 'name', 'resource_group_name', 'storage_account_credential', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'name', 'storage_account_credential', 'kwargs']`
  - Method `NodesOperations.list_by_data_box_edge_device` re-ordered its parameters from `['self', 'device_name', 'resource_group_name', 'kwargs']` to `['self', 'resource_group_name', 'device_name', 'kwargs']`

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
