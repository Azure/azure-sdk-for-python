# Release History

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
