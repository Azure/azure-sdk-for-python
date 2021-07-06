# Release History

## 1.0.0b2 (2021-07-06)

### Breaking Changes

- `workspaces`, `workspace_ids`, `qualified_names` and `azure_resource_ids` are now merged into a single `additional_workspaces` list in the query API.
- The `LogQueryRequest` object now takes in a `workspace_id` and `additional_workspaces` instead of `workspace`.
- `aggregation` param is now a list instead of a string in the `query` method.
- `duration` must now be provided as a timedelta instead of a string.


## 1.0.0b1 (2021-06-10)

  **Features**
  - Version (1.0.0b1) is the first preview of our efforts to create a user-friendly and Pythonic client library for Azure Monitor Query.
  For more information about this, and preview releases of other Azure SDK libraries, please visit https://azure.github.io/azure-sdk/releases/latest/python.html.
  - Added `~azure.monitor.query.LogsQueryClient` to query log analytics along with `~azure.monitor.query.aio.LogsQueryClient`.
  - Implements the `~azure.monitor.query.MetricsQueryClient` for querying metrics, listing namespaces and metric definitions along with `~azure.monitor.query.aio.MetricsQueryClient`.
