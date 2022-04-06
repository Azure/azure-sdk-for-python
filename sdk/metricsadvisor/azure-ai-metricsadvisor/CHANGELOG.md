# Release History

## 1.1.0 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes
- Python 2.7 is no longer supported. Please use Python version 3.6 or later.

## 1.0.0 (2021-07-06)

### Breaking Changes

- Changed
  - `DetectionConditionsOperator` -> `DetectionConditionOperator`
  - `cross_conditions_operator` -> `condition_operator`
  - `AnomalyAlert.created_on` -> `AnomalyAlert.created_time`
  - `AnomalyAlert.modified_on` -> `AnomalyAlert.modified_time`
  - `Anomaly.created_on` -> `Anomaly.created_time`
  - `admin_emails` has been renamed to `admins` in `NotificationHook`
  - `admin_emails` has been renamed to `admins` in `DataFeedOptions`
  - `viewer_emails` has been renamed to `viewers` in `DataFeedOptions`

## 1.0.0b4 (2021-06-07)

**New Features**

- Added `AzureLogAnalyticsDataFeedSource` and `AzureEventHubsDataFeedSource`
- Update method now returns the updated object
- Added DatasourceCredentials and DatasourceCredential operations
- Added authentication type support for data feed

**Breaking Changes**

- Delete methods now take positional only argument as id
- `update_subscription_key` and `update_api_key` are merged into one method `update_key`
- Removed `DataFeedOptions` and moved all its properties to the `DataFeed` model

- Deprecated:
  - `HttpRequestDataFeed`
  - `ElasticsearchDataFeed`

- Renamed
  - `AzureApplicationInsightsDataFeed` -> `AzureApplicationInsightsDataFeedSource`
  - `AzureBlobDataFeed` -> `AzureBlobDataFeedSource`
  - `AzureCosmosDBDataFeed` -> `AzureCosmosDbDataFeedSource`
  - `AzureDataExplorerDataFeed` -> `AzureDataExplorerDataFeedSource`
  - `AzureTableDataFeed` -> `AzureTableDataFeedSource`
  - `InfluxDBDataFeed` -> `InfluxDbDataFeedSource`
  - `MySqlDataFeed` -> `MySqlDataFeedSource`
  - `PostgreSqlDataFeed` -> `PostgreSqlDataFeedSource`
  - `SQLServerDataFeed` -> `SqlServerDataFeedSource`
  - `MongoDBDataFeed` -> `MongoDbDataFeedSource`
  - `AzureDataLakeStorageGen2DataFeed` -> `AzureDataLakeStorageGen2DataFeedSource`

**Dependency Updates**

- Bump `msrest` requirement from `0.6.12` to `0.6.21`

## 1.0.0b3 (2021-02-09)

**New Features**

- AAD support authentication    #15922
- `MetricsAdvisorKeyCredential` support for rotating the subscription and api keys to update long-lived clients
  
**Breaking Changes**

- `list_dimension_values` has been renamed to `list_anomaly_dimension_values`
- update methods now return None
- Updated DataFeed.metric_ids to be a dict rather than a list

**Hotfixes**

- Bump `six` requirement from `1.6` to 1.11.0`

## 1.0.0b2 (2020-11-10)

**Breaking Changes**

- `create_hook` now takes as input an `EmailHook` or `WebHook`
- `Anomaly` has been renamed to `DataPointAnomaly`
- `Incident` has been renamed to `AnomalyIncident`
- `IncidentPropertyIncidentStatus` has been renamed to `AnomalyIncidentStatus`
- `Alert` has been renamed to `AnomalyAlert`
- `Severity` has been renamed to `AnomalySeverity`
- `Metric` has been renamed to `DataFeedMetric`
- `Dimension` has been renamed to `DataFeedDimension`
- `EmailHook` has been renamed to `EmailNotificationHook`
- `WebHook` has been renamed to `WebNotificationHook`
- `Hook` has been renamed to `NotificationHook`
- `TimeMode` has been renamed to `AlertQueryTimeMode`
- `admins` has been renamed to `admin_emails` on `NotificationHook`
- `admins` has been renamed to `admin_emails` on `DataFeedOptions`
- `viewers` has been renamed to `viewer_emails` on `DataFeedOptions`
- `timestamp_list` has been renamed to `timestamps` on `MetricSeriesData`
- `value_list` has been renamed to `values` on `MetricSeriesData`
- `SeriesResult` has been renamed to `MetricEnrichedSeriesData`
- `create_anomaly_alert_configuration` has been renamed to `create_alert_configuration`
- `get_anomaly_alert_configuration` has been renamed to `get_alert_configuration`
- `delete_anomaly_alert_configuration` has been renamed to `delete_alert_configuration`
- `update_anomaly_alert_configuration` has been renamed to `update_alert_configuration`
- `list_anomaly_alert_configurations` has been renamed to `list_alert_configurations`
- `create_metric_anomaly_detection_configuration` has been renamed to `create_detection_configuration`
- `get_metric_anomaly_detection_configuration` has been renamed to `get_detection_configuration`
- `delete_metric_anomaly_detection_configuration` has been renamed to `delete_detection_configuration`
- `update_metric_anomaly_detection_configuration` has been renamed to `update_detection_configuration`
- `list_metric_anomaly_detection_configurations` has been renamed to `list_detection_configurations`
- `list_feedbacks` has been renamed to `list_feedback`
- `list_alerts_for_alert_configuration` has been renamed to `list_alerts`
- `list_anomalies_for_alert` & `list_anomalies_for_detection_configuration` have been grouped into `list_anomalies`
- `list_dimension_values_for_detection_configuration` has been renamed to `list_dimension_values`
- `list_incidents_for_alert` & `list_incidents_for_detection_configuration` have been grouped into `list_incidents`

**New Features**

- `__repr__` added to all models

## 1.0.0b1 (2020-10-07)

First preview release
