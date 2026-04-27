# Release History

## 1.0.0b2 (Unreleased)

### Features Added

  - Updated API version to `2026-01-01-preview`
  - Added new enum `DependenciesAggregationUnit` with `Absolute` and `Percentage` values
  - Added new enum `DiscoveryRuleKind` with `ResourceGraphQuery` and `ApplicationInsightsTopology` values
  - Added new models: `ApplicationInsightsTopologySpecification`, `AzureResourceSignal`, `AzureResourceSignals`, `AzureMonitorWorkspaceSignals`, `DependenciesSignalGroupV2`, `DiscoveryError`, `DiscoveryRuleSpecification`, `EntityHistoryRequest`, `EntityHistoryResponse`, `ExternalSignal`, `ExternalSignalGroup`, `HealthReportEvaluationRule`, `HealthReportRequest`, `HealthStateTransition`, `LogAnalyticsSignal`, `LogAnalyticsSignals`, `PrometheusMetricsSignal`, `ResourceGraphQuerySpecification`, `SignalGroups`, `SignalHistoryDataPoint`, `SignalHistoryRequest`, `SignalHistoryResponse`, `SignalInstanceProperties`, `SignalStatus`, `ThresholdRuleV2`

### Breaking Changes

  - Removed enum value `DependenciesAggregationType.THRESHOLDS`, replaced by `MIN_HEALTHY` and `MAX_NOT_HEALTHY`
  - Removed enums: `DynamicThresholdDirection`, `DynamicThresholdModel`
  - Removed models: `AzureMonitorWorkspaceSignalGroup`, `AzureResourceSignalGroup`, `DependenciesSignalGroup`, `DynamicDetectionRule`, `HealthModelUpdateProperties`, `LogAnalyticsSignalGroup`, `ModelDiscoverySettings`, `SignalAssignment`, `SignalGroup`, `ThresholdRule`
  - Renamed `setup.py`-based packaging to `pyproject.toml`

## 1.0.0b1 (2025-06-04)

### Other Changes

  - Initial version
