---
page_type: sample
languages:
  - python
products:
  - azure-ai-vision-face
urlFragment: face-samples
---

# Azure Face client library for Python Samples

These are code samples that show common scenario operations with the Azure Face client library.
The async versions of the samples (the python sample files appended with `_async`) show asynchronous operations.

Several Azure Face Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Face:

* [samples_authentication.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/face/azure-ai-vision-face/samples/samples_authentication.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/face/azure-ai-vision-face/samples/async_samples/samples_authentication_async.py)) - Examples for authenticating and creating the client:
    * From a key
    * From Microsoft Entra ID

* [samples_face_liveness_detection.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/face/azure-ai-vision-face/samples/samples_face_liveness_detection.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/face/azure-ai-vision-face/samples/async_samples/samples_face_liveness_detection_async.py)) - Examples for performing liveness detection

* [samples_face_liveness_detection_with_verification.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/face/azure-ai-vision-face/samples/samples_face_liveness_detection_with_verification.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/face/azure-ai-vision-face/samples/async_samples/samples_face_liveness_detection_with_verification_async.py)) - Examples for performing liveness detection with face verification

* [samples_face_detection.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/face/azure-ai-vision-face/samples/samples_face_detection.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/face/azure-ai-vision-face/samples/async_samples/samples_face_detection_async.py)) - Examples for detecting human faces in an image:
    * From a binary data
    * From a URL

* [samples_face_grouping.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/face/azure-ai-vision-face/samples/samples_face_grouping.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/face/azure-ai-vision-face/samples/async_samples/samples_face_grouping_async.py)) - Examples for dividing candidate faces into groups based on face similarity.

* [samples_find_similar_faces.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/face/azure-ai-vision-face/samples/samples_find_similar_faces.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/face/azure-ai-vision-face/samples/async_samples/samples_find_similar_faces_async.py)) - Examples for searching the similar-looking faces from a set of candidate faces:
    * From a faceId array
    * From a large face list

## Prerequisites
* Python 3.8 or later is required to use this package
* You must have an [Azure subscription](https://azure.microsoft.com/free/) and an [Face APIs account](https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/overview-identity)
to run these samples.

## Setup

1. Install the Face client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-ai-vision-face
```

2. Clone or download this sample repository
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python samples_face_detection.py`

## Next steps

Check out the [API reference documentation](https://aka.ms/azsdk-python-face-ref) to learn more about what you can do
with the Azure Face client library.
