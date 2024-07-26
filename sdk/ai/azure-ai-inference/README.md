# Azure AI Inference client library for Python

The client Library (in preview) does inference, including chat completions, for AI models deployed by [Azure AI Studio](https://ai.azure.com) and [Azure Machine Learning Studio](https://ml.azure.com/). It supports Serverless API endpoints and Managed Compute endpoints. The client library makes services calls using REST API version `2024-05-01-preview`, as documented in [Azure AI Model Inference API](https://learn.microsoft.com/azure/ai-studio/reference/reference-model-inference-api). For more information see [Overview: Deploy models, flows, and web apps with Azure AI Studio](https://learn.microsoft.com/azure/ai-studio/concepts/deployments-overview).

Use the model inference client library to:

* Authenticate against the service
* Get information about the model
* Do chat completions
* Get text embeddings
<!-- * Get image embeddings -->

With some minor adjustments, this client library can also be configured to do inference for Azure OpenAI endpoints. See samples with `azure_openai` in their name, in the [samples folder](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-inference/samples).

[Product documentation](https://learn.microsoft.com/azure/ai-studio/reference/reference-model-inference-api)
| [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-inference/samples)
| [API reference documentation](https://aka.ms/azsdk/azure-ai-inference/python/reference)
| [Package (Pypi)](https://aka.ms/azsdk/azure-ai-inference/python/package)
| [SDK source code](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-inference/azure/ai/inference)

## Getting started

### Prerequisites

* [Python 3.8](https://www.python.org/) or later installed, including [pip](https://pip.pypa.io/en/stable/).
* An [Azure subscription](https://azure.microsoft.com/free).
* An [AI Model from the catalog](https://ai.azure.com/explore/models) deployed through Azure AI Studio.
* To construct the client library, you will need to pass in the endpoint URL. The endpoint URL has the form `https://your-host-name.your-azure-region.inference.ai.azure.com`, where `your-host-name` is your unique model deployment host name and `your-azure-region` is the Azure region where the model is deployed (e.g. `eastus2`).
* Depending on your model deployment and authentication preference, you either need an API key to authenticate against the service, or Entra ID credentials. The API key is a 32-character string.

### Install the package

To install the Azure AI Inferencing package use the following command:

```bash
pip install azure-ai-inference
```

To update an existing installation of the package, use:

```bash
pip install --upgrade azure-ai-inference
```

## Key concepts

### Create and authenticate a client directly, using key

The package includes two clients `ChatCompletionsClient` and `EmbeddingsClient`<!-- and `ImageGenerationClients`-->. Both can be created in the similar manner. For example, assuming `endpoint` and `key` are strings holding your endpoint URL and key, this Python code will create and authenticate a synchronous `ChatCompletionsClient`:

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

and update the code above to import `asyncio`, and import `ChatCompletionsClient` from the `azure.ai.inference.aio` namespace instead of `azure.ai.inference`:

```python
import asyncio
from azure.ai.inference.aio import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)
```

### Create and authenticate a client directly, using Entra ID

_Note: At the time of this package release, not all deployments support Entra ID authentication. For those who do, follow the instructions below._

To use an Entra ID token credential, first install the [azure-identity](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity) package:

```python
pip install azure.identity
```

You will need to provide the desired credential type obtained from that package. A common selection is [DefaultAzureCredential](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential) and it can be used as follows:

```python
from azure.ai.inference import ChatCompletionsClient
from azure.identity import DefaultAzureCredential

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(exclude_interactive_browser_credential=False)
)
```

During application development, you would typically set up the environment for authentication using Entra ID by first [Installing the Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli), running `az login` in your console window, then entering your credentials in the browser window that was opened. The call to `DefaultAzureCredential()` will then succeed. Setting `exclude_interactive_browser_credential=False` in that call will enable launching a browser window if the user isn't already logged in.

### Defining default settings while creating the clients

You can define default chat completions or embeddings configurations while constructing the relevant client. These configurations will be applied to all future service calls.

For example, here we create a `ChatCompletionsClient` using API key authentication, and apply two settings, `temperature` and `max_tokens`:

```python
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
    temperature=0.5,
    max_tokens=1000
)
```

Default settings can be overridden in individual service calls.

### Create and authenticate clients using `load_client`

As an alternative to creating a specific client directly, you can use the function `load_client` to return the relevant client (of types `ChatCompletionsClient` or `EmbeddingsClient`) based on the provided endpoint:

```python
from azure.ai.inference import load_client
from azure.core.credentials import AzureKeyCredential

client = load_client(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)

print(f"Created client of type `{type(client).__name__}`.")
```

To load an asynchronous client, import the `load_client` function from `azure.ai.inference.aio` instead.

Entra ID authentication is also supported by the `load_client` function. Replace the key authentication above with `credential=DefaultAzureCredential()` for example.

### Get AI model information

All clients provide a `get_model_info` method to retrive AI model information. This makes a REST call to the `/info` route on the provided endpoint, as documented in [the REST API reference](https://learn.microsoft.com/azure/ai-studio/reference/reference-model-inference-info).

<!-- SNIPPET:sample_get_model_info.get_model_info -->

```python
model_info = client.get_model_info()

print(f"Model name: {model_info.model_name}")
print(f"Model provider name: {model_info.model_provider_name}")
print(f"Model type: {model_info.model_type}")
```

<!-- END SNIPPET -->

AI model information is cached in the client, and futher calls to `get_model_info` will access the cached value and wil not result in a REST API call. Note that if you created the client using `load_client` function, model information will already be cached in the client.

AI model information is displayed (if available) when you `print(client)`.

### Chat Completions

The `ChatCompletionsClient` has a method named `complete`. The method makes a REST API call to the `/chat/completions` route on the provided endpoint, as documented in [the REST API reference](https://learn.microsoft.com/azure/ai-studio/reference/reference-model-inference-chat-completions).

See simple chat completion examples below. More can be found in the [samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-inference/samples) folder.

### Text Embeddings

The `EmbeddingsClient` has a method named `embedding`. The method makes a REST API call to the `/embeddings` route on the provided endpoint, as documented in [the REST API reference](https://learn.microsoft.com/azure/ai-studio/reference/reference-model-inference-embeddings).

See simple text embedding example below. More can be found in the [samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-inference/samples) folder.

<!-- 
### Image Embeddings

TODO: Add overview and link to explain image embeddings.

Embeddings operations target the URL route `images/embeddings` on the provided endpoint.
-->

### Inference using Azure OpenAI endpoints

The request and response payloads of the [Azure AI Model Inference API](https://learn.microsoft.com/azure/ai-studio/reference/reference-model-inference-api) is mostly compatible with OpenAI REST APIs for chat completions and text embeddings. Therefore, with some minor adjustments, this client library can be configured to do inference using Azure OpenAI endpoints. See samples with `azure_openai` in their name, in the [samples folder](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-inference/samples), and the comments there.

## Examples

In the following sections you will find simple examples of:

* [Chat completions](#chat-completions-example)
* [Streaming chat completions](#streaming-chat-completions-example)
* [Chat completions with additional model-specific parameters](#chat-completions-with-additional-model-specific-parameters)
* [Text Embeddings](#text-embeddings-example)
<!-- * [Image Embeddings](#image-embeddings-example) -->

The examples create a synchronous client as mentioned in [Create and authenticate a client directly, using key](#create-and-authenticate-a-client-directly-using-key). Only mandatory input settings are shown for simplicity.

See the [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-inference/samples) folder for full working samples for synchronous and asynchronous clients.

### Chat completions example

This example demonstrates how to generate a single chat completions, with key authentication, assuming `endpoint` and `key` are already defined.

<!-- SNIPPET:sample_chat_completions.chat_completions -->

```python
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

response = client.complete(
    messages=[
        SystemMessage(content="You are a helpful assistant."),
        UserMessage(content="How many feet are in a mile?"),
    ]
)

print(response.choices[0].message.content)
```

<!-- END SNIPPET -->

The following types or messages are supported: `SystemMessage`,`UserMessage`, `AssistantMessage`, `ToolMessage`. See also samples:

* [sample_chat_completions_with_tools.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_chat_completions_with_tools.py) for usage of `ToolMessage`. 
* [sample_chat_completions_with_image_url.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_chat_completions_with_image_url.py) for usage of `UserMessage` that
includes sending an image URL.
* [sample_chat_completions_with_image_data.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_chat_completions_with_image_data.py) for usage of `UserMessage` that
includes sending image data read from a local file.

Alternatively, you can provide the messages as dictionary instead of using the strongly typed classes like `SystemMessage` and `UserMessage`:

<!-- SNIPPET:sample_chat_completions_from_input_json.chat_completions -->

```python
response = client.complete(
    {
        "messages": [
            {
                "role": "system",
                "content": "You are an AI assistant that helps people find information. Your replies are short, no more than two sentences.",
            },
            {
                "role": "user",
                "content": "What year was construction of the International Space Station mostly done?",
            },
            {
                "role": "assistant",
                "content": "The main construction of the International Space Station (ISS) was completed between 1998 and 2011. During this period, more than 30 flights by US space shuttles and 40 by Russian rockets were conducted to transport components and modules to the station.",
            },
            {
                "role": "user",
                "content": "And what was the estimated cost to build it?"
            },
        ]
    }
)
```

<!-- END SNIPPET -->

To generate completions for additional messages, simply call `client.complete` multiple times using the same `client`.

### Streaming chat completions example

This example demonstrates how to generate a single chat completions with streaming response, with key authentication, assuming `endpoint` and `key` are already defined. You need to add `stream=True` to the `complete` call to enable streaming.

<!-- SNIPPET:sample_chat_completions_streaming.chat_completions_streaming -->

```python
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

response = client.complete(
    stream=True,
    messages=[
        SystemMessage(content="You are a helpful assistant."),
        UserMessage(content="Give me 5 good reasons why I should exercise every day."),
    ],
)

for update in response:
    print(update.choices[0].delta.content or "", end="")

client.close()
```

<!-- END SNIPPET -->

In the above `for` loop that prints the results you should see the answer progressively get longer as updates get streamed to the client.

To generate completions for additional messages, simply call `client.complete` multiple times using the same `client`.

### Chat completions with additional model-specific parameters

In this example, extra JSON elements are inserted at the root of the request body by setting `model_extras` when calling the `complete` method. These are intended for AI models that require additional model-specific parameters beyond what is defined in the REST API [Request Body table](https://learn.microsoft.com/azure/ai-studio/reference/reference-model-inference-chat-completions#request-body).

<!-- SNIPPET:sample_chat_completions_with_model_extras.model_extras -->

```python
response = client.complete(
    messages=[
        SystemMessage(content="You are a helpful assistant."),
        UserMessage(content="How many feet are in a mile?"),
    ],
    model_extras={"key1": "value1", "key2": "value2"},  # Optional. Additional parameters to pass to the model.
)
```

<!-- END SNIPPET -->
In the above example, this will be the JSON payload in the HTTP request:

```json
{
    "messages":
    [
        {"role":"system","content":"You are a helpful assistant."},
        {"role":"user","content":"How many feet are in a mile?"}
    ],
    "key1": "value1",
    "key2": "value2"
}
```

Note that by default, the service will reject any request payload that includes extra parameters. In order to change the default service behaviour, when the `complete` method includes `model_extras`, the client library will automatically add the HTTP request header `"extra-parameters": "pass-through"`.

### Text Embeddings example

This example demonstrates how to get text embeddings, with key authentication, assuming `endpoint` and `key` are already defined.

<!-- SNIPPET:sample_embeddings.embeddings -->

```python
from azure.ai.inference import EmbeddingsClient
from azure.core.credentials import AzureKeyCredential

client = EmbeddingsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

response = client.embed(input=["first phrase", "second phrase", "third phrase"])

for item in response.data:
    length = len(item.embedding)
    print(
        f"data[{item.index}]: length={length}, [{item.embedding[0]}, {item.embedding[1]}, "
        f"..., {item.embedding[length-2]}, {item.embedding[length-1]}]"
    )
```

<!-- END SNIPPET -->

The length of the embedding vector depends on the model, but you should see something like this:

```text
data[0]: length=1024, [0.0013399124, -0.01576233, ..., 0.007843018, 0.000238657]
data[1]: length=1024, [0.036590576, -0.0059547424, ..., 0.011405945, 0.004863739]
data[2]: length=1024, [0.04196167, 0.029083252, ..., -0.0027484894, 0.0073127747]
```

To generate embeddings for additional phrases, simply call `client.embed` multiple times using the same `client`.

<!--
### Image Embeddings example

This example demonstrates how to get image embeddings.

 <! -- SNIPPET:sample_image_embeddings.image_embeddings -- >

```python
from azure.ai.inference import ImageEmbeddingsClient
from azure.ai.inference.models import EmbeddingInput
from azure.core.credentials import AzureKeyCredential

with open("sample1.png", "rb") as f:
    image1: str = base64.b64encode(f.read()).decode("utf-8")
with open("sample2.png", "rb") as f:
    image2: str = base64.b64encode(f.read()).decode("utf-8")

client = ImageEmbeddingsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

response = client.embed(input=[EmbeddingInput(image=image1), EmbeddingInput(image=image2)])

for item in response.data:
    length = len(item.embedding)
    print(
        f"data[{item.index}]: length={length}, [{item.embedding[0]}, {item.embedding[1]}, "
        f"..., {item.embedding[length-2]}, {item.embedding[length-1]}]"
    )
```

-- END SNIPPET --

The printed result of course depends on the model, but you should see something like this:

```txt
TBD
```

To generate embeddings for additional phrases, simply call `client.embed` multiple times using the same `client`.
-->

## Troubleshooting

### Exceptions

The `complete`, `embed` and `get_model_info` methods on the clients raise an [HttpResponseError](https://learn.microsoft.com/python/api/azure-core/azure.core.exceptions.httpresponseerror) exception for a non-success HTTP status code response from the service. The exception's `status_code` will hold the HTTP response status code (with `reason` showing the friendly name). The exception's `error.message` contains a detailed message that may be helpful in diagnosing the issue:

```python
from azure.core.exceptions import HttpResponseError

...

try:
    result = client.complete( ... )
except HttpResponseError as e:
    print(f"Status code: {e.status_code} ({e.reason})")
    print(e.message)
```

For example, when you provide a wrong authentication key:

```text
Status code: 401 (Unauthorized)
Operation returned an invalid status 'Unauthorized'
```

Or when you create an `EmbeddingsClient` and call `embed` on the client, but the endpoint does not
support the `/embeddings` route:

```text
Status code: 405 (Method Not Allowed)
Operation returned an invalid status 'Method Not Allowed'
```

### Logging

The client uses the standard [Python logging library](https://docs.python.org/3/library/logging.html). The SDK logs HTTP request and response details, which may be useful in troubleshooting. To log to stdout, add the following:

```python
import sys
import logging

# Acquire the logger for this client library. Use 'azure' to affect both
# 'azure.core` and `azure.ai.inference' libraries.
logger = logging.getLogger("azure")

# Set the desired logging level. logging.INFO or logging.DEBUG are good options.
logger.setLevel(logging.DEBUG)

# Direct logging output to stdout:
handler = logging.StreamHandler(stream=sys.stdout)
# Or direct logging output to a file:
# handler = logging.FileHandler(filename="sample.log")
logger.addHandler(handler)

# Optional: change the default logging format. Here we add a timestamp.
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s")
handler.setFormatter(formatter)
```

By default logs redact the values of URL query strings, the values of some HTTP request and response headers (including `Authorization` which holds the key or token), and the request and response payloads. To create logs without redaction, do these two things:

1. Set the method argument `logging_enable = True` when you construct the client library, or when you call the client's `complete` or `embed`  methods.
    ```python
    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
        logging_enable=True
    )
    ```
1. Set the log level to `logging.DEBUG`. Logs will be redacted with any other log level.

Be sure to protect non redacted logs to avoid compromising security.

For more information, see [Configure logging in the Azure libraries for Python](https://aka.ms/azsdk/python/logging)

### Reporting issues

To report issues with the client library, or request additional features, please open a GitHub issue [here](https://github.com/Azure/azure-sdk-for-python/issues)

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
