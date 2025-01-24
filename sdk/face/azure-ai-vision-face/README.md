# Azure AI Face client library for Python

The Azure AI Face service provides AI algorithms that detect, recognize, and analyze human faces in images. It includes the following main features:

- Face detection and analysis
- Liveness detection
- Face recognition
  - Face verification ("one-to-one" matching)
  - Face identification ("one-to-many" matching)
- Find similar faces
- Group faces

[Source code][source_code]
| [Package (PyPI)][face_pypi]
| [API reference documentation][face_ref_docs]
| [Product documentation][face_product_docs]
| [Samples][face_samples]

## Getting started

### Prerequisites

- Python 3.8 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- Your Azure account must have a `Cognitive Services Contributor` role assigned in order for you to agree to the responsible AI terms and create a resource. To get this role assigned to your account, follow the steps in the [Assign roles][azure_role_assignment] documentation, or contact your administrator.
- Once you have sufficient permissions to control your Azure subscription, you need either
  * an [Azure Face account][azure_portal_list_face_account] or
  * an [Azure AI services multi-service account][azure_portal_list_cognitive_service_account]

### Create a Face or an Azure AI services multi-service account

Azure AI Face supports both [multi-service][azure_cognitive_service_account] and single-service access. Create an Azure AI services multi-service account if you plan to access multiple Azure AI services under a single endpoint/key. For Face access only, create a Face resource.

* To create a new Face or Azure AI services multi-service account, you can use [Azure Portal][azure_portal_create_face_account], [Azure PowerShell][quick_start_create_account_via_azure_powershell], or [Azure CLI][quick_start_create_account_via_azure_cli].

### Install the package

```bash
python -m pip install azure-ai-vision-face
```

### Authenticate the client

In order to interact with the Face service, you will need to create an instance of a client.
An **endpoint** and **credential** are necessary to instantiate the client object.

Both key credential and Microsoft Entra ID credential are supported to authenticate the client.
For enhanced security, we strongly recommend utilizing Microsoft Entra ID credential for authentication in the production environment, while AzureKeyCredential should be reserved exclusively for the testing environment.

#### Get the endpoint

You can find the endpoint for your Face resource using the Azure Portal or Azure CLI:

```bash
# Get the endpoint for the Face resource
az cognitiveservices account show --name "resource-name" --resource-group "resource-group-name" --query "properties.endpoint"
```

Either a regional endpoint or a custom subdomain can be used for authentication. They are formatted as follows:

```
Regional endpoint: https://<region>.api.cognitive.microsoft.com/
Custom subdomain: https://<resource-name>.cognitiveservices.azure.com/
```

A regional endpoint is the same for every resource in a region. A complete list of supported regional endpoints can be consulted [here][regional_endpoints]. Please note that regional endpoints do not support Microsoft Entra ID authentication. If you'd like migrate your resource to use custom subdomain, follow the instructions [here][how_to_migrate_resource_to_custom_subdomain].

A custom subdomain, on the other hand, is a name that is unique to the resource. Once created and linked to a resource, it cannot be modified.


#### Create the client with a Microsoft Entra ID credential

`AzureKeyCredential` authentication is used in the examples in this getting started guide, but you can also authenticate with Microsoft Entra ID using the [azure-identity][azure_sdk_python_identity] library.
Note that regional endpoints do not support Microsoft Entra ID authentication. Create a [custom subdomain][custom_subdomain] name for your resource in order to use this type of authentication.

To use the [DefaultAzureCredential][azure_sdk_python_default_azure_credential] type shown below, or other credential types provided with the Azure SDK, please install the `azure-identity` package:

```
pip install azure-identity
```

You will also need to [register a new Microsoft Entra ID application and grant access][register_aad_app] to Face by assigning the `"Cognitive Services User"` role to your service principal.

Once completed, set the values of the client ID, tenant ID, and client secret of the Microsoft Entra ID application as environment variables:
`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`.

```python
"""DefaultAzureCredential will use the values from these environment
variables: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET
"""
from azure.ai.vision.face import FaceClient
from azure.identity import DefaultAzureCredential

endpoint = "https://<my-custom-subdomain>.cognitiveservices.azure.com/"
credential = DefaultAzureCredential()

face_client = FaceClient(endpoint, credential)
```

#### Create the client with AzureKeyCredential

To use an API key as the `credential` parameter, pass the key as a string into an instance of [AzureKeyCredential][azure_sdk_python_azure_key_credential].
You can get the API key for your Face resource using the [Azure Portal][get_key_via_azure_portal] or [Azure CLI][get_key_via_azure_cli]:

```bash
# Get the API keys for the Face resource
az cognitiveservices account keys list --name "<resource-name>" --resource-group "<resource-group-name>"
```

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.vision.face import FaceClient

endpoint = "https://<my-custom-subdomain>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api_key>")
face_client = FaceClient(endpoint, credential)
```


## Key concepts

### FaceClient

`FaceClient` provides operations for:

 - Face detection and analysis: Detect human faces in an image and return the rectangle coordinates of their locations,
   and optionally with landmarks, and face-related attributes. This operation is required as a first step in all the
   other face recognition scenarios.
 - Face recognition: Confirm that a user is who they claim to be based on how closely their face data matches the target face.
   It includes Face verification ("one-to-one" matching).
 - Finding similar faces from a smaller set of faces that look similar to the target face.
 - Grouping faces into several smaller groups based on similarity.

### FaceAdministrationClient

`FaceAdministrationClient` is provided to interact with the following data structures that hold data on faces and
person for Face recognition:

 - `large_face_list`: It is a list of faces which can hold faces and used by [find similar faces][find_similar].
   - It can up to 1,000,000 faces.
   - Training (`begin_train()`) is required before calling `find_similar_from_large_face_list()`.
 - `large_person_group`: It is a container which can hold person objects, and is used by face recognition.
   - It can up to 1,000,000 person objects, with each person capable of holding up to 248 faces. The total person objects in all `large_person_group` should not exceed 1,000,000,000.
   - For [face verification][face_verification], call `verify_from_large_person_group()`.
   - For [face identification][face_identification], training (`begin_train()`) is required before calling `identify_from_large_person_group()`.

### FaceSessionClient

`FaceSessionClient` is provided to interact with sessions which is used for Liveness detection.

 - Create, query, and delete the session.
 - Query the liveness and verification result.
 - Query the audit result.

### Long-running operations

Long-running operations are operations which consist of an initial request sent to the service to start an operation,
followed by polling the service at intervals to determine whether the operation has completed or failed, and if it has
succeeded, to get the result.

Methods that train a group (LargeFaceList or LargePersonGroup) are modeled as long-running operations.
The client exposes a `begin_<method-name>` method that returns an `LROPoller` or `AsyncLROPoller`. Callers should wait
for the operation to complete by calling `result()` on the poller object returned from the `begin_<method-name>` method.
Sample code snippets are provided to illustrate using long-running operations [below](#examples "Examples").

## Examples

The following section provides several code snippets covering some of the most common Face tasks, including:

* [Detecting faces in an image](#face-detection "Face Detection")
* [Identifying the specific face from a LargePersonGroup](#face-recognition-from-largepersongroup "Face Recognition from LargePersonGroup")
* [Determining if a face in an video is real (live) or fake (spoof)](#liveness-detection "Liveness Detection")

### Face Detection
Detect faces and analyze them from an binary data. The latest model is the most accurate and recommended to be used.
For the detailed differences between different versions of **Detection** and **Recognition** model, please refer to the following links.
* [Detection model][evaluate_different_detection_models]
* [Recognition model][recommended_recognition_model]

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.vision.face import FaceClient
from azure.ai.vision.face.models import (
    FaceDetectionModel,
    FaceRecognitionModel,
    FaceAttributeTypeDetection03,
    FaceAttributeTypeRecognition04,
)

endpoint = "<your endpoint>"
key = "<your api key>"

with FaceClient(endpoint=endpoint, credential=AzureKeyCredential(key)) as face_client:
    sample_file_path = "<your image file>"
    with open(sample_file_path, "rb") as fd:
        file_content = fd.read()

    result = face_client.detect(
        file_content,
        detection_model=FaceDetectionModel.DETECTION03,  # The latest detection model.
        recognition_model=FaceRecognitionModel.RECOGNITION04,  # The latest recognition model.
        return_face_id=True,
        return_face_attributes=[
            FaceAttributeTypeDetection03.HEAD_POSE,
            FaceAttributeTypeDetection03.MASK,
            FaceAttributeTypeRecognition04.QUALITY_FOR_RECOGNITION,
        ],
        return_face_landmarks=True,
        return_recognition_model=True,
        face_id_time_to_live=120,
    )

    print(f"Detect faces from the file: {sample_file_path}")
    for idx, face in enumerate(result):
        print(f"----- Detection result: #{idx+1} -----")
        print(f"Face: {face.as_dict()}")
```

### Face Recognition from LargePersonGroup

Identify a face against a defined LargePersonGroup.

First, we have to use `FaceAdministrationClient` to create a `LargePersonGroup`, add a few `Person` to it, and then register faces with these `Person`.

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.vision.face import FaceAdministrationClient, FaceClient
from azure.ai.vision.face.models import FaceDetectionModel, FaceRecognitionModel


def read_file_content(file_path: str):
    with open(file_path, "rb") as fd:
        file_content = fd.read()

    return file_content


endpoint = "<your endpoint>"
key = "<your api key>"

large_person_group_id = "lpg_family"

with FaceAdministrationClient(endpoint=endpoint, credential=AzureKeyCredential(key)) as face_admin_client:
    print(f"Create a large person group with id: {large_person_group_id}")
    face_admin_client.large_person_group.create(
        large_person_group_id, name="My Family", recognition_model=FaceRecognitionModel.RECOGNITION04
    )

    print("Create a Person Bill and add a face to him.")
    bill_person_id = face_admin_client.large_person_group.create_person(
        large_person_group_id, name="Bill", user_data="Dad"
    ).person_id
    bill_image_file_path = "./samples/images/Family1-Dad1.jpg"
    face_admin_client.large_person_group.add_face(
        large_person_group_id,
        bill_person_id,
        read_file_content(bill_image_file_path),
        detection_model=FaceDetectionModel.DETECTION03,
        user_data="Dad-0001",
    )

    print("Create a Person Clare and add a face to her.")
    clare_person_id = face_admin_client.large_person_group.create_person(
        large_person_group_id, name="Clare", user_data="Mom"
    ).person_id
    clare_image_file_path = "./samples/images/Family1-Mom1.jpg"
    face_admin_client.large_person_group.add_face(
        large_person_group_id,
        clare_person_id,
        read_file_content(clare_image_file_path),
        detection_model=FaceDetectionModel.DETECTION03,
        user_data="Mom-0001",
    )
```

Before doing the identification, we need to train the LargePersonGroup first.
```python
    print(f"Start to train the large person group: {large_person_group_id}.")
    poller = face_admin_client.large_person_group.begin_train(large_person_group_id)

    # Wait for the train operation to be completed.
    # If the training status isn't succeed, an exception will be thrown from the poller.
    training_result = poller.result()
```

When the training operation is completed successfully, we can identify the faces in this LargePersonGroup through
`FaceClient`.
```python
with FaceClient(endpoint=endpoint, credential=AzureKeyCredential(key)) as face_client:
    # Detect the face from the target image.
    target_image_file_path = "./samples/images/identification1.jpg"
    detect_result = face_client.detect(
        read_file_content(target_image_file_path),
        detection_model=FaceDetectionModel.DETECTION03,
        recognition_model=FaceRecognitionModel.RECOGNITION04,
        return_face_id=True,
    )
    target_face_ids = list(f.face_id for f in detect_result)

    # Identify the faces in the large person group.
    result = face_client.identify_from_large_person_group(
        face_ids=target_face_ids, large_person_group_id=large_person_group_id
    )
    for idx, r in enumerate(result):
        print(f"----- Identification result: #{idx+1} -----")
        print(f"{r.as_dict()}")
```

Finally, use `FaceAdministrationClient` to remove the large person group if you don't need it anymore.
```python
with FaceAdministrationClient(endpoint=endpoint, credential=AzureKeyCredential(key)) as face_admin_client:
    print(f"Delete the large person group: {large_person_group_id}")
    face_admin_client.large_person_group.delete(large_person_group_id)
```

### Liveness detection
Face Liveness detection can be used to determine if a face in an input video stream is real (live) or fake (spoof).
The goal of liveness detection is to ensure that the system is interacting with a physically present live person at
the time of authentication. The whole process of authentication is called a session.

There are two different components in the authentication: a frontend application and an app server/orchestrator.
Before uploading the video stream, the app server has to create a session, and then the frontend client could upload
the payload with a `session authorization token` to call the liveness detection. The app server can query for the
liveness detection result and audit logs anytime until the session is deleted.

The Liveness detection operation can not only confirm if the input is live or spoof, but also verify whether the input
belongs to the expected person's face, which is called **liveness detection with face verification**. For the detail
information, please refer to the [tutorial][liveness_tutorial].

This package is only responsible for app server to create, query, delete a session and get audit logs. For how to
integrate the UI and the code into your native frontend application, please follow instructions in the [tutorial][liveness_tutorial].

Here is an example to create and get the liveness detection result of a session.
```python
import uuid

from azure.core.credentials import AzureKeyCredential
from azure.ai.vision.face import FaceSessionClient
from azure.ai.vision.face.models import CreateLivenessSessionContent, LivenessOperationMode

endpoint = "<your endpoint>"
key = "<your api key>"

with FaceSessionClient(endpoint=endpoint, credential=AzureKeyCredential(key)) as face_session_client:
    # Create a session.
    print("Create a new liveness session.")
    created_session = face_session_client.create_liveness_session(
        CreateLivenessSessionContent(
            liveness_operation_mode=LivenessOperationMode.PASSIVE,
            device_correlation_id=str(uuid.uuid4()),
            send_results_to_client=False,
            auth_token_time_to_live_in_seconds=60,
        )
    )
    print(f"Result: {created_session}")

    # Get the liveness detection result.
    print("Get the liveness detection result.")
    liveness_result = face_session_client.get_liveness_session_result(created_session.session_id)
    print(f"Result: {liveness_result}")
```

Here is another example for the liveness detection with face verification.
```python
import uuid

from azure.core.credentials import AzureKeyCredential
from azure.ai.vision.face import FaceSessionClient
from azure.ai.vision.face.models import CreateLivenessSessionContent, LivenessOperationMode

endpoint = "<your endpoint>"
key = "<your api key>"

with FaceSessionClient(endpoint=endpoint, credential=AzureKeyCredential(key)) as face_session_client:
    sample_file_path = "<your verify image file>"
    with open(sample_file_path, "rb") as fd:
        file_content = fd.read()

    # Create a session.
    print("Create a new liveness with verify session with verify image.")

    created_session = face_session_client.create_liveness_with_verify_session(
        CreateLivenessSessionContent(
            liveness_operation_mode=LivenessOperationMode.PASSIVE,
            device_correlation_id=str(uuid.uuid4()),
            send_results_to_client=False,
            auth_token_time_to_live_in_seconds=60,
        ),
        verify_image=file_content,
    )
    print(f"Result: {created_session}")

    # Get the liveness detection and verification result.
    print("Get the liveness detection and verification result.")
    liveness_result = face_session_client.get_liveness_with_verify_session_result(created_session.session_id)
    print(f"Result: {liveness_result}")
```

## Troubleshooting

### General

Face client library will raise exceptions defined in [Azure Core][python_azure_core_exceptions].
Error codes and messages raised by the Face service can be found in the [service documentation][face_errors].

### Logging

This library uses the standard [logging][python_logging] library for logging.

Basic information about HTTP sessions (URLs, headers, etc.) is logged at `INFO` level.

Detailed `DEBUG` level logging, including request/response bodies and **unredacted**
headers, can be enabled on the client or per-operation with the `logging_enable` keyword argument.

See full SDK logging documentation with examples [here][sdk_logging_docs].

```python
import sys
import logging

from azure.ai.vision.face import FaceClient
from azure.core.credentials import AzureKeyCredential

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    stream=sys.stdout)

endpoint = "https://<my-custom-subdomain>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api_key>")
face_client = FaceClient(endpoint, credential)

face.detect(..., logging_enable=True)
```

### Optional Configuration

Optional keyword arguments can be passed in at the client and per-operation level.
The azure-core [reference documentation][azure_core_ref_docs] describes available configurations for retries, logging, transport protocols, and more.

## Next steps

### More sample code

See the [Sample README][face_samples] for several code snippets illustrating common patterns used in the Face Python API.

### Additional documentation

For more extensive documentation on Azure AI Face, see the [Face documentation][face_product_docs] on learn.microsoft.com.

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact opencode@microsoft.com with any
additional questions or comments.

<!-- LINKS -->
[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/face/azure-ai-vision-face/azure/ai/vision/face
[face_pypi]: https://aka.ms/azsdk-python-face-pkg
[face_ref_docs]: https://aka.ms/azsdk-python-face-ref
[face_product_docs]: https://learn.microsoft.com/azure/ai-services/computer-vision/overview-identity
[face_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/face/azure-ai-vision-face/samples

[azure_sub]: https://azure.microsoft.com/free/
[azure_role_assignment]: https://learn.microsoft.com/azure/role-based-access-control/role-assignments-steps
[azure_portal_list_face_account]: https://portal.azure.com/#blade/Microsoft_Azure_ProjectOxford/CognitiveServicesHub/Face
[azure_portal_list_cognitive_service_account]: https://portal.azure.com/#view/Microsoft_Azure_ProjectOxford/CognitiveServicesHub/~/AllInOne
[azure_cognitive_service_account]: https://learn.microsoft.com/azure/ai-services/multi-service-resource?tabs=windows&pivots=azportal#supported-services-with-a-multi-service-resource
[azure_portal_create_face_account]: https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesFace
[quick_start_create_account_via_azure_cli]: https://learn.microsoft.com/azure/ai-services/multi-service-resource?tabs=windows&pivots=azcli
[quick_start_create_account_via_azure_powershell]: https://learn.microsoft.com/azure/ai-services/multi-service-resource?tabs=windows&pivots=azpowershell

[get_key_via_azure_portal]: https://learn.microsoft.com/azure/ai-services/multi-service-resource?tabs=windows&pivots=azportal#get-the-keys-for-your-resource
[get_key_via_azure_cli]: https://learn.microsoft.com/azure/ai-services/multi-service-resource?tabs=windows&pivots=azcli#get-the-keys-for-your-resource
[regional_endpoints]: https://azure.microsoft.com/global-infrastructure/services/?products=cognitive-services
[how_to_migrate_resource_to_custom_subdomain]: https://learn.microsoft.com/azure/ai-services/cognitive-services-custom-subdomains#how-does-this-impact-existing-resources
[azure_sdk_python_azure_key_credential]: https://aka.ms/azsdk/python/core/azurekeycredential
[azure_sdk_python_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
[custom_subdomain]: https://learn.microsoft.com/azure/cognitive-services/authentication#create-a-resource-with-a-custom-subdomain
[azure_sdk_python_default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[register_aad_app]: https://learn.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal

[face_verification]: https://learn.microsoft.com/azure/ai-services/computer-vision/overview-identity#verification
[face_identification]: https://learn.microsoft.com/azure/ai-services/computer-vision/overview-identity#identification
[find_similar]: https://learn.microsoft.com/azure/ai-services/computer-vision/overview-identity#find-similar-faces
[use_person_directory_structure]: https://learn.microsoft.com/azure/ai-services/computer-vision/how-to/use-persondirectory

[evaluate_different_detection_models]: https://learn.microsoft.com/azure/ai-services/computer-vision/how-to/specify-detection-model#evaluate-different-models
[recommended_recognition_model]: https://learn.microsoft.com/azure/ai-services/computer-vision/how-to/specify-recognition-model#recommended-model
[liveness_tutorial]: https://learn.microsoft.com/azure/ai-services/computer-vision/tutorials/liveness

[python_azure_core_exceptions]: https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions
[face_errors]: https://aka.ms/face-error-codes-and-messages
[python_logging]: https://docs.python.org/3/library/logging.html
[sdk_logging_docs]: https://learn.microsoft.com/azure/developer/python/sdk/azure-sdk-logging
[azure_core_ref_docs]: https://aka.ms/azsdk/python/core/docs

[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[authenticate_with_token]: https://learn.microsoft.com/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-an-authentication-token
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[pip]: https://pypi.org/project/pip/
