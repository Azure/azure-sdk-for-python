# Guide for migrating to azure-ai-anomalydetector v3.0.0b7 from azure-cognitiveservices-anomalydetector v0.3.0

This guide is intended to assist in the migration to azure-ai-anomalydetector v3.0.0b7 from azure-cognitiveservices-anomalydetector v0.3.0.

It will focus on side-by-side comparisons for similar operations between the two packages.

Familiarity with the `azure-cognitiveservices-anomalydetector` v0.3.0 package is assumed.
For those new to the Azure Form Recognizer library for Python, please refer to the [README for `azure-ai-anomalydetector`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/anomalydetector/azure-ai-anomalydetector/README.md) rather than this guide. Please note that the Azure AI Anomaly Detector service will be [retired on October 1, 2026](https://azure.microsoft.com/updates/ai-services-anomaly-detector-will-be-retired-on-1-october-2026/).

## Table of contents

* [Migration benefits](#migration-benefits)
  * [New Features](#new-features)
* [Important changes](#important-changes)
  * [Anomaly Detection for Entire Series in Batch](#anomaly-detection-for-entire-series-in-batch)
  * [Anomaly Detection Status of Latest Point in Time Series](#anomaly-detection-status-of-latest-point-in-time-series)
  * [Change Point Detection for Entire Series](#change-point-detection-for-entire-series)
* [Samples](#samples)

## Migration benefits

A natural question to ask when considering whether or not to adopt a new version or library is what
the benefits of doing so would be. As Azure has matured and been embraced by a more diverse group of developers,
we have been focused on learning the patterns and practices to best support developer productivity and
to understand the gaps that the Python client libraries have.

There were several areas of consistent feedback expressed across the Azure client library ecosystem.
One of the most important is that the client libraries for different Azure services have not had a
consistent approach to organization, naming, and API structure. Additionally, many developers have felt
that the learning curve was difficult, and the APIs did not offer a good, approachable,
and consistent onboarding story for those learning Azure or exploring a specific Azure service.

To try and improve the development experience across Azure services,
a set of uniform [design guidelines](https://azure.github.io/azure-sdk/general_introduction.html) was created
for all languages to drive a consistent experience with established API patterns for all services.
A set of [Python-specific guidelines](https://azure.github.io/azure-sdk/python/guidelines/index.html) was also introduced to ensure
that Python clients have a natural and idiomatic feel with respect to the Python ecosystem.
Further details are available in the guidelines for those interested.

### New Features

We have a variety of new features in the version v3.0.0b7 of the AI Anomaly Detector library.

- The `AnomalyDetectorClient` now additionally provides the following operations:
  - `list_multivariate_model`
  - `train_multivariate_model`
  - `detect_anomaly`
  - `get_detection_result`
  - `get_multivariate_model`
  - `export_model`
  - `delete_multivariate_model`
  - `last_detect_anomaly`
- Refer to the [CHANGELOG.md](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/anomalydetector/azure-ai-anomalydetector/CHANGELOG.md) for more new features, changes, and bug fixes.

## Important changes

### Anomaly Detection for Entire Series in Batch

The `detect_univariate_entire_series` method has replaced `entire_detect` on the AnomalyDetectorClient.
 - The `options` parameter has replaced `body`. The `options` parameter takes type `models.UnivariateDetectionOptions`, `IO`, or `JSON`.
 - `models.UnivariateDetectionOptions` has replaced `models.Request` and has the additional attributes `impute_mode` and `impute_fixed_value`.
 - `content_type` optional parameter, the Content-Type of the `options` parameter, has been added.
 - Optional parameter `raw` has been removed and `cls` of `Type[models.UnivariateEntireDetectionResults]` can be passed in to return the deserialized response as a `models.UnivariateEntireDetectionResults` object.
 - The `custom_headers` optional parameter has been replaced by `headers`.
 - `operation_config` is now `kwargs`.

### Anomaly Detection Status of Latest Point in Time Series

The `detect_univariate_last_point` method has replaced `last_detect` on the AnomalyDetectorClient.
 - The `options` parameter has replaced `body`. The `options` parameter takes type `models.UnivariateDetectionOptions`, `IO`, or `JSON`.
 - `models.UnivariateDetectionOptions` has replaced `models.Request` and has the additional attributes `impute_mode` and `impute_fixed_value`.
 - `content_type` optional parameter, the Content-Type of the `options` parameter, has been added.
 - Optional parameter `raw` has been removed and `cls` of `Type[models.UnivariateLastDetectionResults]` can be passed in to return the deserialized response as a `models.UnivariateLastDetectionResults` object.
 - The `custom_headers` optional parameter has been replaced by `headers`.
 - `operation_config` is now `kwargs`.

### Change Point Detection for Entire Series

The `detect_univariate_change_point` method has replaced `change_point_detect` on the AnomalyDetectorClient.
 - The `options` parameter has replaced `body`. The `options` parameter takes type `models.UnivariateChangePointDetectionOptions`, `IO`, or `JSON`.
 - `models.UnivariateChangePointDetectionOptions` has replaced `models.ChangePointDetectRequest`.
 - `content_type` optional parameter, the Content-Type of the `options` parameter, has been added.
 - Optional parameter `raw` has been removed and `cls` of `Type[models.UnivariateChangePointDetectionResults]` can be passed in to return the deserialized response as a `models.UnivariateChangePointDetectionResults` object.
 - The `custom_headers` optional parameter has been replaced by `headers`.
 - `operation_config` is now `kwargs`.

## Samples

Usage examples can be found at [Samples for azure-ai-anomalydetector](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/anomalydetector/azure-ai-anomalydetector/samples).
