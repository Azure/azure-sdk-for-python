# Release History

## 3.1.0 (2025-03-18)

### Features Added

  - Model `CreateOrderLimitForSubscriptionValidationRequest` added property `model`
  - Model `DataBoxScheduleAvailabilityRequest` added property `model`
  - Enum `DataCenterCode` added member `AMS25`
  - Enum `DataCenterCode` added member `BL24`
  - Enum `DataCenterCode` added member `CPQ21`
  - Enum `DataCenterCode` added member `DSM11`
  - Enum `DataCenterCode` added member `DXB23`
  - Enum `DataCenterCode` added member `IDC5`
  - Enum `DataCenterCode` added member `NTG20`
  - Enum `DataCenterCode` added member `OSA23`
  - Enum `DataCenterCode` added member `TYO23`
  - Model `DataTransferDetailsValidationRequest` added property `model`
  - Model `DatacenterAddressRequest` added property `model`
  - Model `DiskScheduleAvailabilityRequest` added property `model`
  - Model `HeavyScheduleAvailabilityRequest` added property `model`
  - Model `JobResource` added property `delayed_stage`
  - Model `JobResource` added property `all_devices_lost`
  - Model `JobStages` added property `delay_information`
  - Model `PreferencesValidationRequest` added property `model`
  - Model `RegionConfigurationRequest` added property `device_capability_request`
  - Model `RegionConfigurationResponse` added property `device_capability_response`
  - Model `ScheduleAvailabilityRequest` added property `model`
  - Model `Sku` added property `model`
  - Model `SkuAvailabilityValidationRequest` added property `model`
  - Model `SkuCapacity` added property `individual_sku_usable`
  - Model `TransportAvailabilityRequest` added property `model`
  - Model `ValidateAddress` added property `model`
  - Added enum `DelayNotificationStatus`
  - Added model `DeviceCapabilityDetails`
  - Added model `DeviceCapabilityRequest`
  - Added model `DeviceCapabilityResponse`
  - Added model `JobDelayDetails`
  - Added enum `ModelName`
  - Added enum `PortalDelayErrorCode`

## 3.0.0 (2024-10-30)

### Breaking Changes

  - This package now only targets the latest Api-Version available on Azure and removes APIs of other Api-Version. After this change, the package can have much smaller size. If your application requires a specific and non-latest Api-Version, it's recommended to pin this package to the previous released version; If your application always only use latest Api-Version, please ignore this change.

## 2.0.0 (2023-05-22)

### Features Added

  - Added operation JobsOperations.mark_devices_shipped
  - Added operation group DataBoxManagementClientOperationsMixin
  - Model CopyProgress has a new parameter actions
  - Model CopyProgress has a new parameter error
  - Model DataBoxDiskCopyProgress has a new parameter actions
  - Model DataBoxDiskCopyProgress has a new parameter error
  - Model DataBoxDiskJobDetails has a new parameter actions
  - Model DataBoxDiskJobDetails has a new parameter data_center_code
  - Model DataBoxDiskJobDetails has a new parameter datacenter_address
  - Model DataBoxDiskJobDetails has a new parameter device_erasure_details
  - Model DataBoxDiskJobDetails has a new parameter expected_data_size_in_tera_bytes
  - Model DataBoxDiskJobDetails has a new parameter granular_copy_log_details
  - Model DataBoxDiskJobDetails has a new parameter granular_copy_progress
  - Model DataBoxDiskJobDetails has a new parameter last_mitigation_action_on_job
  - Model DataBoxDiskJobDetails has a new parameter reverse_shipping_details
  - Model DataBoxHeavyJobDetails has a new parameter actions
  - Model DataBoxHeavyJobDetails has a new parameter data_center_code
  - Model DataBoxHeavyJobDetails has a new parameter datacenter_address
  - Model DataBoxHeavyJobDetails has a new parameter device_erasure_details
  - Model DataBoxHeavyJobDetails has a new parameter expected_data_size_in_tera_bytes
  - Model DataBoxHeavyJobDetails has a new parameter last_mitigation_action_on_job
  - Model DataBoxHeavyJobDetails has a new parameter reverse_shipping_details
  - Model DataBoxJobDetails has a new parameter actions
  - Model DataBoxJobDetails has a new parameter data_center_code
  - Model DataBoxJobDetails has a new parameter datacenter_address
  - Model DataBoxJobDetails has a new parameter device_erasure_details
  - Model DataBoxJobDetails has a new parameter expected_data_size_in_tera_bytes
  - Model DataBoxJobDetails has a new parameter last_mitigation_action_on_job
  - Model DataBoxJobDetails has a new parameter reverse_shipping_details
  - Model DataImportDetails has a new parameter log_collection_level
  - Model EncryptionPreferences has a new parameter hardware_encryption
  - Model JobDetails has a new parameter actions
  - Model JobDetails has a new parameter data_center_code
  - Model JobDetails has a new parameter datacenter_address
  - Model JobDetails has a new parameter device_erasure_details
  - Model JobDetails has a new parameter expected_data_size_in_tera_bytes
  - Model JobDetails has a new parameter last_mitigation_action_on_job
  - Model JobDetails has a new parameter reverse_shipping_details
  - Model JobResource has a new parameter reverse_shipping_details_update
  - Model JobResource has a new parameter reverse_transport_preference_update
  - Model JobResource has a new parameter system_data
  - Model Preferences has a new parameter reverse_transport_preferences
  - Model Preferences has a new parameter storage_account_access_tier_preferences
  - Model RegionConfigurationRequest has a new parameter datacenter_address_request
  - Model RegionConfigurationResponse has a new parameter datacenter_address_response
  - Model ShippingAddress has a new parameter skip_address_validation
  - Model ShippingAddress has a new parameter tax_identification_number
  - Model SkuInformation has a new parameter countries_within_commerce_boundary
  - Model TransportPreferences has a new parameter is_updated
  - Model UpdateJobDetails has a new parameter preferences
  - Model UpdateJobDetails has a new parameter return_to_customer_package_details
  - Model UpdateJobDetails has a new parameter reverse_shipping_details

### Breaking Changes

  - Model DataBoxDiskJobDetails no longer has parameter expected_data_size_in_terabytes
  - Model DataBoxHeavyJobDetails no longer has parameter expected_data_size_in_terabytes
  - Model DataBoxJobDetails no longer has parameter expected_data_size_in_terabytes
  - Model DiskScheduleAvailabilityRequest has a new required parameter expected_data_size_in_tera_bytes
  - Model DiskScheduleAvailabilityRequest no longer has parameter expected_data_size_in_terabytes
  - Model JobDetails no longer has parameter expected_data_size_in_terabytes

## 2.0.0b1 (2023-02-10)

### Features Added

  - Added operation JobsOperations.mark_devices_shipped
  - Added operation group DataBoxManagementClientOperationsMixin
  - Model DataBoxDiskJobDetails has a new parameter actions
  - Model DataBoxDiskJobDetails has a new parameter data_center_code
  - Model DataBoxDiskJobDetails has a new parameter datacenter_address
  - Model DataBoxDiskJobDetails has a new parameter device_erasure_details
  - Model DataBoxDiskJobDetails has a new parameter expected_data_size_in_tera_bytes
  - Model DataBoxDiskJobDetails has a new parameter granular_copy_log_details
  - Model DataBoxDiskJobDetails has a new parameter granular_copy_progress
  - Model DataBoxDiskJobDetails has a new parameter last_mitigation_action_on_job
  - Model DataBoxDiskJobDetails has a new parameter reverse_shipping_details
  - Model DataBoxHeavyJobDetails has a new parameter actions
  - Model DataBoxHeavyJobDetails has a new parameter data_center_code
  - Model DataBoxHeavyJobDetails has a new parameter datacenter_address
  - Model DataBoxHeavyJobDetails has a new parameter device_erasure_details
  - Model DataBoxHeavyJobDetails has a new parameter expected_data_size_in_tera_bytes
  - Model DataBoxHeavyJobDetails has a new parameter last_mitigation_action_on_job
  - Model DataBoxHeavyJobDetails has a new parameter reverse_shipping_details
  - Model DataBoxJobDetails has a new parameter actions
  - Model DataBoxJobDetails has a new parameter data_center_code
  - Model DataBoxJobDetails has a new parameter datacenter_address
  - Model DataBoxJobDetails has a new parameter device_erasure_details
  - Model DataBoxJobDetails has a new parameter expected_data_size_in_tera_bytes
  - Model DataBoxJobDetails has a new parameter last_mitigation_action_on_job
  - Model DataBoxJobDetails has a new parameter reverse_shipping_details
  - Model DataImportDetails has a new parameter log_collection_level
  - Model JobDetails has a new parameter actions
  - Model JobDetails has a new parameter data_center_code
  - Model JobDetails has a new parameter datacenter_address
  - Model JobDetails has a new parameter device_erasure_details
  - Model JobDetails has a new parameter expected_data_size_in_tera_bytes
  - Model JobDetails has a new parameter last_mitigation_action_on_job
  - Model JobDetails has a new parameter reverse_shipping_details
  - Model JobResource has a new parameter reverse_shipping_details_update
  - Model JobResource has a new parameter reverse_transport_preference_update
  - Model JobResource has a new parameter system_data
  - Model Preferences has a new parameter reverse_transport_preferences
  - Model Preferences has a new parameter storage_account_access_tier_preferences
  - Model RegionConfigurationRequest has a new parameter datacenter_address_request
  - Model RegionConfigurationResponse has a new parameter datacenter_address_response
  - Model SkuInformation has a new parameter countries_within_commerce_boundary
  - Model TransportPreferences has a new parameter is_updated
  - Model UpdateJobDetails has a new parameter preferences
  - Model UpdateJobDetails has a new parameter return_to_customer_package_details
  - Model UpdateJobDetails has a new parameter reverse_shipping_details

### Breaking Changes

  - Model DataBoxDiskJobDetails no longer has parameter expected_data_size_in_terabytes
  - Model DataBoxHeavyJobDetails no longer has parameter expected_data_size_in_terabytes
  - Model DataBoxJobDetails no longer has parameter expected_data_size_in_terabytes
  - Model DiskScheduleAvailabilityRequest has a new required parameter expected_data_size_in_tera_bytes
  - Model DiskScheduleAvailabilityRequest no longer has parameter expected_data_size_in_terabytes
  - Model JobDetails no longer has parameter expected_data_size_in_terabytes

## 1.0.0 (2021-03-18)

- GA release

## 1.0.0b1 (2020-11-30)

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

## 0.2.0 (2020-02-12)

**Features**

- Model DestinationAccountDetails has a new parameter share_password
- Model ValidateAddress has a new parameter transport_preferences
- Model DataBoxDiskJobSecrets has a new parameter dc_access_security_code
- Model Preferences has a new parameter transport_preferences
- Model DestinationManagedDiskDetails has a new parameter share_password
- Model AddressValidationOutput has a new parameter error
- Model DataBoxDiskJobDetails has a new parameter expected_data_size_in_terabytes
- Model DataboxJobSecrets has a new parameter dc_access_security_code
- Model JobResource has a new parameter delivery_info
- Model JobResource has a new parameter is_cancellable_without_fee
- Model JobResource has a new parameter delivery_type
- Model CopyProgress has a new parameter invalid_file_bytes_uploaded
- Model CopyProgress has a new parameter files_errored_out
- Model CopyProgress has a new parameter invalid_files_processed
- Model CopyProgress has a new parameter renamed_container_count
- Model CopyProgress has a new parameter data_destination_type
- Model DataBoxHeavyJobSecrets has a new parameter dc_access_security_code
- Model DestinationStorageAccountDetails has a new parameter share_password
- Model AccountCredentialDetails has a new parameter data_destination_type
- Model JobDetails has a new parameter expected_data_size_in_terabytes
- Model JobSecrets has a new parameter dc_access_security_code
- Model DataBoxJobDetails has a new parameter device_password
- Model DataBoxJobDetails has a new parameter expected_data_size_in_terabytes
- Model DataBoxHeavyJobDetails has a new parameter device_password
- Model DataBoxHeavyJobDetails has a new parameter expected_data_size_in_terabytes
- Added operation ServiceOperations.validate_inputs_by_resource_group
- Added operation ServiceOperations.validate_inputs
- Added operation ServiceOperations.list_available_skus_by_resource_group
- Added operation ServiceOperations.region_configuration

**Breaking changes**

- Operation ServiceOperations.validate_address_method has a new signature
- Model ValidateAddress has a new required parameter validation_type
- Model DataBoxDiskJobDetails no longer has parameter expected_data_size_in_tera_bytes
- Model JobDetails no longer has parameter expected_data_size_in_tera_bytes
- Model DataBoxJobDetails no longer has parameter expected_data_size_in_tera_bytes
- Model DataBoxHeavyJobDetails no longer has parameter expected_data_size_in_tera_bytes

## 0.1.0 (2020-02-05)

* Initial Release
