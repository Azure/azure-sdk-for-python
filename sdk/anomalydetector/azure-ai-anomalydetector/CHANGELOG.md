# Release History

## 3.0.0 (2023-04-12)

### Other Changes

  - GA release

## 3.0.0b6 (2022-12-08)
  **Features**
  - Added `OneTable` and `MultiTable` two data schemas.
  - Added `DataSchema` to `ModelInfo`.
  - Added Azure Managed Identity data reader access for Azure Blob Storage.
  - Added `topContributorCount` in the request body for `get_multivariate_batch_detection_result`, `detect_multivariate_batch_anomaly` and `detect_multivariate_last_anomaly`.

  **Breaking Changes**
  - Renamed `Model` to `AnomalyDetectionModel`.
  - Renamed `DetectionRequest` to `MultivariateBatchDetectionOptions`.
  - Renamed `DetectionResult` to `MultivariateDetectionResult`.
  - Renamed `DetectionStatus` to `MultivariateBatchDetectionStatus`.
  - Renamed `DetectionResultSummary` to `MultivariateBatchDetectionResultSummary`.
  - Renamed `FillNaMethod` to `FillNAMethod`.
  - Renamed `LastDetectionRequest` to `MultivariateLastDetectionOptions`.
  - Renamed `LastDetectionResult` to `MultivariateLastDetectionResult`.
  - Replaced `ModelSnapshot` with `AnomalyDetectionModel` in `list_multivariate_model`.
  - Renamed `train_multivariate_model_with_response` to `train_multivariate_model`.
  - Renamed `detect_anomaly_with_response` to `detect_multivariate_batch_anomaly`.
  - Renamed `get_detection_result` to `get_multivariate_batch_detection_result`.
  - Renamed `list_multivariate_model` to `list_multivariate_models`.
  - Renamed `last_detect_anomaly_with_response` to `detect_multivariate_last_anomaly`.
  - Renamed `DetectRequest` to `UnivariateDetectionOptions`.
  - Renamed `EntireDetectResponse` to `UnivariateEntireDetectionResult`.
  - Renamed `LastDetectResponse` to `UnivariateLastDetectionResult`.
  - Renamed `ChangePointDetectRequest` to `UnivariateChangePointDetectionOptions`.
  - Renamed `ChangePointDetectResponse` to `UnivariateChangePointDetectionResult`.
  - Renamed `detect_entire_series` to `detect_univariate_entire_series`.
  - Renamed `detect_last_point` to `detect_univariate_last_point`.
  - Renamed `detect_change_point` to `detect_univariate_change_point`.
  - Removed `AnomalyDetectorErrorException`.
  - Removed `export_model_with_response`.
  - Removed `changedvalue` in the inference response body.
  - Removed `detecting_points` in the sync inference request body.

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
