# Release History

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
