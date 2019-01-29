# Azure Cognitive Services Computer Vision SDK for Python

The cloud-based Computer Vision service provides developers with access to advanced algorithms for processing images and returning information. Computer Vision works with popular image formats, such as JPEG and PNG. To analyze an image, you can either upload an image or specify an image URL. Computer Vision algorithms can analyze the content of an image in different ways, depending on the visual features you're interested in. For example, Computer Vision can determine if an image contains adult or racy content, or find all the faces in an image.

You can use Computer Vision in your application to:

- Analyze images for insight
- Extract text from images
- Moderate content in images

Looking for source code or API reference?

* [SDK source code][source_code]
* [SDK reference documentation][ref_computervision_sdk]

## Prerequisites

* Azure subscription - [Create a free account][azure_sub]
* Azure [Computer Vision resource][computer_vision_resource] - SQL API
* [Python 3.6+][python]

If you need a Computer Vision API account, you can create one with this [Azure CLI][azure_cli] command:

```Bash
az cognitiveservices account create -n myresource -g myResourceGroup --kind ComputerVision --sku S1 -l WestEurope --yes
```

## Installation

Install the Azure Cognitive Services Computer Vision SDK with [pip][pip], optionally within a [virtual environment][venv].

### Configure a virtual environment (optional)

Although not required, you can keep your your base system and Azure SDK environments isolated from one another if you use a virtual environment. Execute the following commands to configure and then enter a virtual environment with [venv][venv]:

```Bash
python3 -m venv azure-cognitiveservices-vision-computervision-environment
source azure-cognitiveservices-vision-computervision-environment/bin/activate
```

### Install the SDK

Install the Azure Cognitive Services Computer Vision SDK for Python with [pip][pip]:

```Bash
pip install git+https://github.com/johanste/azure-computervision-python.git@ux git+https://github.com/binderjoe/computervision-python-prototype.git@master
```

## Authentication

Interaction with Computer Vision starts with an instance of the [Computer Vision][ref_computervisionclient] class. You need an **account**, its **URI**, and one of its **account keys** to instantiate the client object.

### Get credentials

Use the Azure CLI snippet below to populate two environment variables with the Computer Vision account URI and its primary master key (you can also find these values in the Azure portal). The snippet is formatted for the Bash shell.

```Bash
RES_GROUP=<resource-group-name>
ACCT_NAME=<computervision-account-name>

export ACCOUNT_URI=$(az computervision show --resource-group $RES_GROUP --name $ACCT_NAME --query documentEndpoint --output tsv)
export ACCOUNT_KEY=$(az computervision list-keys --resource-group $RES_GROUP --name $ACCT_NAME --query primaryMasterKey --output tsv)
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

* [Analyze an image][ref_database]: You can analyze images using Computer Vision to detect and provide insight about the visual features and characteristics of your images. You can either upload the contents of an image to analyze local images, or you can specify the URL of an image to analyze remote images. 

* [Moderate images in content][ref_item]: Detect adult and racy content in an image, rating the likelihood that the image contains either adult or racy content and generating a confidence score for both. The filter for adult and racy content detection can be set on a sliding scale to accommodate your preferences.

* [Extract text from an image][ref_item]: Extract text using OCR from an image into a machine-readable character stream. If needed, OCR corrects the rotation of the recognized text, in degrees, around the horizontal image axis, and provides the frame coordinates of each word. OCR supports 25 languages, and automatically detects the language of extracted text.

For more information about these resources, see [Working with Azure computer vision][computervision_resources].

## Examples

The following sections provide several code snippets covering some of the most common computervision tasks, including:

* [Analyze an image](#)
* [Analyze an image by domain](#)
* [Describe image](#insert-data)
* [Generate thumbnail](#delete-data)
* [Get list of domains](#query-the-database)

### Analyze an image

After authenticating your [ComputerVisionAPI][ref_computervisionclient] client, you can analyze an image for certain features.

```Python
try:
    image_analysis = client.analyze_image(url,visual_features=[VisualFeatureTypes.tags])

    for tag in image_analysis.tags:
        print(tag)

except HTTPFailure as e:
    if e.status_code != 409:
        raise
```


### Analyze an image by domain

After authenticating your [ComputerVisionAPI][ref_computervisionclient] client, you can analyze an image by domain. 

```Python
domain = "landmarks"
url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Broadway_and_Times_Square_by_night.jpg/450px-Broadway_and_Times_Square_by_night.jpg"
language = "en"

try:
    analysis = client.analyze_image_by_domain(domain, url, language)

    print(analysis.result)

except HTTPFailure as e:
    if e.status_code != 409:
        raise
```

### Describe image

This example creates a container with default settings. If a container with the same name already exists in the database (generating a `409 Conflict` error), the existing container is obtained instead.

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
    if e.status_code != 409:
        raise
```

### Generate thumbnail

Retrieve an existing container from the database:

```Python
from PIL import Image
import io

width=50
height=50
url = "http://www.public-domain-photos.com/free-stock-photos-4/travel/san-francisco/golden-gate-bridge-in-san-francisco.jpg"

try:
    thumbnail = client.generate_thumbnail(width, height, url)

    for x in thumbnail:
        image = Image.open(io.BytesIO(x))
    image.save('thumbnail.jpg')


except HTTPFailure as e:
    if e.status_code != 409:
        raise
```

### Get subject domain list

The supported subject domains list contains all domains an image can be analyzed for.

```Python
try:
    models = client.list_models()

    for x in models.models_property:
        print(x)

except HTTPFailure as e:
    if e.status_code != 409:
        raise
```

<!--

{'additional_properties': {}, 'name': 'celebrities', 'categories': ['people_', '人_', 'pessoas_', 'gente_']}
{'additional_properties': {}, 'name': 'landmarks', 'categories': ['outdoor_', '户外_', '屋外_', 'aoarlivre_', 'alairelibre_', 'building_', '建筑_', '建物_', 'edifício_']}

-->

## Troubleshooting

### General

When you interact with computervision DB using the Python SDK, errors returned by the service correspond to the same HTTP status codes returned for REST API requests:

[HTTP Status Codes for Azure computervision DB][computervision_http_status_codes]

For example, if you try to create a container using an ID (name) that's already in use in your computervision DB database, a `409` error is returned, indicating the conflict. In the following snippet, the error is handled gracefully by catching the exception and displaying additional information about the error.

```Python
try:
    database.create_container(id=container_name, partition_key=PartitionKey(path="/productName")
except HTTPFailure as e:
    if e.status_code == 409:
        print("""Error creating container.
HTTP status code 409: The ID (name) provided for the container is already in use.
The container name must be unique within the database.""")
    else:
        raise
```

### Handle transient errors with retries

While working with computervision DB, you might encounter transient failures caused by [rate limits][computervision_request_units] enforced by the service, or other transient problems like network outages. For information about handling these types of failures, see [Retry pattern][azure_pattern_retry] in the Cloud Design Patterns guide, and the related [Circuit Breaker pattern][azure_pattern_circuit_breaker].

## Next steps

### More sample code

Several computervision DB Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with computervision DB:

* [`examples.py`][sample_examples_misc] - Contains the code snippets found in this article.
* [`databasemanagementsample.py`][sample_database_mgmt] - Python code for working with Azure computervision DB databases, including:
  * Create database
  * Get database by ID
  * Get database by query
  * List databases in account
  * Delete database
* [`documentmanagementsample.py`][sample_document_mgmt] - Example code for working with computervision DB documents, including:
  * Create container
  * Create documents (including those with differing schemas)
  * Get document by ID
  * Get all documents in a container

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