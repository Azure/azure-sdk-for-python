# Release History

## 1.0.0b1 (2024-05-21)

This is the first preview of the `azure-ai-vsion-face` client library that follows the [Azure Python SDK Design Guidelines](https://azure.github.io/azure-sdk/python_design.html).
This library replaces the package [azure-cognitiveservices-vision-face](https://pypi.org/project/azure-cognitiveservices-vision-face/).

This package's [documentation](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/face/azure-ai-vision-face/) and [samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/face/azure-ai-vision-face/samples) demonstrate the new API.

**Breaking changes: New API design**

- This library supports only the Azure AI Face v1.1-preview.1 API.
- The namespace/package name for Azure AI Face has changed from `azure.cognitiveservices.vision.face` to `azure.ai.vision.face`.
- Three client design:
  - `FaceClient` to perform core Face functions such as face detection, recognition(identification and verification),
    finding similar faces and grouping faces.
  - `FaceAdministrationClient` to managed the following data structures that hold data on faces and persons for
    Face recognition, like `face_list`, `large_face_list`, `person_group`, `large_person_group`, `person` and
	`dynamic_person_group`.
  - `FaceSessionClient` to interact with sessions which is used for Liveness detection.
- Asynchronous APIs added under `azure.ai.vision.face.aio` namespace
- New function names that comply with [Azure Python SDK Design Guidelines](https://azure.github.io/azure-sdk/python_design.html):
  - For example, the method `person_group_person.create()` is changed to `create_person_group_person()`
- Authentication with API key supported using `AzureKeyCredential("<api_key>")` from `azure.core.credentials`
