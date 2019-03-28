.. :changelog:

Release History
===============

1.0.0 (2019-03-22)
++++++++++++++++++

This is a stable release of the Cognitive Services Custom Vision SDK.

**Training**

- Added an advanced training option to set a budget to train longer for improved iteration performance.
- Added additional export options targetting Vision AI Dev Kit and Docker ARM for Raspberry Pi.

**Prediction**

- PredictImage and PredictImageUrl have been replaced with project type specific calls.
  ClassifyImage and ClassifyImageUrl for image classification projects.
  DetectImage and DetectImageUrl for object detection projects .
- Prediction methods now take a name to designate which published iteration to use. Iterations can be published using the Custom Vision Training SDK.

0.4.0 (2018-11-13)
++++++++++++++++++

- The API client name was changed from TrainingAPI to CustomVisionTrainingClient, in keeping with other Azure SDKs.
- The way the Azure region is specfied has changed.  Specifically, the AzureRegion property was dropped in favor of an Endpoint property. If you were previously specifying an AzureRegion value, you should now specify Endpoint='https://{AzureRegion}.api.cognitive.microsoft.com' instead. This change ensures better global coverage.
- Added ONNX 1.2 as an export option
- Added negative tag support.

0.3.0 (2018-07-12)
++++++++++++++++++

**Features**

-	Added ability to create Multilabel or Multiclass image classification projects
-	Fixes and improvements to Docker container export and export pipeline to know when a newer version is available

0.2.0 (2018-05-07)
++++++++++++++++++

**Breaking changes**

- Expect many breaking changes. As a preview package, we don't detail, but updated samples are available at:
  https://github.com/Azure-Samples/cognitive-services-python-sdk-samples

**Features**

- Adding support for object detection projects and expanded export functionality for image classification projects
- Client class can be used as a context manager to keep the underlying HTTP session open for performance

**Bugfixes**

- Compatibility of the sdist with wheel 0.31.0

Internal API version moved from 1.2 to 2.0

0.1.0 (2018-04-05)
++++++++++++++++++

* Initial Release
