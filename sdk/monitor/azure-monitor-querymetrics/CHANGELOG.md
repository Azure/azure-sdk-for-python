# Release History

## 1.0.0 (2025-07-28)

### Features Added

- Initial release. This version includes the core functionality for querying metrics from Azure Monitor using the `MetricsClient`, which was originally introduced in the `azure-monitor-query` package.
- Migration from `azure-monitor-query` to `azure-monitor-querymetrics` is straightforward, as the API surface remains largely unchanged. Only the import paths need to be updated to reflect the new package name:
  - Example: `from azure.monitor.query import MetricsClient` to `from azure.monitor.querymetrics import MetricsClient`
