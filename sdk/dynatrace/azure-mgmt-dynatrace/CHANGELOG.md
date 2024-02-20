# Release History

## 2.0.0 (2023-08-18)

### Features Added

  - Added operation MonitorsOperations.get_marketplace_saa_s_resource_details
  - Added operation MonitorsOperations.get_metric_status
  - Model MetricRules has a new parameter sending_metrics

### Breaking Changes

  - Model MonitorResourceUpdate no longer has parameter dynatrace_environment_properties
  - Model MonitorResourceUpdate no longer has parameter marketplace_subscription_status
  - Model MonitorResourceUpdate no longer has parameter monitoring_status
  - Model MonitorResourceUpdate no longer has parameter plan_data
  - Model MonitorResourceUpdate no longer has parameter user_info
  - Parameter region of model LinkableEnvironmentRequest is now required
  - Parameter tenant_id of model LinkableEnvironmentRequest is now required
  - Parameter user_principal of model LinkableEnvironmentRequest is now required
  - Parameter user_principal of model SSODetailsRequest is now required
  - Removed operation MonitorsOperations.get_account_credentials
  - Removed operation TagRulesOperations.update

## 1.1.0b1 (2022-12-27)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 1.0.0 (2022-09-16)

### Breaking Changes

  - Client name is changed from `DynatraceObservability` to `DynatraceObservabilityMgmtClient`

## 1.0.0b1 (2022-05-19)

* Initial Release
