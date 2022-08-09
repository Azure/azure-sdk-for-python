# Release History

## 1.0.4 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

## 1.0.3 (2022-07-07)

### Bugs Fixed

- Fixed a bug where `query_resource` in metrics client is throwing an error with unexpected `metric_namespace` argument. 

## 1.0.2 (2022-05-06)

- This version and all future versions will require Python 3.6+. Python 2.7 is no longer supported.

### Bugs Fixed

- Fixed a bug where having a None value in datetime throws

## 1.0.1 (2021-11-09)

### Bugs Fixed

- Fixed a bug where Metadata values in timestamp don't show up sometimes.

## 1.0.0 (2021-10-06)

### Features Added

- Added `LogsQueryPartialResult` and `LogsQueryError` to handle errors.
- Added `status` attribute to `LogsQueryResult`.
- Added `LogsQueryStatus` Enum to describe the status of a result.
- Added a new `LogsTableRow` type that represents a single row in a table.
- Items in `metrics` list in `MetricsQueryResult` can now be accessed by metric names.

### Breaking Changes

- `LogsQueryResult` now iterates over the tables directly as a convenience.
- `query` API in logs is renamed to `query_workspace`
- `query` API in metrics is renamed to `query_resource`
- `query_workspace` API now returns a union of `LogsQueryPartialResult` and `LogsQueryResult`.
- `query_batch` API now returns a union of `LogsQueryPartialResult`, `LogsQueryError` and `LogsQueryResult`.
- `metric_namespace` is renamed to `namespace` and is a keyword-only argument in `list_metric_definitions` API.
- `MetricsResult` is renamed to `MetricsQueryResult`.

## 1.0.0b4 (2021-09-09)

### Features Added

- Added additional `display_description` attribute to the `Metric` type.
- Added a `MetricClass` enum to provide the class of a metric.
- Added a `metric_class` attribute to the `MetricDefinition` type.
- Added a `MetricNamespaceClassification` enum to support the `namespace_classification` attribute on `MetricNamespace` type.
- Added a `MetricUnit` enum to describe the unit of the metric.

### Breaking Changes

- Rename `batch_query` to `query_batch`.
- Rename `LogsBatchQueryRequest` to `LogsBatchQuery`.
- `include_render` is now renamed to `include_visualization` in the query API.
- `LogsQueryResult` now returns `visualization` instead of `render`.
- `start_time`, `duration` and `end_time` are now replaced with a single param called `timespan`
- `resourceregion` is renamed to `resource_region` in the MetricResult type.
- `top` is renamed to `max_results` in the metric's `query` API.
- `metric_namespace_name` is renamed to `fully_qualified_namespace`
- `is_dimension_required` is renamed to `dimension_required`
- `interval`  and `time_grain` are renamed to `granularity`
- `orderby` is renamed to `order_by`
- `LogsQueryResult` now returns `datetime` objects for a time values.
- `LogsBatchQuery` doesn't accept a `request_id` anymore.
- `MetricsMetadataValues` is removed. A dictionary is used instead.
- `time_stamp` is renamed to `timestamp` in `MetricValue` type.
- `AggregationType` is renamed to `MetricAggregationType`.
- Removed `LogsBatchResultError` type.
- `LogsQueryResultTable` is named to `LogsTable`
- `LogsTableColumn` is now removed. Column labels are strings instead.
- `start_time` in `list_metric_namespaces` API is now a datetime.
- The order of params in `LogsBatchQuery` is changed. Also, `headers` is no longer accepted.
- `timespan` is now a required keyword-only argument in logs APIs.
- batch api now returns a list of `LogsQueryResult` objects.

### Bugs Fixed

- `include_statistics` and `include_visualization` args can now work together.

## 1.0.0b3 (2021-08-09)

### Features Added

- Added enum `AggregationType` which can be used to specify aggregations in the query API.
- Added `LogsBatchQueryResult` model that is returned for a logs batch query.
- Added `error` attribute to `LogsQueryResult`.

### Breaking Changes

- `aggregation` param in the query API is renamed to `aggregations`
- `batch_query` API now returns a list of responses.
- `LogsBatchResults` model is now removed.
- `LogsQueryRequest` is renamed to `LogsBatchQueryRequest`
- `LogsQueryResults` is now renamed to `LogsQueryResult`
- `LogsBatchQueryResult` now has 4 additional attributes - `tables`, `error`, `statistics` and `render` instead of `body` attribute.

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
