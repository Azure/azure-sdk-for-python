# Release History

## 1.0.0b2 (Unreleased)

**Breaking Changes**

- `create_data_feed` now takes as input a `DataFeed` object
- `create_metric_anomaly_detection_configuration` now takes as input an `AnomalyDetectionConfiguration` object
- `create_anomaly_detection_configuration` now takes as input an `AnomalyAlertConfiguration` object
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

**New Features**

- `__repr__` added to all models

## 1.0.0b1 (2020-10-07)

First preview release

