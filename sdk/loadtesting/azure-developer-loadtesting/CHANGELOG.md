# Release History

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
