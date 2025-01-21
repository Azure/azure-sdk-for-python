# Release History

## 1.0.0b2 (2024-10-23)

### Features Added

- Added support for the Large Face List and Large Person Group:
  - Added operation groups `LargeFaceListOperations` and `LargePersonGroupOperations` to `FaceAdministrationClient`.
  - Added operations `find_similar_from_large_face_list`, `identify_from_large_person_group` and `verify_from_large_person_group` to `FaceClient`.
  - Added models for supporting Large Face List and Large Person Group.
- Added support for latest Detect Liveness Session API:
  - Added operations `get_session_image` and `detect_from_session_image` to `FaceSessionClient`.
  - Added properties `enable_session_image` and `liveness_single_modal_model` to model `CreateLivenessSessionContent`.
  - Added model `CreateLivenessWithVerifySessionContent`.

### Breaking Changes

- Changed the parameter of `create_liveness_with_verify_session` from model `CreateLivenessSessionContent` to `CreateLivenessWithVerifySessionContent`.
- Changed the enum value of `FaceDetectionModel`, `FaceRecognitionModel`, `LivenessModel` and `Versions`.

### Other Changes

- Change the default service API version to `v1.2-preview.1`.

## 1.0.0b1 (2024-05-28)

This is the first preview of the `azure-ai-vision-face` client library that follows the [Azure Python SDK Design Guidelines](https://azure.github.io/azure-sdk/python_design.html).
This library replaces the package [azure-cognitiveservices-vision-face](https://pypi.org/project/azure-cognitiveservices-vision-face/).

This package's [documentation](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/face/azure-ai-vision-face/) and [samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/face/azure-ai-vision-face/samples) demonstrate the new API.

### Features Added

- Added support for Liveness detection.
- Asynchronous APIs are added under `azure.ai.vision.face.aio` namespace.
- Authentication with Microsoft Entra ID is supported using `DefaultAzureCredential()` from `azure.identity`.

### Breaking Changes

- This library only supports the API of the the operation groups below of [Azure AI Face v1.1-preview.1](https://learn.microsoft.com/rest/api/face/operation-groups?view=rest-face-v1.1-preview.1):
  - Face Detection Operations
  - Face Recognition Operations: only `Find Similiar`, `Group` and `Verify Face To Face`.
  - Liveness Session Operations
- The namespace/package name for Azure AI Face has changed from `azure.cognitiveservices.vision.face` to `azure.ai.vision.face`.
- Two client design:
  - `FaceClient` to perform core Face functions such as face detection, verification, finding similar faces and grouping faces.
  - `FaceSessionClient` to interact with sessions which is used for Liveness detection.
- New function names that comply with [Azure Python SDK Design Guidelines](https://azure.github.io/azure-sdk/python_design.html):
  - For example, the method `person_group_person.create()` is changed to `create_person_group_person()`.
- The Snapshot operations are all removed as [the Snapshot API is no longer supported](https://azure.microsoft.com/updates/facelimitedaccess/).
