# Release History

## 3.0.0b6 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

- Python 2.7 is no longer supported. Please use Python version 3.6 or later.

## 3.0.0b5 (2022-01-23)

  - Fix release issues

## 3.0.0b4 (2022-01-18)

  **Features**
  - Introduced the new API: `AnomalyDetectorClientOperationsMixin.last_detect_anomaly`.
  - Added 2 new optional properties: `impute_mode` & `impute_fixed_value` to `DetectRequest` object.
  - Added 1 new optional property: `severity` to the `EntireDetectResponse` & `LastDetectResponse` objects.
  - Removed the optional property `errors` from the `VariableState` object.
  - Refactored the optional property `contributors` to `interpretation` from the `AnomalyValue` object.
  - Modified the `FillNAMethod` object into an extensible enum.

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
