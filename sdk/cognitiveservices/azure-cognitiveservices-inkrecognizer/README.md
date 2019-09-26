# Azure Ink Recognizer client library for Python

Azure Ink Recognizer SDK is an SDK for developers to work with Azure Ink Recognizer Service. The service recognize a collection of ink strokes and return a tree hierarchy of the recognized units, such as lines, words, shapes, as well as the handwriting recognition result of the words.

Features:

* Connect to Azure Ink Recognizer Service
* Convert collections of ink strokes into HTTP requests
* Parse HTTP response into ink recognition units

[Source code][source_code] | [Package (PyPi)][pypi] | [API reference documentation][ref_inkrecognizer_sdk] | [Product documentation][ink_recognizer_docs] | [Samples][samples]

## Getting started

### Install the package

Install the Azure Cosmos DB client library for Python with [pip][pip]:

```Bash
pip install azure-cognitiveservices-inkrecognizer
```

**Prerequisites**: You must have an [Azure subscription][azure_sub]. You must have [Python 2.7][python] or [Python 3.5.3+][python] to use this package. Asynchronous features supports Python 3.5.3+ only.

#### Get URL

TODO.

#### Get credentials

TODO.

## Key concepts

TODO.

## Examples

The [Samples][samples] provide several code snippets covering some of the most common Ink Recognizer SDK tasks, including:

* Implement InkPoint and InkStroke classes
* Convert stroke unit from pixel to mm
* Set language recognition locale
* Indexing a key word from recognition results
* Set application kind if user know expected type of ink content

### Implement ink stroke

If you don't have any pre-defined ink point or ink stroke classes, you can either follow the [Ink Stroke Interfaces][ink_stroke_file] to build your stroke, or build your own class that has all required fields. If you already defined ink strokes yourself, you should feed attributes in your class according to the interfaces.

```Python
from azure.cognitiveservices.inkrecognizer import InkStrokeKind

InkPoint = namedtuple("InkPoint", "x y")

class InkStroke():
    def __init__(self,
                 ink_stroke_id,
                 ink_points,
                 stroke_kind=InkStrokeKind.UNKNOWN,
                 stroke_language=""):
        self.id = ink_stroke_id
        self.points = ink_points
        self.kind = stroke_kind
        self.language = stroke_language
```

You can then create a list (or any iterable object) of ink strokes for recognition.

### Create a client

Once you got the url for ink recognizer service and an Azure credential instance, you can create an InkRecognizerClient

```Python
from azure.cognitiveservices.inkrecognizer import InkRecognizerClient
client = InkRecognizerClient(url, credential)
```

Or use Async version (Python 3.5.3+ only)

```Python
from azure.cognitiveservices.inkrecognizer.aio import InkRecognizerClient
client = InkRecognizerClient(url, credential)
```

### Send a request

You can then send stroke list to Ink Recognizer Service and get the root of all ink recognition results.

```Python
# Sync version
recognition_root = client.recognize_ink(ink_stroke_list)
# Async version
recognition_root = await client.recognize_ink(ink_stroke_list)
```

### Get recognition units from results

You can get all the recognition units either by InkRecognitionUnitKind or by hierarchy, then visit support properties of the units. [API reference documentation][ref_inkrecognizer_sdk]

```Python
lines = recognition_root.lines
for line in lines:
    foo_show_bounding_box(line.bounding_box)
    for word in line.words:
        print(word.recognized_text)
```

## Troubleshooting

TODO.

## Next steps

TODO.

### Additional documentation

For more extensive documentation on the Ink Recognizer Service, see the [Ink Recognizer Service Documentation][ink_recognizer_docs].

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

<!-- LINKS -->
[azure_sub]: https://azure.microsoft.com/free/
[ink_recognizer_docs]: https://docs.microsoft.com/en-us/azure/cognitive-services/ink-recognizer/
[pip]: https://pypi.org/project/pip/
[pypi]: https://pypi.org/project/azure-cosmos/
[python]: https://www.python.org/downloads/
[ref_inkrecognizer_sdk]: https://
[ref_ink_stroke_file]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-inkrecognizer/azure/cognitiveservices/inkrecognizer/_ink_stroke.py
[ref_inkrecognizer_client]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-inkrecognizer/azure/cognitiveservices/inkrecognizer/_client.py
[samples]: https://github.com/Azure-Samples/cognitive-services-python-sdk-samples/tree/master/samples/vision
[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-inkrecognizer
