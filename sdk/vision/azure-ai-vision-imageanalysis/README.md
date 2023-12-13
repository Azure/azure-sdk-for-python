# Image Analysis client library for Python

The Image Analysis service provides AI algorithms for processing images and returning information about their content. In a single service call, you can extract one or more visual features from the image simultaneously, including getting a caption for the image, extracting text shown in the image (OCR) and detecting objects. For more information on the service and the supported visual features, see [Image Analysis overview][image_analysis_overview], and the [Concepts][image_analysis_concepts] page.

Use the Image Analysis client library to:
* Authenticate against the service
* Set what features you would like to extract
* Upload an image for analysis, or send an image URL
* Get the analysis result

[Product documentation][image_analysis_overview] 
| [Samples](samples)
| [Vision Studio][vision_studio]
| [API reference documentation](https://learn.microsoft.com/python/api/azure-ai-vision-imageanalysis)
| [Package (Pypi)](https://pypi.org/project/azure-ai-vision-imageanalysis/)
| [Package (Conda)](https://anaconda.org/microsoft/azure-ai-vision-imageanalysis)
| [SDK source code](azure/ai/vision/imageanalysis)

## Getting started

### Prerequisites

* [Python 3.7](https://www.python.org/) or later installed, including [pip](https://pip.pypa.io/en/stable/).
* An [Azure subscription](https://azure.microsoft.com/free).
* A [Computer Vision resource](https://portal.azure.com/#create/Microsoft.CognitiveServicesComputerVision) in your Azure subscription.
  * You will need the key and endpoint from this resource to authenticate against the service.
  * You can use the free pricing tier (`F0`) to try the service, and upgrade later to a paid tier for production.
  * Note that in order to run Image Analysis with the `Caption` or `Dense Captions` features, the Azure resource needs to be from one of the following GPU-supported regions: `East US`, `France Central`, `Korea Central`, `North Europe`, `Southeast Asia`, `West Europe`, or `West US`.

### Install the Image Analysis package

```bash
pip install azure-ai-vision-imageanalysis
```
### Set environment variables

To authenticate the `ImageAnalysisClient`, you will need the endpoint and key from your Azure Computer Vision resource in the [Azure Portal](https://portal.azure.com). The code snippet below assumes these values are stored in environment variables:

* Set the environment variable `VISION_ENDPOINT` to the endpoint URL. It has the form `https://your-resource-name.cognitiveservices.azure.com`, where `your-resource-name` is your unique Azure Computer Vision resource name.

* Set the environment variable `VISION_KEY` to the key. The key is a 32-character Hexadecimal number.

### Create and authenticate the client

Once you define the environment variables, this Python code will create and authenticate a synchronous `ImageAnalysisClient`:

<!-- SNIPPET:sample_caption_image_file.create_client -->

```python
import os
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

# Set the values of your computer vision endpoint and computer vision key 
# as environment variables:
try:
    endpoint = os.environ["VISION_ENDPOINT"]
    key = os.environ["VISION_KEY"]
except KeyError:
    print("Missing environment variable 'VISION_ENDPOINT' or 'VISION_KEY'")
    print("Set them before running this sample.")
    exit()

# Create an Image Analysis client for synchronous operations
client = ImageAnalysisClient(
    endpoint = endpoint,
    credential = AzureKeyCredential(key))
```

<!-- END SNIPPET -->

A synchronous client supports synchronous analysis methods, meaning they will block until the service responds with analysis results. The code snippets below all use synchronous methods because it's easier for a getting-started guide. The SDK offers equivalent asynchronous APIs which are often preferred. To create an asynchronous client, simply update the above code to import `ImageAnalysisClient` from the `aio` namespace:

```python
from azure.ai.vision.imageanalysis.aio import ImageAnalysisClient
```

## Key concepts

### Visual features

Once you've initialized an `ImageAnalysisClient`, you need to select one or more visual features to analyze. The options are specified by the enum class `VisualFeatures`. The following features are supported:

1. `VisualFeatures.CAPTION` ([Examples](#generate-an-image-caption-for-an-image-file) | [Samples](samples)): Generate a human-readable sentence that describes the content of an image.
1. `VisualFeatures.READ` ([Examples](#extract-text-from-the-image-file) | [Samples](samples)): Also known as Optical Character Recognition (OCR). Extract printed or handwritten text from images.
1. `VisualFeatures.DENSE_CAPTIONS` ([Samples](samples)): Dense Captions provides more details by generating one-sentence captions for up to 10 different regions in the image, including one for the whole image. 
1. `VisualFeatures.TAGS` ([Samples](samples)): Extract content tags for thousands of recognizable objects, living beings, scenery, and actions that appear in images.
1. `VisualFeatures.OBJECTS` ([Samples](samples)): Object detection. This is similar to tagging, but focused on detecting physical objects in the image and returning their location.
1. `VisualFeatures.SMART_CROPS` ([Samples](samples)): Used to find a representative sub-region of the image for thumbnail generation, with priority given to include faces.
1. `VisualFeatures.PEOPLE` ([Samples](samples)): Detect people in the image and return their location.

For more information about these features, see [Image Analysis overview][image_analysis_overview], and the [Concepts][image_analysis_concepts] page.

### Analyze from image buffer or URL

The `ImageAnalysisClient` has two methods `analyze_from_buffer` and `analyze_from_url`.
* `analyze_from_buffer`: Analyze an image from an input [bytes](https://docs.python.org/3/library/stdtypes.html#bytes-objects) object. The client will upload the image to the service as part of the REST request. 
* `analyze_from_url`: Analyze an image from a publicly-accessible URL, via the `ImageUrl` object. The client will send the image URL to the service. The service will download the image.

The examples below show how to do both. The `analyze_from_buffer` examples populate the input `bytes` object by loading an image from a file on disk.

### Supported image formats

Image Analysis works on images that meet the following requirements:
* The image must be presented in JPEG, PNG, GIF, BMP, WEBP, ICO, TIFF, or MPO format
* The file size of the image must be less than 20 megabytes (MB)
* The dimensions of the image must be greater than 50 x 50 pixels and less than 16,000 x 16,000 pixels


## Examples

The following sections provide code snippets covering these common Image Analysis scenarios:

* [Generate an image caption for an image file](#generate-an-image-caption-for-an-image-file)
* [Generate an image caption for an image URL](#generate-an-image-caption-for-an-image-url)
* [Extract text (OCR) from an image file](#extract-text-from-an-image-file)
* [Extract text (OCR) from an image URL](#extract-text-from-an-image-url)

These snippets use the synchronous `client` from [Create and authenticate the client](#3-create-and-authenticate-the-client).

See the [Samples](samples) folder for fully working samples for all visual features, including asynchronous clients.

### Generate an image caption for an image file

This example demonstrates how to generate a one-sentence caption for the image file [sample.jpg](sample.jpg) using the `ImageAnalysisClient`. The synchronous (blocking) `analyze_from_buffer` method call returns an `ImageAnalysisResult` object with a `caption` property of type `CaptionResult`. It contains the generated caption and its confidence score in the range [0, 1]. By default the caption may contain gender terms such as "man", "woman", or "boy", "girl". You have the option to request gender-neutral terms such as "person" or "child" by setting `gender_neutral_caption = True` when calling `analyze_from_buffer`.

Notes:
* Caption is only available in some Azure regions. See [Prerequisites](#prerequisites).
* Caption is only supported in English at the moment.

<!-- SNIPPET:sample_caption_image_file.caption -->

```python
# Load image to analyze into a 'bytes' object
with open("sample.jpg", 'rb') as f:
    image_buffer = bytes(f.read())

# Get a caption for the image. This will be a synchronously (blocking) call.
result = client.analyze(
    image_content = image_buffer,
    visual_features = [ VisualFeatures.CAPTION ],
    gender_neutral_caption = True) # Optional (default is False)

client.close()

# Print caption results to the console
print(f"Image analysis results:")
print(f" Caption:")
print(f"   '{result.caption.text}', Confidence {result.caption.confidence:.4f}")
```

<!-- END SNIPPET -->

To generate captions for additional images, simply call the 'analyze_from_buffer' multiple times. You can use the same `ImageAnalysisClient` do to multiple analysis calls.

### Generate an image caption for an image URL

This example is similar to the above, expect it calls the `analyze_from_url` method and provides a [publicly accessible image URL](https://aka.ms/azai/vision/image-analysis-sample.jpg) instead of a file name.

<!-- SNIPPET:sample_caption_image_url.caption -->

```python
# Get a caption for the image. This will be a synchronously (blocking) call.
result = client.analyze(
    image_content = "https://aka.ms/azai/vision/image-analysis-sample.jpg",
    visual_features = [ VisualFeatures.CAPTION ],
    gender_neutral_caption = True) # Optional (default is False)

client.close()

# Print caption results to the console
print(f"Image analysis results:")
print(f" Caption:")
print(f"   '{result.caption.text}', Confidence {result.caption.confidence:.4f}")
```

<!-- END SNIPPET -->

### Extract text from an image file

This example demonstrates how to extract printed or hand-written text for the image file [sample.jpg](sample.jpg) using the `ImageAnalysisClient`. The synchronous (blocking) `analyze_from_buffer` method call returns an `ImageAnalysisResult` object with a `read` property of type `ReadResult`. It includes a list of text lines and a bounding polygon surrounding each text line. For each line, it also returns a list of words in the text line and a bounding polygon surrounding each word.

<!-- SNIPPET:sample_ocr_image_file.read -->

```python
# Load image to analyze into a 'bytes' object
with open("sample.jpg", 'rb') as f:
    image_buffer = bytes(f.read())

# Extract text (OCR) from an image stream. This will be a synchronously (blocking) call.
result = client.analyze(
    image_content = image_buffer,
    visual_features = [ VisualFeatures.READ ])

client.close()

# Print text (OCR) analysis results to the console
print(f"Image analysis results:")
print(f" Read:")
for line in result.read.blocks[0].lines:
    print(f"   Line: '{line.text}', Bounding box {line.bounding_polygon}")
    for word in line.words:
        print(f"     Word: '{word.text}', Bounding polygon {word.bounding_polygon}, Confidence {word.confidence:.4f}")
```

<!-- END SNIPPET -->

To extract text for additional images, simply call the 'analyze_from_buffer' multiple times. You can use the same ImageAnalysisClient do to multiple analysis calls.


### Extract text from an image URL

This example is similar to the above, expect it calls the `analyze_from_url` method and provides a [publicly accessible image URL](https://aka.ms/azai/vision/image-analysis-sample.jpg) instead of a file name.

<!-- SNIPPET:sample_ocr_image_url.read -->

```python
# Extract text (OCR) from an image stream. This will be a synchronously (blocking) call.
result = client.analyze(
    image_content = "https://aka.ms/azai/vision/image-analysis-sample.jpg",
    visual_features = [ VisualFeatures.READ ])

client.close()

# Print text (OCR) analysis results to the console
print(f"Image analysis results:")
print(f" Read:")
for line in result.read.blocks[0].lines:
    print(f"   Line: '{line.text}', Bounding box {line.bounding_polygon}")
    for word in line.words:
        print(f"     Word: '{word.text}', Bounding polygon {word.bounding_polygon}, Confidence {word.confidence:.4f}")
```

<!-- END SNIPPET -->


## Troubleshooting

### Exceptions

The `analyze_from_buffer` and `analyze_from_url` methods raise an [HttpResponseError](https://learn.microsoft.com/python/api/azure-core/azure.core.exceptions.httpresponseerror) exception for a non-success HTTP status code response from the service. The exception's `status_code` will be the HTTP response status code. The exception's `error.message` contains a detailed message that will allow you to diagnose the issue:

```python
try:
    result = client.analyze_from_url( ... )
except HttpResponseError as e:
    print(f"Status code: {e.status_code}")
    print(f"Reason: {e.reason}")
    print(f"Message: {e.error.message}")
```

For example, when you provide a wrong authentication key:
```
Status code: 401
Reason: PermissionDenied
Message: Access denied due to invalid subscription key or wrong API endpoint. Make sure to provide a valid key for an active subscription and use a correct regional API endpoint for your resource.
```

Or when you provide an image URL that does not exist or not accessible:
```
Status code: 400
Reason: Bad Request
Message: The provided image url is not accessible.
```

### Logging

The client uses the standard [Python logging library](https://docs.python.org/3/library/logging.html). The SDK logs HTTP request and response details, which may be useful in troubleshooting. To log to stdout, add the following:

<!-- SNIPPET:sample_analyze_all_image_file.logging -->

```python
import sys
import logging

# Acquire the logger for this client library. Use 'azure' to affect both 
# 'azure.core` and `azure.ai.vision.imageanalysis' libraries.
logger = logging.getLogger('azure')

# Set the desired logging level. logging.INFO or logging.DEBUG are good options.
logger.setLevel(logging.INFO)

# Direct logging output to stdout (the default):
handler = logging.StreamHandler(stream = sys.stdout)
# Or direct logging output to a file:
# handler = logging.FileHandler(filename = 'sample.log')
logger.addHandler(handler)

# Optional: change the default logging format. Here we add a timestamp.
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
handler.setFormatter(formatter)
```

<!-- END SNIPPET -->

By default logs redact the values of URL query strings, the values of some HTTP request and response headers (including `Ocp-Apim-Subscription-Key` which holds the key), and the request and response payloads. To create logs without redaction, set the method argument `logging_enable = True` when you create `ImageAnalysisClient`, or when you call `analyze_from_buffer` and `analyze_from_url` on the client. 

<!-- SNIPPET:sample_analyze_all_image_file.create_client_with_logging -->

```python
# Create an Image Analysis client with none redacted log
client = ImageAnalysisClient(
    endpoint = endpoint,
    credential = AzureKeyCredential(key),
    logging_enable = True)
```

<!-- END SNIPPET -->

None redacted logs are generated for log level `logging.DEBUG` only. Be sure to protect none redacted logs to avoid compromising security. For more information see [Configure logging in the Azure libraries for Python](https://aka.ms/azsdk/python/logging)


## Next steps

* Have a look at the [Samples](samples) folder, containing fully runnable Python code for Image Analysis (all visual features, synchronous and asynchronous clients, from image file or URL).

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
[Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct). For more information,
see the Code of Conduct FAQ or contact opencode@microsoft.com with any
additional questions or comments.

<!-- LINKS -->
[image_analysis_overview]: https://learn.microsoft.com/azure/ai-services/computer-vision/overview-image-analysis?tabs=4-0
[image_analysis_concepts]: https://learn.microsoft.com/azure/ai-services/computer-vision/concept-tag-images-40
[vision_studio]: https://portal.vision.cognitive.azure.com/gallery/imageanalysis

