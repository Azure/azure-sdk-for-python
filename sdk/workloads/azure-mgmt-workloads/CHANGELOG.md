# Release History

## 1.0.0 (2023-04-19)

### Breaking Changes

  - Client name is changed from `WorkloadsClient` to `WorkloadsMgmtClient`
  - Model ImageReference no longer has parameter exact_version
  - Model ImageReference no longer has parameter shared_gallery_image_id

## 1.0.0b3 (2023-02-15)

### Features Added

  - Added operation SAPApplicationServerInstancesOperations.begin_start_instance
  - Added operation SAPApplicationServerInstancesOperations.begin_stop_instance
  - Added operation SAPCentralInstancesOperations.begin_start_instance
  - Added operation SAPCentralInstancesOperations.begin_stop_instance
  - Added operation SAPDatabaseInstancesOperations.begin_start_instance
  - Added operation SAPDatabaseInstancesOperations.begin_stop_instance
  - Added operation group SapLandscapeMonitorOperations
  - Model CentralServerVmDetails has a new parameter storage_details
  - Model DatabaseConfiguration has a new parameter disk_configuration
  - Model DatabaseVmDetails has a new parameter storage_details
  - Model DiscoveryConfiguration has a new parameter managed_rg_storage_account_name
  - Model HanaDbProviderInstanceProperties has a new parameter sap_sid
  - Model PrometheusOSProviderInstanceProperties has a new parameter sap_sid
  - Model SAPApplicationServerInstance has a new parameter load_balancer_details
  - Model SAPApplicationServerInstance has a new parameter vm_details
  - Model SAPCentralServerInstance has a new parameter load_balancer_details
  - Model SAPDatabaseInstance has a new parameter load_balancer_details
  - Model SAPDiskConfiguration has a new parameter recommended_configuration
  - Model SAPDiskConfiguration has a new parameter supported_configurations
  - Model SAPDiskConfigurationsResult has a new parameter volume_configurations
  - Model SingleServerConfiguration has a new parameter custom_resource_names
  - Model SingleServerConfiguration has a new parameter db_disk_configuration
  - Model StopRequest has a new parameter soft_stop_timeout_seconds
  - Model ThreeTierConfiguration has a new parameter custom_resource_names
  - Model ThreeTierConfiguration has a new parameter storage_configuration

### Breaking Changes

  - Model HanaDbProviderInstanceProperties no longer has parameter db_ssl_certificate_uri
  - Model SAPApplicationServerInstance no longer has parameter virtual_machine_id
  - Model SAPDiskConfiguration no longer has parameter disk_count
  - Model SAPDiskConfiguration no longer has parameter disk_iops_read_write
  - Model SAPDiskConfiguration no longer has parameter disk_m_bps_read_write
  - Model SAPDiskConfiguration no longer has parameter disk_size_gb
  - Model SAPDiskConfiguration no longer has parameter disk_storage_type
  - Model SAPDiskConfiguration no longer has parameter disk_type
  - Model SAPDiskConfiguration no longer has parameter volume
  - Model SAPDiskConfigurationsResult no longer has parameter disk_configurations
  - Model SapNetWeaverProviderInstanceProperties no longer has parameter sap_ssl_certificate_uri
  - Model StopRequest no longer has parameter hard_stop
  - Removed operation group PhpWorkloadsOperations
  - Removed operation group SkusOperations
  - Removed operation group WordpressInstancesOperations

## 1.0.0b2 (2022-11-30)

### Features Added

  - Model DB2ProviderInstanceProperties has a new parameter ssl_certificate_uri
  - Model DB2ProviderInstanceProperties has a new parameter ssl_preference
  - Model HanaDbProviderInstanceProperties has a new parameter ssl_certificate_uri
  - Model HanaDbProviderInstanceProperties has a new parameter ssl_preference
  - Model Monitor has a new parameter storage_account_arm_id
  - Model Monitor has a new parameter zone_redundancy_preference
  - Model MsSqlServerProviderInstanceProperties has a new parameter ssl_certificate_uri
  - Model MsSqlServerProviderInstanceProperties has a new parameter ssl_preference
  - Model PrometheusHaClusterProviderInstanceProperties has a new parameter ssl_certificate_uri
  - Model PrometheusHaClusterProviderInstanceProperties has a new parameter ssl_preference
  - Model PrometheusOSProviderInstanceProperties has a new parameter ssl_certificate_uri
  - Model PrometheusOSProviderInstanceProperties has a new parameter ssl_preference
  - Model SapNetWeaverProviderInstanceProperties has a new parameter ssl_certificate_uri
  - Model SapNetWeaverProviderInstanceProperties has a new parameter ssl_preference

## 1.0.0b1 (2022-06-30)

* Initial Release
