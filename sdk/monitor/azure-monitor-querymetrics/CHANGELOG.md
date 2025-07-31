# Release History

## 1.0.1 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

## 1.0.0 (2025-07-28)

### Features Added

- **Initial release** of `azure-monitor-querymetrics` package with core Azure Monitor metrics querying functionality.
- Includes the `MetricsClient` for querying metrics from Azure Monitor resources.

**Migration from azure-monitor-query**

This package extracts the metrics functionality from the `azure-monitor-query` package to provide a focused solution for metrics querying.

**For existing users of `MetricsClient`:**
- Migration is straightforward - only import paths need to be updated.
- The API surface remains unchanged.
- **Before:** `from azure.monitor.query import MetricsClient`
- **After:** `from azure.monitor.querymetrics import MetricsClient`

**For users of `MetricsQueryClient`:**
- This functionality is **not included** in this package.
- **Recommended alternative:** Use `MonitorManagementClient` from the `azure-mgmt-monitor` package.
- The management client provides comprehensive Azure Monitor resource management capabilities.

For more details, see the [migration guide](https://aka.ms/azsdk/python/monitor/query/migration).
