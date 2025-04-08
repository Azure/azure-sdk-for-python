# Release History

## 1.1.0b1 (2025-03-27)

Updated the client library to use API Version 2025-05-01-preview. This adds all the capabilities that were introduced until this API version.

This version and all future versions will require Python 3.8+. Python 3.7 is no longer supported.

### Features Added

- This release adds models and enums for all the APIs supported by Azure Load Testing   
- Support for AutoStop Criteria
    - Use `auto_stop_criteria` property on the `Test` model to add autostop criteria
- Support for Quick Load Tests with RPS (Requests Per Second) Inputs
    - Use `requests_per_second` and `max_response_time_in_ms` in `OptionalLoadTestConfig` model to specify desired RPS for a quick load test
- Support for URL Tests with JSON based test plans
    - Added enum `TestKind` with value `URL` and support for `URL_TEST_CONFIG` file type in the `FileType` enum
- Support for Locust Load Tests
    - Added value `Locust` in the `TestKind` enum
- Support for Multi Region Load Tests
    - Added property `regional_load_test_config` in `LoadTestConfiguration` model to specify regional load distribution
- Support for Disabling Public IP Deployment for Private Load Tests
    - Added property `public_ip_disabled` to the `Test` model to disable injecting public IP
- Support for uploading ZIP Artifacts
    - Added value `ZIPPED_ARTIFACTS` in the `FileType` enum
- Support for all Test Profiles & Test Profile Run Scenarios
    - Added methods `create_or_update_test_profile`, `get_test_profile`, `delete_test_profile` and `list_test_profiles` in `LoadTestAdministrationClient` to work with Test Profiles
    - Added methods `begin_test_profile_run`, `get_test_profile_run`, `delete_test_profile_run` and `list_test_profile_runs` in `LoadTestRunClient` to work with Test Profile Runs

## 1.0.1 (2025-01-20)

### Bugs Fixed

- Update API response enum typo for VALIDATION_FAILURE

### Other Changes

- Add NOT_VALIDATED to the list of terminal states for the file validation poller

## 1.0.0 (2023-03-07)

### Breaking Changes
- moved all operations under `azure.developer.loadtesting.LoadTestingClient.test_run` to `azure.developer.loadtesting.LoadTestRunClient` 
- moved all operations under `azure.developer.loadtesting.LoadTestingClient.administration` to `azure.developer.loadtesting.LoadTestAdministrationClient` 
- moved all operations under `azure.developer.loadtesting.aio.LoadTestingClient.test_run` to `azure.developer.loadtesting.aio.LoadTestRunClient` 
- moved all operations under `azure.developer.loadtesting.aio.LoadTestingClient.administration` to `azure.developer.loadtesting.aio.LoadTestAdministrationClient` 
- removed `azure.developer.loadtesting.LoadTestingClient.administration.upload_test_file` as it moved all functionality to `azure.developer.loadtesting.LoadTestAdministrationClient.begin_upload_test_file`
- removed `azure.developer.loadtesting.aio.LoadTestingClient.administration.upload_test_file` as it moved all functionality to `azure.developer.loadtesting.aio.LoadTestAdministrationClient.begin_upload_test_file`
- removed `azure.developer.loadtesting.LoadTestingClient.test_run.create_or_update_test_run` as it moved all functionality to `azure.developer.loadtesting.LoadTestRunClient.begin_test_run`
- removed `azure.developer.loadtesting.aio.LoadTestingClient.test_run.create_or_update_test_run` as it moved all functionality to `azure.developer.loadtesting.aio.LoadTestRunClient.begin_test_run`
- removed `azure.developer.loadtesting.aio.LoadTestingClient.test_run.list_metric_definitions` as it moved all functionality to `azure.developer.loadtesting.aio.LoadTestRunClient.get_metric_definitions`
- removed `azure.developer.loadtesting.LoadTestingClient.test_run.list_metric_definitions` as it moved all functionality to `azure.developer.loadtesting.LoadTestRunClient.get_metric_definitions`
- removed `azure.developer.loadtesting.aio.LoadTestingClient.test_run.list_metric_definitions` as it moved all functionality to `azure.developer.loadtesting.aio.LoadTestRunClient.get_metric_definitions`
- removed `azure.developer.loadtesting.LoadTestingClient.test_run.list_metric_namespaces` as it moved all functionality to `azure.developer.loadtesting.LoadTestRunClient.get_metric_namespaces`

### Other Changes
- bumped version to stable `1.0.0`
- updated README.md

## 1.0.0b3 (2023-01-01)

### Features Added 
- Method added `azure.developer.loadtesting.LoadTestingClient.test_run.list_metric_namespaces`
- Method added `azure.developer.loadtesting.LoadTestingClient.test_run.list_metric_definitions`
- Method added `azure.developer.loadtesting.LoadTestingClient.test_run.list_metrics`
- Method added `azure.developer.loadtesting.LoadTestingClient.test_run.create_or_update_app_components`
- Method added `azure.developer.loadtesting.LoadTestingClient.test_run.get_app_components`
- Method added `azure.developer.loadtesting.LoadTestingClient.test_run.create_or_update_server_metrics_config`
- Method added `azure.developer.loadtesting.LoadTestingClient.test_run.get_server_metrics_config`
- Method added `azure.developer.loadtesting.LoadTestingClient.administration.begin_upload_test_file`
- Method added `azure.developer.loadtesting.LoadTestingClient.test_run.begin_test_run`
- Method added `azure.developer.loadtesting.LoadTestingClient.test_run.begin_test_run_status`
- Method added `azure.developer.loadtesting.aio.LoadTestingClient.test_run.list_metric_namespaces`
- Method added `azure.developer.loadtesting.aio.LoadTestingClient.test_run.list_metric_definitions`
- Method added `azure.developer.loadtesting.aio.LoadTestingClient.test_run.list_metrics`
- Method added `azure.developer.loadtesting.aio.LoadTestingClient.test_run.create_or_update_app_components`
- Method added `azure.developer.loadtesting.aio.LoadTestingClient.test_run.get_app_components`
- Method added `azure.developer.loadtesting.aio.LoadTestingClient.test_run.create_or_update_server_metrics_config`
- Method added `azure.developer.loadtesting.aio.LoadTestingClient.test_run.get_server_metrics_config`
- Method added `azure.developer.loadtesting.aio.LoadTestingClient.administration.begin_upload_test_file`
- Method added `azure.developer.loadtesting.aio.LoadTestingClient.test_run.begin_test_run_status`
- Method added `azure.developer.loadtesting.aio.LoadTestingClient.test_run.get_metric_dimension_values`
- Method added `azure.developer.loadtesting.aio.LoadTestingClient.test_run.begin_test_run`


### Breaking Changes
- Changed subclients `load_test_runs` and `load_test_adminsitration` to `test_run` and `adminsitrative` respectively
- Removed `continuation_token` as a parameter for method `azure.developer.loadtesting.aio.LoadTestingClient.test_run.list_test_runs`
- Removed `continuation_token` as a parameter for method `azure.developer.loadtesting.LoadTestingClient.test_run.list_test_runs`,
- Removed `continuation_token` as a parameter for method `azure.developer.loadtesting.aio.LoadTestingClient.administration.list_test_files`
- Removed `continuation_token` as a parameter for method `azure.developer.loadtesting.LoadTestingClient.administration.list_test_files`
- Removed `continuation_token` as a parameter for method `azure.developer.loadtesting.aio.LoadTestingClient.administration.list_tests`
- Removed `continuation_token` as a parameter for method `azure.developer.loadtesting.LoadTestingClient.administration.list_tests`

### Other Changes
- Updated README

## 1.0.0b2 (2022-10-17)

### Bug Fixed 
- `delete_app_components` method from `azure.developer.loadtesting.LoadTestingClient.load_test_administration.delete_app_components` was not discoverable in expected location, fixed discoverability.

### Other Changes
- Updated README

## 1.0.0b1 (2022-07-28)

### Features Added
- Initial version
