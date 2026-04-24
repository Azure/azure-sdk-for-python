# Release History

## 1.0.0b1 (2026-04-22)

### Features Added

- Initial preview release of `azure-mgmt-monitorslis` for managing
  Service Level Indicator (SLI) resources under the `Microsoft.Monitor` namespace.
- Support for SLI resource CRUD operations: create or update, get, delete, and list.
- SLI evaluation with Availability and Latency categories, supporting both
  window-based and request-based evaluation types with configurable signal sources,
  aggregation, and SLO baselines.
- Integration with Azure Monitor Workspace (AMW) accounts for metric emission,
  with managed identity and alert support.

### Other Changes

  - Initial version