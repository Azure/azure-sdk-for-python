# Azure AI Model Client Library for Python

The Model Client library allows you to do inference against any of AI models in you deployed to Azure. It supports both "model as a service" and "models with hosted managed infrastructure". For more information see [Overview: Deploy models, flows, and web apps with Azure AI Studio](https://learn.microsoft.com/azure/ai-studio/concepts/deployments-overview).

Use the model client library to:

* Authenticate against the service
* Get chat completions
* Get embeddings
* Generate an image from a text prompt

Note that for inference of OpenAI models hosted on azure you should be using the [OpenAI Python client library](https://github.com/openai/openai-python) instead of this client.

[Product documentation](https://learn.microsoft.com/azure/ai-studio/concepts/deployments-overview)
| [Samples](https://aka.ms/azsdk/model-client/samples/python)
| [API reference documentation](https://aka.ms/azsdk/model-client/ref-docs/python)
| [Package (Pypi)](https://aka.ms/azsdk/model-client/package/pypi)
| [SDK source code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-inference/azure/ai/inference)

## Getting started

### Prerequisites

* [Python 3.8](https://www.python.org/) or later installed, including [pip](https://pip.pypa.io/en/stable/).
* An [Azure subscription](https://azure.microsoft.com/free).
* A [TBD resource](https://azure.microsoft.com/) in your Azure subscription. You will need the key and endpoint from this resource to authenticate against the service.

### Install the Model Client package

```bash
pip install azure-ai-inferencing
```

### Set environment variables

To authenticate the `ModelClient`, you will need the endpoint and key from your TBD resource in the [Azure Portal](https://portal.azure.com). The code snippet below assumes these values are stored in environment variables:

* Set the environment variable `MODEL_ENDPOINT` to the endpoint URL. It has the form `https://your-model-deployment-name.your-azure-region.inference.ai.azure.com`, where `your-model-deployment-name` is your unique TBD resource name.

* Set the environment variable `MODEL_KEY` to the key. The key is a 32-character string.

Note that the client library does not directly read these environment variable at run time. The endpoint and key must be provided to the constructor of `ModelClient` in your code. The code snippet below reads environment variables to promote the practice of not hard-coding secrets in your source code.

### Create and authenticate the client

Once you define the environment variables, this Python code will create and authenticate a synchronous `ModelClient`:

<!-- SNIPPET:sample_chat_completions.create_client -->

```python
import os
from azure.ai.inference import ModelClient
from azure.ai.inference.models import ChatRequestSystemMessage, ChatRequestUserMessage, UnknownParameters
from azure.core.credentials import AzureKeyCredential

# Read the values of your model endpoint and key from environment variables
try:
    endpoint = os.environ["MODEL_ENDPOINT"]
    key = os.environ["MODEL_KEY"]
except KeyError:
    print("Missing environment variable 'MODEL_ENDPOINT' or 'MODEL_KEY'")
    print("Set them before running this sample.")
    exit()

# Create Model Client for synchronous operations
client = ModelClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)
```

<!-- END SNIPPET -->

A synchronous client supports synchronous inference methods, meaning they will block until the service responds with inference results. The code snippets below all use synchronous methods because it's easier for a getting-started guide. The SDK offers equivalent asynchronous APIs which are often preferred. To create an asynchronous client, do the following:

* Update the above code to import `ModelClient` from the `aio` namespace:

    ```python
    from azure.ai.inference.aio import ModelClient
    ```

* Install the additional package [aiohttp](https://pypi.org/project/aiohttp/):

    ```bash
    pip install aiohttp
    ```

## Key concepts

### Chat Completions

TBD

Target the `/v1/chat/completions` route

### Embeddings

TBD

Target the `/v1/embeddings` route

### Image Generation

TBD

Target the `/images/generations` route

## Examples

The following sections provide code snippets covering these common scenarios:

* [Chat completions](#chat-completions-example)
* [Embeddings](#embeddings-example)
* [Image geneartion](#image-generation-example)

These snippets use the synchronous `client` from [Create and authenticate the client](#create-and-authenticate-the-client).

See the [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-inference/samples) folder for fully working samples for synchronous and asynchronous clients.

### Chat completions example

This example demonstrates how to generate chat completions.

<!-- SNIPPET:sample_chat_completions.chat_completions -->

```python
# Do a single chat completion operation. This will be a synchronously (blocking) call.
result = client.get_chat_completions(
    messages=[
        ChatRequestSystemMessage(content="You are an AI assistant that helps people find information."),
        ChatRequestUserMessage(content="How many feet are in a mile?"),
    ]
)

# Print results the the console
print("Chat Completions:")
for index, choice in enumerate(result.choices):
    print(f"choices[{index}].message.content: {choice.message.content}")
    print(f"choices[{index}].message.role: {choice.message.role}")
    print(f"choices[{index}].finish_reason: {choice.finish_reason}")
    print(f"choices[{index}].index: {choice.index}")
print(f"id: {result.id}")
print(f"created: {result.created}")
print(f"model: {result.model}")
print(f"object: {result.object}")
print(f"usage.prompt_tokens: {result.usage.prompt_tokens}")
print(f"usage.completion_tokens: {result.usage.completion_tokens}")
print(f"usage.total_tokens: {result.usage.total_tokens}")
```

<!-- END SNIPPET -->

To generate completions for additional messages, simply call `get_chat_completions` multiple times using the same `ModelClient`.

### Embeddings example

This example demonstrates how to get embeddings.

<!-- SNIPPET:sample_embeddings.embeddings -->

```python
# Do a single embeddings operation. This will be a synchronously (blocking) call.
result = client.get_embeddings(input=["first sentence", "second sentence", "third sentence"])

# Print results the the console
print("Embeddings result:")
for index, item in enumerate(result.data):
    len = item.embedding.__len__()
    print(f"data[{index}].index: {item.index}")
    print(f"data[{index}].embedding[0]: {item.embedding[0]}")
    print(f"data[{index}].embedding[1]: {item.embedding[1]}")
    print("...")
    print(f"data[{index}].embedding[{len-2}]: {item.embedding[len-2]}")
    print(f"data[{index}].embedding[{len-1}]: {item.embedding[len-1]}")
print(f"id: {result.id}")
print(f"model: {result.model}")
print(f"object: {result.object}")
print(f"usage.prompt_tokens: {result.usage.prompt_tokens}")
print(f"usage.total_tokens: {result.usage.total_tokens}")
```

<!-- END SNIPPET -->

### Image generation example

This example demonstrates how to generate and image from a text prompt

<!-- SNIPPET:sample_image_generation.image_generation -->

```python
# Generate a single image from a text prompt. This will be a synchronously (blocking) call.
result = client.get_image_generations(
    prompt="A painting of a beautiful sunset over a mountain lake.",
    size="1024x768"
)

# Save generated image to file and print other results the the console
print("Image generation result:")
for index, item in enumerate(result.data):
    with open(f"image_{index}.png", "wb") as image:
        image.write(item.b64_json.decode('base64'))
print(f"id: {result.id}")
print(f"model: {result.model}")
print(f"created: {result.created}")
```

<!-- END SNIPPET -->

## Troubleshooting

### Exceptions

The `get_chat_completions`, `get_embeddings` and `get_image_geneartions` methods raise an [HttpResponseError](https://learn.microsoft.com/python/api/azure-core/azure.core.exceptions.httpresponseerror) exception for a non-success HTTP status code response from the service. The exception's `status_code` will be the HTTP response status code. The exception's `error.message` contains a detailed message that will allow you to diagnose the issue:

```python
from azure.core.exceptions import HttpResponseError

...

try:
    result = client.get_chat_completions( ... )
except HttpResponseError as e:
    print(f"Status code: {e.status_code} ({e.reason})")
    print(f"{e}")
```

For example, when you provide a wrong authentication key:

```text
Status code: 401 (Unauthorized)
Operation returned an invalid status 'Unauthorized'
Content: {"status": "Invalid auth token"}
```

Or for example when you call `get_embeddings` on a model that does not support the `/v1/embeddings` route:

```text
Status code: 424 (Failed Dependency)
Operation returned an invalid status 'Failed Dependency'
Content: {"detail":"Not Found"}
```

### Logging

The client uses the standard [Python logging library](https://docs.python.org/3/library/logging.html). The SDK logs HTTP request and response details, which may be useful in troubleshooting. To log to stdout, add the following:

```python
import sys
import logging

# Acquire the logger for this client library. Use 'azure' to affect both
# 'azure.core` and `azure.ai.vision.imageanalysis' libraries.
logger = logging.getLogger("azure")

# Set the desired logging level. logging.INFO or logging.DEBUG are good options.
logger.setLevel(logging.INFO)

# Direct logging output to stdout (the default):
handler = logging.StreamHandler(stream=sys.stdout)
# Or direct logging output to a file:
# handler = logging.FileHandler(filename = 'sample.log')
logger.addHandler(handler)

# Optional: change the default logging format. Here we add a timestamp.
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s")
handler.setFormatter(formatter)
```

By default logs redact the values of URL query strings, the values of some HTTP request and response headers (including `Authorization` which holds the key), and the request and response payloads. To create logs without redaction, set the method argument `logging_enable = True` when you construct `ModelClient`, or when you call any of the client's operation methods (e.g. `get_chat_completions`).

```python
# Create a Model Client with none redacted log
client = ModelClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key),
    logging_enable=True
)
```

None redacted logs are generated for log level `logging.DEBUG` only. Be sure to protect none redacted logs to avoid compromising security. For more information see [Configure logging in the Azure libraries for Python](https://aka.ms/azsdk/python/logging)

## Next steps

* Have a look at the [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/vision/azure-ai-vision-imageanalysis/samples) folder, containing fully runnable Python code for Image Analysis (all visual features, synchronous and asynchronous clients, from image file or URL).

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit [https://cla.microsoft.com](https://cla.microsoft.com).

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct). For more information,
see the Code of Conduct FAQ or contact opencode@microsoft.com with any
additional questions or comments.


<!-- Note: I did not use LINKS section here with a list of `[link-label](link-url)` because these
links don't work in the Sphinx generated documentation. The index.html page of these docs
include this README, but with broken links.-->
