# Release History

## 3.1.0 (2020-11-10)

*Training 3.4-preview*

**Features**

  - Support for `3.4-preview` API version.

## 3.0.0 (2020-06-22)

*Training 3.3*

**Features**

  - Model ImageUrlCreateBatch has a new parameter metadata
  - Model ImageIdCreateBatch has a new parameter metadata
  - Model Prediction has a new parameter tag_type
  - Model ImageFileCreateBatch has a new parameter metadata
  - Model Image has a new parameter metadata
  - Added operation get_images
  - Added operation update_image_metadata
  - Added operation get_artifact
  - Added operation get_image_count

**Breaking changes**

  - Operation import_project has a new signature
  - Operation publish_iteration has a new signature
  - Operation create_images_from_files has a new signature
  - Operation create_images_from_urls has a new signature
  - Operation create_images_from_predictions has a new signature

*Prediction 3.1*

**Features**

  - Model Prediction has a new parameter tag_type

## 2.0.0 (2020-05-14)

**Features**

  - Model Iteration has a new parameter training_time_in_minutes
  - Model ProjectSettings has a new parameter image_processing_settings
  - Model ProjectSettings has a new parameter detection_parameters
  - Model ProjectSettings has a new parameter use_negative_set
  - Model Project has a new parameter status
  - Added operation CustomVisionPredictionClientOperationsMixin.detect_image_with_no_store
  - Added operation CustomVisionPredictionClientOperationsMixin.detect_image_url
  - Added operation CustomVisionPredictionClientOperationsMixin.classify_image_url
  - Added operation CustomVisionPredictionClientOperationsMixin.detect_image_url_with_no_store
  - Added operation CustomVisionPredictionClientOperationsMixin.classify_image_url_with_no_store
  - Added operation CustomVisionPredictionClientOperationsMixin.classify_image_with_no_store
  - Added operation CustomVisionPredictionClientOperationsMixin.classify_image
  - Added operation CustomVisionPredictionClientOperationsMixin.detect_image
  - Added operation group CustomVisionTrainingClientOperationsMixin

**Breaking changes**

- Credentials are now longer a simple string, but a `msrest.authentication.ApiKeyCredentials` instance instead

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if from some import. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - CustomVisionPredictionClient cannot be imported from `azure.cognitiveservices.vision.customvision.prediction.custom_vision_prediction_client`
    anymore (import from `azure.cognitiveservices.vision.customvision.prediction` works like before)
  - CustomVisionPredictionClientConfiguration import has been moved from
    `azure.cognitiveservices.vision.customvision.prediction.custom_vision_prediction_client` to `azure.cognitiveservices.vision.customvision.prediction`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.cognitiveservices.vision.customvision.prediction.models.my_class` (import from
    `azure.cognitiveservices.vision.customvision.prediction.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.cognitiveservices.vision.customvision.operations.prediction.my_class_operations` (import
    from `azure.cognitiveservices.vision.customvision.prediction.operations` works like before)
  - CustomVisionTrainingClient cannot be imported from `azure.cognitiveservices.vision.customvision.training.custom_vision_training_client`
    anymore (import from `azure.cognitiveservices.vision.customvision.training` works like before)
  - CustomVisionTrainingClientConfiguration import has been moved from
    `azure.cognitiveservices.vision.customvision.training.custom_vision_training_client` to `azure.cognitiveservices.vision.customvision.training`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.cognitiveservices.vision.customvision.training.models.my_class` (import from
    `azure.cognitiveservices.vision.customvision.training.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.cognitiveservices.vision.customvision.operations.training.my_class_operations` (import
    from `azure.cognitiveservices.vision.customvision.training.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 1.0.0 (2019-03-22)

This is a stable release of the Cognitive Services Custom Vision SDK.

**Training**

  - Added an advanced training option to set a budget to train longer
    for improved iteration performance.
  - Added additional export options targetting Vision AI Dev Kit and
    Docker ARM for Raspberry Pi.

**Prediction**

  - PredictImage and PredictImageUrl have been replaced with project
    type specific calls. ClassifyImage and ClassifyImageUrl for image
    classification projects. DetectImage and DetectImageUrl for object
    detection projects .
  - Prediction methods now take a name to designate which published
    iteration to use. Iterations can be published using the Custom
    Vision Training SDK.

## 0.4.0 (2018-11-13)

  - The API client name was changed from TrainingAPI to
    CustomVisionTrainingClient, in keeping with other Azure SDKs.
  - The way the Azure region is specfied has changed. Specifically, the
    AzureRegion property was dropped in favor of an Endpoint property.
    If you were previously specifying an AzureRegion value, you should
    now specify
    Endpoint=`https://{AzureRegion}.api.cognitive.microsoft.com`
    instead. This change ensures better global coverage.
  - Added ONNX 1.2 as an export option
  - Added negative tag support.

## 0.3.0 (2018-07-12)

**Features**

  - Added ability to create Multilabel or Multiclass image
    classification projects
  - Fixes and improvements to Docker container export and export
    pipeline to know when a newer version is available

## 0.2.0 (2018-05-07)

**Breaking changes**

  - Expect many breaking changes. As a preview package, we don't detail,
    but updated samples are available at:[cognitive-services-python-sdk-samples](https://github.com/Azure-Samples/cognitive-services-python-sdk-samples)

**Features**

  - Adding support for object detection projects and expanded export
    functionality for image classification projects
  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

**Bugfixes**

  - Compatibility of the sdist with wheel 0.31.0

Internal API version moved from 1.2 to 2.0

## 0.1.0 (2018-04-05)

  - Initial Release
