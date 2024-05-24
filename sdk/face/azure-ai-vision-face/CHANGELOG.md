# Release History

## 1.0.0b1 (Unreleased)

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
