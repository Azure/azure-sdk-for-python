# Release History

## 1.0.0b2 (Unreleased)

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

