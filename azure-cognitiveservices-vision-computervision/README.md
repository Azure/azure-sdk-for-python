# Azure Cognitive Services Computer Vision SDK for Python

The cloud-based Computer Vision service provides developers with access to advanced algorithms for processing images and returning information. This service works with popular image formats, such as JPEG and PNG. 

To analyze an image, you can either upload an image or specify an image URL. Computer Vision algorithms analyze the content of an image in different ways, depending on the visual features you're interested in. For example, Computer Vision can determine if an image contains adult or racy content, or find all the faces in an image.

You can use Computer Vision in your application to:

- Analyze images for insight
- Extract text from images
- Generate thumbnails

Looking for source code or API reference?

* [SDK source code][source_code]
* [SDK reference documentation][ref_computervision_sdk]

## Prerequisites

* Azure subscription - [Create a free account][azure_sub]
* Azure [Computer Vision resource][computer_vision_resource] - SQL API
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

Although not required, you can keep your base system and Azure SDK environments isolated from one another if you use a virtual environment. Execute the following commands to configure and then enter a virtual environment with [venv][venv], such as `cogsrv-vision-env`:

```Bash
python3 -m venv cogsrv-vision-env
source cogsrv-vision-env/bin/activate
```

### Install the SDK

Install the Azure Cognitive Services Computer Vision SDK for Python with [pip][pip]:

```Bash
pip install azure-cognitiveservices-vision-computervision
```

## Authentication

Once you create your Computer Vision resource, you need its **region**, and one of its **account keys** to instantiate the client object.

Use these values when you create the instance of the [ComputerVisionAPI][ref_computervisionclient]. 

### Get credentials

Use the Azure CLI snippet below to populate two environment variables with the Computer Vision account URI and one of its key (you can also find these values in the Azure portal). The snippet is formatted for the Bash shell.

```Bash
RES_GROUP=<resourcegroup-name>
ACCT_NAME=<computervision-account-name>

export ACCOUNT_REGION=$(az cognitiveservices account show \
    --resource-group $RES_GROUP \
    --name $ACCT_NAME \
    --query location \
    --output tsv)

export ACCOUNT_KEY=$(az cognitiveservices account keys list \
    --name $ACCT_NAME \
    --resource-group $RES_GROUP \
    --name $ACCT_NAME \
    --query key1 \
    --output tsv)
```

### Create client

Once you've populated the `ACCOUNT_REGION` and `ACCOUNT_KEY` environment variables, you can create the [ComputerVisionAPI][ref_computervisionclient] client.

```Python
from azure.cognitiveservices.vision.computervision import ComputerVisionAPI
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

import os
region = os.environ['ACCOUNT_REGION']
key = os.environ['ACCOUNT_KEY']

credentials = CognitiveServicesCredentials(key)
client = ComputerVisionAPI(region, credentials)
```

## Usage

Once you've initialized a [ComputerVisionAPI][ref_computervisionclient] client, you can:

* Analyze an image: You can analyze an iimage for certain features such as faces, colors, tags.   
* Moderate images in content: An image can be analyzed for adult content.
* Extract text from an image: An image can be scanned for text. In order to complete the analysis, Computer Vision may correct rotation before analysis. Computer Vision supports 25 languages, and automatically detects the language of extracted text.

For more information about these resources, see [Working with Azure computer vision][computervision_resources].

## Examples

The following sections provide several code snippets covering some of the most common Computer Vision tasks, including:

* [Analyze an image](#analyze-an-image)
* [Analyze an image by domain](#analyze-an-image-by-domain)
* [Get text description of an image](#get-text-description-of-an-image)
* [Generate thumbnail](#generate-thumbnail)
* [Get subject domain list](#get-subject-domain-list)

### Analyze an image

You can analyze an image for certain features. Use the `visual_features` property to set the types of analysis to perform on the image. Common values are: 

    * VisualFeatureTypes.tags
    * VisualFeatureTypes.description

```Python
url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Broadway_and_Times_Square_by_night.jpg/450px-Broadway_and_Times_Square_by_night.jpg"

image_analysis = client.analyze_image(url,visual_features=[VisualFeatureTypes.tags])

for tag in image_analysis.tags:
    print(tag)
```


### Analyze an image by domain

You can analyze an image by subject domain. Get the [list of support subject domains](#get-subject-domain-list) in order to use the correct domain name.  

```Python
domain = "landmarks"
url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Broadway_and_Times_Square_by_night.jpg/450px-Broadway_and_Times_Square_by_night.jpg"
language = "en"

analysis = client.analyze_image_by_domain(domain, url, language)

for landmark in analysis.result["landmarks"]:
    print(landmark["name"])
    print(landmark["confidence"])
```

### Get text description of an image

You can get a language-based text description of an image. Request several descriptions with the `max_description` property if you are doing text analysis for keywords associated with the image. Examples of a text description for the following image include:

    * a train crossing a bridge over a body of water
    * a large bridge over a body of water
    * a train crossing a bridge over a large body of water

```Python
domain = "landmarks"
url = "http://www.public-domain-photos.com/free-stock-photos-4/travel/san-francisco/golden-gate-bridge-in-san-francisco.jpg"
language = "en"
max_descriptions=3

analysis = client.describe_image(url, max_descriptions, language)

for caption in analysis.captions:
    print(caption.text)
    print(caption.confidence)
```

### Generate thumbnail

You can generate a thumbnail (JPG) of an image. The thumbnail does not need to be in the same proportions as the original image. 

```Python
from PIL import Image
import io

width=50
height=50
url = "http://www.public-domain-photos.com/free-stock-photos-4/travel/san-francisco/golden-gate-bridge-in-san-francisco.jpg"

thumbnail = client.generate_thumbnail(width, height, url)

for x in thumbnail:
    image = Image.open(io.BytesIO(x))
image.save('thumbnail.jpg')
```

### Get subject domain list

Review the subject domains used to analyze your image. These domain names are used when [analyzing an image by domain](#analyze-an-image-by-domain). An example of a domain is `landmarks`.

```Python
models = client.list_models()

for x in models.models_property:
    print(x)
```


## Troubleshooting

### General

When you interact with the [ComputerVisionAPI][ref_computervisionclient] client using the Python SDK, errors returned by the service correspond to the same HTTP status codes returned for REST API requests:

[HTTP Status Codes for Azure ComputerVisionAPI][computervision_http_status_codes]

For example, if you try to analyze an image with an invalid key, a `401` error is returned. In the following snippet, the error is handled gracefully by catching the exception and displaying additional information about the error.

```Python

domain = "landmarks"
url = "http://www.public-domain-photos.com/free-stock-photos-4/travel/san-francisco/golden-gate-bridge-in-san-francisco.jpg"
language = "en"
max_descriptions=3

try:
    analysis = client.describe_image(url, max_descriptions, language)

    for caption in analysis.captions:
        print(caption.text)
        print(caption.confidence)
except HTTPFailure as e:
    if e.status_code == 401:
        print("""Error unauthorized.
HTTP status code 401: your Computer Vision account is not authorized. Make sure your key and region are correct.""")
    else:
        raise
```

### Handle transient errors with retries

While working with the [ComputerVisionAPI][ref_computervisionclient] client , you might encounter transient failures caused by [rate limits][computervision_request_units] enforced by the service, or other transient problems like network outages. For information about handling these types of failures, see [Retry pattern][azure_pattern_retry] in the Cloud Design Patterns guide, and the related [Circuit Breaker pattern][azure_pattern_circuit_breaker].

## Next steps

### More sample code

Several Computer Vision Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Computer Vision:

* [`examples.py`][sample_examples_misc] - Contains the code snippets found in this article.


### Additional documentation

For more extensive documentation on the computervision DB service, see the [Azure computervision DB documentation][computervision_docs] on docs.microsoft.com.

<!-- LINKS -->
[azure_cli]: https://docs.microsoft.com/cli/azure
[azure_pattern_circuit_breaker]: https://docs.microsoft.com/azure/architecture/patterns/circuit-breaker
[azure_pattern_retry]: https://docs.microsoft.com/azure/architecture/patterns/retry
[azure_portal]: https://portal.azure.com
[azure_sub]: https://azure.microsoft.com/free/
[cloud_shell]: https://docs.microsoft.com/azure/cloud-shell/overview
[computervision_account_create]: https://docs.microsoft.com/azure/computervision-db/how-to-manage-database-account
[computervision_account]: https://docs.microsoft.com/azure/computervision-db/account-overview
[computervision_container]: https://docs.microsoft.com/azure/computervision-db/databases-containers-items#azure-computervision-containers
[computervision_database]: https://docs.microsoft.com/azure/computervision-db/databases-containers-items#azure-computervision-databases
[computervision_docs]: https://docs.microsoft.com/azure/computervision-db/
[computervision_http_status_codes]: https://docs.microsoft.com/rest/api/computervision-db/http-status-codes-for-computervision
[computervision_item]: https://docs.microsoft.com/azure/computervision-db/databases-containers-items#azure-computervision-items
[computervision_request_units]: https://docs.microsoft.com/azure/computervision-db/request-units
[computervision_resources]: https://docs.microsoft.com/azure/computervision-db/databases-containers-items
[computervision_sql_queries]: https://docs.microsoft.com/azure/computervision-db/how-to-sql-query
[computervision_ttl]: https://docs.microsoft.com/azure/computervision-db/time-to-live
[pip]: https://pypi.org/project/pip/
[python]: https://www.python.org/downloads/
[ref_container_delete_item]: http://computervisionproto.westus.azurecontainer.io/#azure.computervision.Container.delete_item
[ref_container_query_items]: http://computervisionproto.westus.azurecontainer.io/#azure.computervision.Container.query_items
[ref_container_upsert_item]: http://computervisionproto.westus.azurecontainer.io/#azure.computervision.Container.upsert_item
[ref_container]: http://computervisionproto.westus.azurecontainer.io/#azure.computervision.Container
[ref_computervision_sdk]: http://computervisionproto.westus.azurecontainer.io
[ref_computervisionclient_create_database]: http://computervisionproto.westus.azurecontainer.io/#azure.computervision.computervisionClient.create_database
[ref_computervisionclient]: http://computervisionproto.westus.azurecontainer.io/#azure.computervision.computervisionClient
[ref_database]: http://computervisionproto.westus.azurecontainer.io/#azure.computervision.Database
[ref_httpfailure]: https://docs.microsoft.com/python/api/azure-computervision/azure.computervision.errors.httpfailure
[ref_item]: http://computervisionproto.westus.azurecontainer.io/#azure.computervision.Item
[sample_database_mgmt]: https://github.com/binderjoe/computervision-python-prototype/blob/master/examples/databasemanagementsample.py
[sample_document_mgmt]: https://github.com/binderjoe/computervision-python-prototype/blob/master/examples/documentmanagementsample.py
[sample_examples_misc]: https://github.com/binderjoe/computervision-python-prototype/blob/master/examples/examples.py
[source_code]: https://github.com/binderjoe/computervision-python-prototype
[venv]: https://docs.python.org/3/library/venv.html
[virtualenv]: https://virtualenv.pypa.io