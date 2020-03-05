# Release History

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
