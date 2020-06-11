# Azure Cognitive Services Computer Vision SDK for Python

The Computer Vision service provides developers with access to advanced algorithms for processing images and returning information. Computer Vision algorithms analyze the content of an image in different ways, depending on the visual features you're interested in.

You can use Computer Vision in your application to:

- Analyze images for insight
- Extract text from images
- Generate thumbnails

Looking for more documentation?

* [SDK reference documentation](https://docs.microsoft.com/python/api/azure-cognitiveservices-vision-computervision/azure.cognitiveservices.vision.computervision)
* [Cognitive Services Computer Vision documentation](https://docs.microsoft.com/azure/cognitive-services/computer-vision/)

## Prerequisites

* Azure subscription - [Create a free account][azure_sub]
* Azure [Computer Vision resource][computervision_resource]
* [Python 3.6+][python]

If you need a Computer Vision API account, you can create one with this [Azure CLI][azure_cli] command:

```Bash
RES_REGION=westeurope
RES_GROUP=<resourcegroup-name>
ACCT_NAME=<computervision-account-name>

az cognitiveservices account create \
    --resource-group $RES_GROUP \
    --name $ACCT_NAME \
    --location $RES_REGION \
    --kind ComputerVision \
    --sku S1 \
    --yes
```

## Installation

Install the Azure Cognitive Services Computer Vision SDK with [pip][pip], optionally within a [virtual environment][venv].

### Configure a virtual environment (optional)

Although not required, you can keep your base system and Azure SDK environments isolated from one another if you use a [virtual environment][virtualenv]. Execute the following commands to configure and then enter a virtual environment with [venv][venv], such as `cogsrv-vision-env`:

```Bash
python3 -m venv cogsrv-vision-env
source cogsrv-vision-env/bin/activate
```

### Install the SDK

Install the Azure Cognitive Services Computer Vision SDK for Python [package][pypi_computervision] with [pip][pip]:

```Bash
pip install azure-cognitiveservices-vision-computervision
```

## Authentication

Once you create your Computer Vision resource, you need its **region**, and one of its **account keys** to instantiate the client object.

Use these values when you create the instance of the [ComputerVisionClient][ref_computervisionclient] client object.

### Get credentials

Use the [Azure CLI][cloud_shell] snippet below to populate two environment variables with the Computer Vision account **region** and one of its **keys** (you can also find these values in the [Azure portal][azure_portal]). The snippet is formatted for the Bash shell.

```Bash
RES_GROUP=<resourcegroup-name>
ACCT_NAME=<computervision-account-name>

export ACCOUNT_REGION=$(az cognitiveservices account show \
    --resource-group $RES_GROUP \
    --name $ACCT_NAME \
    --query location \
    --output tsv)

export ACCOUNT_KEY=$(az cognitiveservices account keys list \
    --resource-group $RES_GROUP \
    --name $ACCT_NAME \
    --query key1 \
    --output tsv)
```

### Create client

Once you've populated the `ACCOUNT_REGION` and `ACCOUNT_KEY` environment variables, you can create the [ComputerVisionClient][ref_computervisionclient] client object.

```Python
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

import os
region = os.environ['ACCOUNT_REGION']
key = os.environ['ACCOUNT_KEY']

credentials = CognitiveServicesCredentials(key)
client = ComputerVisionClient(
    endpoint="https://" + region + ".api.cognitive.microsoft.com/",
    credentials=credentials
)
```

## Usage

Once you've initialized a [ComputerVisionClient][ref_computervisionclient] client object, you can:

* Analyze an image: You can analyze an image for certain features such as faces, colors, tags.
* Generate thumbnails: Create a custom JPEG image to use as a thumbnail of the original image.
* Get description of an image: Get a description of the image based on its subject domain.

For more information about this service, see [What is Computer Vision?][computervision_docs].

## Examples

The following sections provide several code snippets covering some of the most common Computer Vision tasks, including:

* [Analyze an image](#analyze-an-image)
* [Get subject domain list](#get-subject-domain-list)
* [Analyze an image by domain](#analyze-an-image-by-domain)
* [Get text description of an image](#get-text-description-of-an-image)
* [Get handwritten text from image](#get-text-from-image)
* [Generate thumbnail](#generate-thumbnail)

### Analyze an image

You can analyze an image for certain features with [`analyze_image`][ref_computervisionclient_analyze_image]. Use the [`visual_features`][ref_computervision_model_visualfeatures] property to set the types of analysis to perform on the image. Common values are `VisualFeatureTypes.tags` and `VisualFeatureTypes.description`.

```Python
url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Broadway_and_Times_Square_by_night.jpg/450px-Broadway_and_Times_Square_by_night.jpg"

image_analysis = client.analyze_image(url,visual_features=[VisualFeatureTypes.tags])

for tag in image_analysis.tags:
    print(tag)
```

### Get subject domain list

Review the subject domains used to analyze your image with [`list_models`][ref_computervisionclient_list_models]. These domain names are used when [analyzing an image by domain](#analyze-an-image-by-domain). An example of a domain is `landmarks`.

```Python
models = client.list_models()

for x in models.models_property:
    print(x)
```

### Analyze an image by domain

You can analyze an image by subject domain with [`analyze_image_by_domain`][ref_computervisionclient_analyze_image_by_domain]. Get the [list of supported subject domains](#get-subject-domain-list) in order to use the correct domain name.

```Python
domain = "landmarks"
url = "https://images.pexels.com/photos/338515/pexels-photo-338515.jpeg"
language = "en"

analysis = client.analyze_image_by_domain(domain, url, language)

for landmark in analysis.result["landmarks"]:
    print(landmark["name"])
    print(landmark["confidence"])
```

### Get text description of an image

You can get a language-based text description of an image with [`describe_image`][ref_computervisionclient_describe_image]. Request several descriptions with the `max_description` property if you are doing text analysis for keywords associated with the image. Examples of a text description for the following image include `a train crossing a bridge over a body of water`, `a large bridge over a body of water`, and `a train crossing a bridge over a large body of water`.

```Python
domain = "landmarks"
url = "http://www.public-domain-photos.com/free-stock-photos-4/travel/san-francisco/golden-gate-bridge-in-san-francisco.jpg"
language = "en"
max_descriptions = 3

analysis = client.describe_image(url, max_descriptions, language)

for caption in analysis.captions:
    print(caption.text)
    print(caption.confidence)
```

### Get text from image

You can get any handwritten or printed text from an image. This requires two calls to the SDK: [`read`][ref_computervisionclient_read] and [`get_read_result`][ref_computervisionclient_get_read_result]. The call to read is asynchronous. In the results of the get_read_result call, you need to check if the first call completed with [`OperationStatusCodes`][ref_computervision_model_operationstatuscodes] before extracting the text data. The results include the text as well as the bounding box coordinates for the text.

```Python
# import models
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes

url = "https://github.com/Azure-Samples/cognitive-services-python-sdk-samples/raw/master/samples/vision/images/make_things_happen.jpg"
raw = True
numberOfCharsInOperationId = 36

# SDK call
rawHttpResponse = client.read(url, language="en", raw=True)

# Get ID from returned headers
operationLocation = rawHttpResponse.headers["Operation-Location"]
idLocation = len(operationLocation) - numberOfCharsInOperationId
operationId = operationLocation[idLocation:]

# SDK call
result = client.get_read_result(operationId)

# Get data
if result.status == OperationStatusCodes.succeeded:

    for line in result.analyze_result.read_results[0].lines:
        print(line.text)
        print(line.bounding_box)
```

### Generate thumbnail

You can generate a thumbnail (JPG) of an image with [`generate_thumbnail`][ref_computervisionclient_generate_thumbnail]. The thumbnail does not need to be in the same proportions as the original image.

This example uses the [Pillow][pypi_pillow] package to save the new thumbnail image locally.

```Python
from PIL import Image
import io

width = 50
height = 50
url = "http://www.public-domain-photos.com/free-stock-photos-4/travel/san-francisco/golden-gate-bridge-in-san-francisco.jpg"

thumbnail = client.generate_thumbnail(width, height, url)

for x in thumbnail:
    image = Image.open(io.BytesIO(x))

image.save('thumbnail.jpg')
```

## Troubleshooting

### General

When you interact with the [ComputerVisionClient][ref_computervisionclient] client object using the Python SDK, the [`ComputerVisionErrorException`][ref_computervision_computervisionerrorexception] class is used to return errors. Errors returned by the service correspond to the same HTTP status codes returned for REST API requests.

For example, if you try to analyze an image with an invalid key, a `401` error is returned. In the following snippet, the [error][ref_httpfailure] is handled gracefully by catching the exception and displaying additional information about the error.

```Python

domain = "landmarks"
url = "http://www.public-domain-photos.com/free-stock-photos-4/travel/san-francisco/golden-gate-bridge-in-san-francisco.jpg"
language = "en"
max_descriptions = 3

try:
    analysis = client.describe_image(url, max_descriptions, language)

    for caption in analysis.captions:
        print(caption.text)
        print(caption.confidence)
except HTTPFailure as e:
    if e.status_code == 401:
        print("Error unauthorized. Make sure your key and region are correct.")
    else:
        raise
```

### Handle transient errors with retries

While working with the [ComputerVisionClient][ref_computervisionclient] client, you might encounter transient failures caused by [rate limits][computervision_request_units] enforced by the service, or other transient problems like network outages. For information about handling these types of failures, see [Retry pattern][azure_pattern_retry] in the Cloud Design Patterns guide, and the related [Circuit Breaker pattern][azure_pattern_circuit_breaker].

## Next steps

### More sample code

Several Computer Vision Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Computer Vision:

* [See sample repo][recognize-text]

### Additional documentation

For more extensive documentation on the Computer Vision service, see the [Azure Computer Vision documentation][computervision_docs] on docs.microsoft.com.

<!-- LINKS -->
[pip]: https://pypi.org/project/pip/
[python]: https://www.python.org/downloads/

[azure_cli]: https://docs.microsoft.com/cli/azure
[azure_pattern_circuit_breaker]: https://docs.microsoft.com/azure/architecture/patterns/circuit-breaker
[azure_pattern_retry]: https://docs.microsoft.com/azure/architecture/patterns/retry
[azure_portal]: https://portal.azure.com
[azure_sub]: https://azure.microsoft.com/free/

[cloud_shell]: https://docs.microsoft.com/azure/cloud-shell/overview

[venv]: https://docs.python.org/3/library/venv.html
[virtualenv]: https://virtualenv.pypa.io

[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-vision-computervision

[pypi_computervision]:https://pypi.org/project/azure-cognitiveservices-vision-computervision/
[pypi_pillow]:https://pypi.org/project/Pillow/

[ref_computervision_sdk]: https://docs.microsoft.com/python/api/azure-cognitiveservices-vision-computervision/azure.cognitiveservices.vision.computervision?view=azure-python
[ref_computervision_computervisionerrorexception]:https://docs.microsoft.com/python/api/azure-cognitiveservices-vision-computervision/azure.cognitiveservices.vision.computervision.models.computervisionerrorexception?view=azure-python
[ref_httpfailure]: https://docs.microsoft.com/python/api/msrest/msrest.exceptions.httpoperationerror?view=azure-python


[computervision_resource]: https://docs.microsoft.com/azure/cognitive-services/computer-vision/vision-api-how-to-topics/howtosubscribe

[computervision_docs]: https://docs.microsoft.com/azure/cognitive-services/computer-vision/home

[ref_computervisionclient]: https://docs.microsoft.com/python/api/azure-cognitiveservices-vision-computervision/azure.cognitiveservices.vision.computervision.computervisionclient?view=azure-python


[ref_computervisionclient_analyze_image]: https://docs.microsoft.com/python/api/azure-cognitiveservices-vision-computervision/azure.cognitiveservices.vision.computervision.computervisionclient?view=azure-python#analyze-image-url--visual-features-none--details-none--language--en---custom-headers-none--raw-false----operation-config-
[ref_computervisionclient_list_models]:https://docs.microsoft.com/python/api/azure-cognitiveservices-vision-computervision/azure.cognitiveservices.vision.computervision.computervisionclient?view=azure-python#list-models-custom-headers-none--raw-false----operation-config-
[ref_computervisionclient_analyze_image_by_domain]:https://docs.microsoft.com/python/api/azure-cognitiveservices-vision-computervision/azure.cognitiveservices.vision.computervision.computervisionclient?view=azure-python#analyze-image-by-domain-model--url--language--en---custom-headers-none--raw-false----operation-config-
[ref_computervisionclient_describe_image]:https://docs.microsoft.com/python/api/azure-cognitiveservices-vision-computervision/azure.cognitiveservices.vision.computervision.computervisionclient?view=azure-python#describe-image-url--max-candidates--1---language--en---custom-headers-none--raw-false----operation-config-
[ref_computervisionclient_read]:https://docs.microsoft.com/python/api/azure-cognitiveservices-vision-computervision/azure.cognitiveservices.vision.computervision.computervisionclient?view=azure-python#read-url--mode--custom-headers-none--raw-false----operation-config-
[ref_computervisionclient_get_read_result]:https://docs.microsoft.com/python/api/azure-cognitiveservices-vision-computervision/azure.cognitiveservices.vision.computervision.computervisionclient?view=azure-python#get-read-result-operation-id--custom-headers-none--raw-false----operation-config-
[ref_computervisionclient_generate_thumbnail]:https://docs.microsoft.com/python/api/azure-cognitiveservices-vision-computervision/azure.cognitiveservices.vision.computervision.computervisionclient?view=azure-python#generate-thumbnail-width--height--url--smart-cropping-false--custom-headers-none--raw-false--callback-none----operation-config-


[ref_computervision_model_visualfeatures]:https://docs.microsoft.com/python/api/azure-cognitiveservices-vision-computervision/azure.cognitiveservices.vision.computervision.models.visualfeaturetypes?view=azure-python

[ref_computervision_model_operationstatuscodes]:https://docs.microsoft.com/python/api/azure-cognitiveservices-vision-computervision/azure.cognitiveservices.vision.computervision.models.operationstatuscodes?view=azure-python

[computervision_request_units]:https://azure.microsoft.com/pricing/details/cognitive-services/computer-vision/

[recognize-text]:https://github.com/Azure-Samples/cognitive-services-python-sdk-samples/blob/master/samples/vision/computer_vision_samples.py