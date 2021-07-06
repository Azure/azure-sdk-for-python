# Release History

## 3.0.0b3 (2021-04-16)

  **Features**
  - Added operation AnomalyDetectorClientOperationsMixin.list_multivariate_model
  - Added operation AnomalyDetectorClientOperationsMixin.train_multivariate_model
  - Added operation AnomalyDetectorClientOperationsMixin.detect_anomaly
  - Added operation AnomalyDetectorClientOperationsMixin.get_detection_result
  - Added operation AnomalyDetectorClientOperationsMixin.get_multivariate_model
  - Added operation AnomalyDetectorClientOperationsMixin.export_model
  - Added operation AnomalyDetectorClientOperationsMixin.delete_multivariate_model

## 3.0.0b2 (2020-08-27)

  **Bug Fixes**
  - Fixed an issue with ChangePointDetect

  **Breaking Changes**
  - Renamed `entire_detect` to `detect_entire_series`
  - Renamed `APIError` to `AnomalyDetectorError`
  - Renamed `Request` to `DetectRequest`
  - Renamed `last_detect` to `detect_last_point`
  - Renamed `change_point_detect` to `detect_change_point`
  - Renamed `Granularity` to `TimeGranularity`
  - Renamed `minutely` and `secondly` to `per_minute` and `per_second`
  - Renamed `Point` to `TimeSeriesPoint`


## 3.0.0b1 (2020-08-17)

  - Initial Release
