# Release History

## 1.0.0b3 (2023-01-01)

### Features Added 
- Method added `azure.developer.loadtesting.LoadTestingClient.load_test_run.list_metric_namespaces`
- Method added `azure.developer.loadtesting.LoadTestingClient.load_test_run.list_metric_definitions`
- Method added `azure.developer.loadtesting.LoadTestingClient.load_test_run.list_metrics`
- Method added `azure.developer.loadtesting.LoadTestingClient.load_test_run.create_or_update_app_components`
- Method added `azure.developer.loadtesting.LoadTestingClient.load_test_run.list_app_components`
- Method added `azure.developer.loadtesting.LoadTestingClient.load_test_run.create_or_update_server_metrics_config`
- Method added `azure.developer.loadtesting.LoadTestingClient.load_test_run.get_server_metrics_config`
- Method added `azure.developer.loadtesting.LoadTestingClient.load_test_administration.begin_get_test_script_validation_status`
- Method added `azure.developer.loadtesting.LoadTestingClient.load_test_run.begin_test_run_status`
- Method added `azure.developer.loadtesting.aio.LoadTestingClient.load_test_run.list_metric_namespaces`
- Method added `azure.developer.loadtesting.aio.LoadTestingClient.load_test_run.list_metric_definitions`
- Method added `azure.developer.loadtesting.aio.LoadTestingClient.load_test_run.list_metrics`
- Method added `azure.developer.loadtesting.aio.LoadTestingClient.load_test_run.create_or_update_app_components`
- Method added `azure.developer.loadtesting.aio.LoadTestingClient.load_test_run.list_app_components`
- Method added `azure.developer.loadtesting.aio.LoadTestingClient.load_test_run.create_or_update_server_metrics_config`
- Method added `azure.developer.loadtesting.aio.LoadTestingClient.load_test_run.get_server_metrics_config`
- Method added `azure.developer.loadtesting.aio.LoadTestingClient.load_test_administration.begin_get_test_script_validation_status`
- Method added `azure.developer.loadtesting.aio.LoadTestingClient.load_test_run.begin_test_run_status`
- Method added `azure.developer.loadtesting.aio.LoadTestingClient.load_test_run.get_metric_dimension_values`

### Breaking Changes
- renamed subclient from `load_test_runs` to `load_test_run`
- renamed `azure.developer.loadtesting.LoadTestingClient.load_test_administration.delete_load_test` to `azure.developer.loadtesting.LoadTestingClient.load_test_administration.delete_test`
- renamed `azure.developer.loadtesting.LoadTestingClient.load_test_administration.get_load_test` to `azure.developer.loadtesting.LoadTestingClient.load_test_administration.get_test`
- renamed `azure.developer.loadtesting.LoadTestingClient.load_test_administration.list_load_test` to `azure.developer.loadtesting.LoadTestingClient.load_test_administration.list_tests`
- renamed `azure.developer.loadtesting.aio.LoadTestingClient.load_test_administration.delete_load_test` to `azure.developer.loadtesting.aio.LoadTestingClient.load_test_administration.delete_test`
- renamed `azure.developer.loadtesting.aio.LoadTestingClient.load_test_administration.get_load_test` to `azure.developer.loadtesting.aio.LoadTestingClient.load_test_administration.get_test`
- renamed `azure.developer.loadtesting.aio.LoadTestingClient.load_test_administration.list_load_test` to `azure.developer.loadtesting.aio.LoadTestingClient.load_test_administration.list_tests`
- renamed `azure.developer.loadtesting.LoadTestingClient.load_test_administration.list_load_test_search` to `azure.developer.loadtesting.LoadTestingClient.load_test_administration.list_load_tests`
- renamed `azure.developer.loadtesting.LoadTestingClient.load_test_runs.create_or_update_test` to `azure.developer.loadtesting.LoadTestingClient.load_test_runs.create_or_update_test_run`
- renamed `azure.developer.loadtesting.aio.LoadTestingClient.load_test_administration.list_load_test_search` to `azure.developer.loadtesting.aio.LoadTestingClient.load_test_administration.list_load_tests`
- renamed `azure.developer.loadtesting.aio.LoadTestingClient.load_test_runs.create_or_update_test` to `azure.developer.loadtesting.aio.LoadTestingClient.load_test_runs.create_or_update_test_run`
- removed `azure.developer.loadtesting.LoadTestingClient.load_test_runs.get_test_run_client_metrics`
- removed `azure.developer.loadtesting.LoadTestingClient.load_test_runs.get_test_run_client_metrics_filters`
- removed `azure.developer.loadtesting.LoadTestingClient.load_test_administration.delete_app_components`
- removed `azure.developer.loadtesting.LoadTestingClient.load_test_administration.get_server_metrics_config_by_name`
- removed `azure.developer.loadtesting.LoadTestingClient.load_test_administration.delete_server_metrics_config`
- removed `azure.developer.loadtesting.LoadTestingClient.load_test_administration.get_server_default_metrics_config`
- removed `azure.developer.loadtesting.LoadTestingClient.load_test_administration.get_server_metrics_config`
- removed `azure.developer.loadtesting.LoadTestingClient.load_test_administration.list_supported_resource_types`
- removed `azure.developer.loadtesting.aio.LoadTestingClient.load_test_runs.get_test_run_client_metrics`
- removed `azure.developer.loadtesting.aio.LoadTestingClient.load_test_runs.get_test_run_client_metrics_filters`
- removed `azure.developer.loadtesting.aio.LoadTestingClient.load_test_administration.delete_app_components`
- removed `azure.developer.loadtesting.aio.LoadTestingClient.load_test_administration.get_server_metrics_config_by_name`
- removed `azure.developer.loadtesting.aio.LoadTestingClient.load_test_administration.delete_server_metrics_config`
- removed `azure.developer.loadtesting.aio.LoadTestingClient.load_test_administration.get_server_default_metrics_config`
- removed `azure.developer.loadtesting.aio.LoadTestingClient.load_test_administration.get_server_metrics_config`
- removed `azure.developer.loadtesting.aio.LoadTestingClient.load_test_administration.list_supported_resource_types`

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
