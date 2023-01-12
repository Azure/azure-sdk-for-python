# Release History

## 1.0.0b3 (2023-01-01)

### Features Added 
- Method added `azure.developer.loadtesting.LoadTestRunClient.list_metric_namespaces`
- Method added `azure.developer.loadtesting.LoadTestRunClient.list_metric_definitions`
- Method added `azure.developer.loadtesting.LoadTestRunClient.list_metrics`
- Method added `azure.developer.loadtesting.LoadTestRunClient.create_or_update_app_components`
- Method added `azure.developer.loadtesting.LoadTestRunClient.get_app_components`
- Method added `azure.developer.loadtesting.LoadTestRunClient.create_or_update_server_metrics_config`
- Method added `azure.developer.loadtesting.LoadTestRunClient.get_server_metrics_config`
- Method added `azure.developer.loadtesting.LoadTestAdministration.begin_upload_test_file`
- Method added `azure.developer.loadtesting.LoadTestRunClient.begin_test_run`
- Method added `azure.developer.loadtesting.LoadTestRunClient.begin_test_run_status`
- Method added `azure.developer.loadtesting.aio.LoadTestRunClient.list_metric_namespaces`
- Method added `azure.developer.loadtesting.aio.LoadTestRunClient.list_metric_definitions`
- Method added `azure.developer.loadtesting.aio.LoadTestRunClient.list_metrics`
- Method added `azure.developer.loadtesting.aio.LoadTestRunClient.create_or_update_app_components`
- Method added `azure.developer.loadtesting.aio.LoadTestRunClient.get_app_components`
- Method added `azure.developer.loadtesting.aio.LoadTestRunClient.create_or_update_server_metrics_config`
- Method added `azure.developer.loadtesting.aio.LoadTestRunClient.get_server_metrics_config`
- Method added `azure.developer.loadtesting.aio.LoadTestAdministration.begin_upload_test_file`
- Method added `azure.developer.loadtesting.aio.LoadTestRunClient.begin_test_run_status`
- Method added `azure.developer.loadtesting.aio.LoadTestRunClient.get_metric_dimension_values`
- Method added `azure.developer.loadtesting.aio.LoadTestRunClient.begin_test_run`


### Breaking Changes
- Changed subclients `load_test_runs` and `load_test_adminsitration` to `test_run` and `adminsitrative` respectively

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
