# Azure model inference client library for Python

The client Library allows you to do inference using AI models you deployed to Azure. It supports both serverless endpoints (aka "model as a service" (MaaS) or "pay as you go") and selfhosted endpoints (aka "model as a platform" (MaaP) or "real-time endpoints"). The client library makes services calls using REST AP version `2024-04-01-preview` specificed here (TODO: insert link). For more information see [Overview: Deploy models, flows, and web apps with Azure AI Studio](https://learn.microsoft.com/azure/ai-studio/concepts/deployments-overview).

Use the model inference client library to:

* Authenticate against the service
* Get information about the model
* Get chat completions
* Get embeddings
* Generate an image from a text prompt

Note that for inference using OpenAI models hosted on Azure you should be using the [OpenAI Python client library](https://github.com/openai/openai-python) instead of this client.

[Product documentation](https://learn.microsoft.com/azure/ai-studio/concepts/deployments-overview)
| [Samples](https://aka.ms/azsdk/model-client/samples/python)
| [API reference documentation](https://aka.ms/azsdk/model-client/ref-docs/python)
| [Package (Pypi)](https://aka.ms/azsdk/model-client/package/pypi)
| [SDK source code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-inference/azure/ai/inference)

## Getting started

### Prerequisites

* [Python 3.8](https://www.python.org/) or later installed, including [pip](https://pip.pypa.io/en/stable/).
* An [Azure subscription](https://azure.microsoft.com/free).
* An [AI Model from the catalog](https://ai.azure.com/explore/models) deployed through Azure AI Studio. To construct the client library, you will need to pass in the endpoint URL and key associated with your deployed AI model.

  * The endpoint URL has the form `https://your-deployment-name.your-azure-region.inference.ai.azure.com`, where `your-deployment-name` is your unique model deployment name and `your-azure-region` is the Azure region where the model is deployed (e.g. `eastus2`).

  * The key is a 32-character string.

### Install the package

```bash
pip install azure-ai-inferencing
```

### Create and authenticate clients

The package includes three clients `ChatCompletionsClient`, `EmbeddingsClient` and `ImageGenerationClients`. They are all created in the similar manner. For example, assuming `endpoint` and `key` are strings holding your endpoint URL and key, this Python code will create and authenticate a synchronous `ChatCompletionsClient`:

```python
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)
```

A synchronous client supports synchronous inference methods, meaning they will block until the service responds with inference results. For simplicity the code snippets below all use synchronous methods. The client offers equivalent asynchronous methods which are more commonly used in production.

To create an asynchronous client, Install the additional package [aiohttp](https://pypi.org/project/aiohttp/):

```bash
    pip install aiohttp
```

and update the code above to import `ChatCompletionsClient` from the `aio` namespace:

```python
import asyncio
from azure.ai.inference.aio import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)
```

## Key concepts

### Chat Completions

TODO: Add overview and link to explain chat completions.

Chat completion operations target the URL route `/v1/chat/completions` on the provided endpoint.

### Embeddings

TODO: Add overview and link to explain embeddings.

Embeddings operations target the URL route `/v1/embeddings` on the provided endpoint.

### Image Generation

TODO: Add overview and link to explain image generation.

Image generation operations target the URL route `/images/generations` on the provided endpoint.

## Examples

In the following sections you will find simple examples of:

* [Chat completions](#chat-completions-example)
* [Streaming chat completions](#streaming-chat-completions-example)
* [Embeddings](#embeddings-example)
* [Image geneartion](#image-generation-example)

The examples create a synchronous client as mentioned in [Create and authenticate clients](#create-and-authenticate-clients). Only mandatory input settings are shown for simplicity.

See the [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-inference/samples) folder for full working samples for synchronous and asynchronous clients.

### Chat completions example

This example demonstrates how to generate a single chat completions.

<!-- SNIPPET:sample_chat_completions.chat_completions -->

```python
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

result = client.create(
    messages=[
        SystemMessage(content="You are a helpful assistant."),
        UserMessage(content="How many feet are in a mile?"),
    ]
)

print(result.choices[0].message.content)
```

<!-- END SNIPPET -->

The printed result of course depends on the model, but you should get something like this: `Hello! I'd be happy to help answer your question. There are 5,280 feet in a mile`.

To generate completions for additional messages, simply call `client.create` multiple times using the same `client`.

### Streaming chat completions example

This example demonstrates how to generate a single chat completions with streaming response.

<!-- SNIPPET:sample_chat_completions_streaming.chat_completions_streaming -->

```python
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

result = client.create_streaming(
    messages=[
        SystemMessage(content="You are a helpful assistant."),
        UserMessage(content="Give me 5 good reasons why I should exercise every day."),
    ]
)

for update in result:
    print(update.choices[0].delta.content, end="")
```

<!-- END SNIPPET -->

The printed result of course depends on the model, but you should see the answer progressively get longer as updates get streamed to the client.

To generate completions for additional messages, simply call `client.create_streaming` multiple times using the same `client`.

### Embeddings example

This example demonstrates how to get embeddings.

<!-- SNIPPET:sample_embeddings.embeddings -->

```python
from azure.ai.inference import EmbeddingsClient
from azure.core.credentials import AzureKeyCredential

client = EmbeddingsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

result = client.create(input=["first phrase", "second phrase", "third phrase"])

for item in result.data:
    length = len(item.embedding)
    print(
        f"data[{item.index}]: length={length}, [{item.embedding[0]}, {item.embedding[1]}, "
        f"..., {item.embedding[length-2]}, {item.embedding[length-1]}]"
    )
```

<!-- END SNIPPET -->

The printed result of course depends on the model, but you should see something like this:
```txt
data[0]: length=1024, [0.0013399124, -0.01576233, ..., 0.007843018, 0.000238657]
data[1]: length=1024, [0.036590576, -0.0059547424, ..., 0.011405945, 0.004863739]
data[2]: length=1024, [0.04196167, 0.029083252, ..., -0.0027484894, 0.0073127747]
```

To generate embeddings for additional phrases, simply call `client.create` multiple times using the same `client`.

### Image generation example

This example demonstrates how to generate an image of size 1024x768 from a text prompt, and save the resulting image to a `image.png` file.

<!-- SNIPPET:sample_image_generation.image_generation -->

```python
from azure.ai.inference import ImageGenerationClient
from azure.core.credentials import AzureKeyCredential

client = ImageGenerationClient(endpoint=endpoint, credential=AzureKeyCredential(key))

result = client.create(prompt="A painting of a beautiful sunset over a mountain lake.", size="1024x768")

with open(f"image.png", "wb") as image:
    image.write(result.data[0].b64_json.decode("base64"))
```

<!-- END SNIPPET -->

## Troubleshooting

### Exceptions

The `create` and `get_model_info` methods on the clients raise an [HttpResponseError](https://learn.microsoft.com/python/api/azure-core/azure.core.exceptions.httpresponseerror) exception for a non-success HTTP status code response from the service. The exception's `status_code` will be the HTTP response status code. The exception's `error.message` contains a detailed message that will allow you to diagnose the issue:

```python
from azure.core.exceptions import HttpResponseError

...

try:
    result = client.create( ... )
except HttpResponseError as e:
    print(f"Status code: {e.status_code} ({e.reason})")
    print(f"{e}")
```

For example, when you provide a wrong authentication key:

```text
Status code: 401 (Unauthorized)
Operation returned an invalid status 'Unauthorized'
Content: {"status": "Invalid auth token"}
```v

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

By default logs redact the values of URL query strings, the values of some HTTP request and response headers (including `Authorization` which holds the key), and the request and response payloads. To create logs without redaction, set the method argument `logging_enable = True` when you construct the client library, or when you call any of the client's `create` methods.

```python
# Create a Model Client with none redacted log
client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key),
    logging_enable=True
)
```

None redacted logs are generated for log level `logging.DEBUG` only. Be sure to protect none redacted logs to avoid compromising security. For more information see [Configure logging in the Azure libraries for Python](https://aka.ms/azsdk/python/logging)

## Next steps

* Have a look at the [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-inference/samples) folder, containing fully runnable Python code for doing inference using synchronous and asynchronous clients.

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
