---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-ai
urlFragment: model-inference-samples
---

# Samples for Azure AI Inference client library for Python

These are runnable console Python scripts that show how to do chat completion and text embeddings against Serverless API endpoints and Managed Compute endpoints.

Samples with `azure_openai` in their name show how to do chat completions and text embeddings against Azure OpenAI endpoints.

Samples in this folder use the a synchronous clients. Samples in the subfolder `async_samples` use the asynchronous clients. The concepts are similar, you can easily modify any of the synchronous samples to asynchronous.

## Prerequisites

See [Prerequisites](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/README.md#prerequisites) here.

## Setup

* Clone or download this sample repository
* Open a command prompt / terminal window in this samples folder
* Install the client library for Python with pip:
  ```bash
  pip install azure-ai-inference
  ```
  or update an existing installation:
  ```bash
  pip install --upgrade azure-ai-inference
  ```
* If you plan to run the asynchronous client samples, insall the additional package [aiohttp](https://pypi.org/project/aiohttp/):
  ```bash
  pip install aiohttp
  ```

## Set environment variables

To construct any of the clients, you will need to pass in the endpoint URL. If you are using key authentication, you also need to pass in the key associated with your deployed AI model.

* For Serverless API and Managed Compute endpoints, the endpoint URL has the form `https://your-unique-resouce-name.your-azure-region.models.ai.azure.com`, where `your-unique-resource-name` is your globally unique Azure resource name and `your-azure-region` is the Azure region where the model is deployed (e.g. `eastus2`).

* For Azure OpenAI endpoints, the endpoint URL has the form `https://your-unique-resouce-name.openai.azure.com/openai/deployments/your-deployment-name`, where `your-unique-resource-name` is your globally unique Azure OpenAI resource name, and `your-deployment-name` is your AI Model deployment name.

* The key is a 32-character string.

For convenience, and to promote the practice of not hard-coding secrets in your source code, all samples here assume the endpoint URL and key are stored in environment variables. You will need to set these environment variables before running the samples as-is. The environment variables are mentioned in the tables below.

Note that the client library does not directly read these environment variable at run time. The sample code reads the environment variables and constructs the relevant client with these values.

## Serverless API and Managed Compute endpoints

| Sample type | Endpoint environment variable name | Key environment variable name  |
|----------|----------|----------|
| Chat completions | `AZURE_AI_CHAT_ENDPOINT` | `AZURE_AI_CHAT_KEY` |
| Embeddings | `AZURE_AI_EMBEDDINGS_ENDPOINT` | `AZURE_AI_EMBEDDINGS_KEY` |
<!--
| Image generation | `IMAGE_GENERATION_ENDPOINT` | `IMAGE_GENERATION_KEY` |
-->

To run against a Managed Compute Endpoint, some samples also have an optional environment variable `AZURE_AI_CHAT_DEPLOYMENT_NAME`. This is the value used to set the HTTP request header `azureml-model-deployment` when constructing the client.

## Azure OpenAI endpoints

| Sample type | Endpoint environment variable name | Key environment variable name  |
|----------|----------|----------|
| Chat completions | `AZURE_OPENAI_CHAT_ENDPOINT` | `AZURE_OPENAI_CHAT_KEY` |
| Embeddings | `AZURE_OPENAI_EMBEDDINGS_ENDPOINT` | `AZURE_OPENAI_EMBEDDINGS_KEY` |
<!--
| Image generation | `IMAGE_GENERATION_ENDPOINT` | `IMAGE_GENERATION_KEY` |
-->

## Running the samples

To run the first sample, type:

```bash
python sample_chat_completions.py
```

similarly for the other samples.

## Synchronous client samples

### Chat completions

|**File Name**|**Description**|
|----------------|-------------|
|[sample_chat_completions_streaming.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_chat_completions_streaming.py) | One chat completion operation using a synchronous client and streaming response. |
|[sample_chat_completions_streaming_with_entra_id_auth.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_chat_completions_streaming_with_entra_id_auth.py) | One chat completion operation using a synchronous client and streaming response, using Entra ID authentication. This sample also shows setting the `azureml-model-deployment` HTTP request header, which may be required for some Managed Compute endpoint. |
|[sample_chat_completions.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_chat_completions.py) | One chat completion operation using a synchronous client. |
|[sample_chat_completions_with_defaults.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_chat_completions_with_defaults.py) | One chat completion operation using a synchronous client, with default chat completions configuration set in the client constructor. |
|[sample_chat_completions_with_image_url.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_chat_completions_with_image_url.py) | One chat completion operation using a synchronous client, which includes sending an input image URL. |
|[sample_chat_completions_with_image_data.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_chat_completions_with_image_data.py) | One chat completion operation using a synchronous client, which includes sending input image data read from a local file. |
|[sample_chat_completions_with_history.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_chat_completions_with_history.py) | Two chat completion operations using a synchronous client, with the second completion using chat history from the first. |
|[sample_chat_completions_from_input_bytes.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_chat_completions_from_input_bytes.py) | One chat completion operation using a synchronous client, with input messages provided as `IO[bytes]`. |
|[sample_chat_completions_from_input_json.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_chat_completions_from_input_json.py) | One chat completion operation using a synchronous client, with input messages provided as a dictionary (type `MutableMapping[str, Any]`) |
|[sample_chat_completions_from_input_json_with_image_url.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_chat_completions_from_input_json_with_image_url.py) | One chat completion operation using a synchronous client, with input messages provided as a dictionary (type `MutableMapping[str, Any]`). Includes sending an input image URL. |
|[sample_chat_completions_with_tools.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_chat_completions_with_tools.py) | Shows how do use a tool (function) in chat completions, for an AI model that supports tools |
|[sample_chat_completions_streaming_with_tools.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_chat_completions_streaming_with_tools.py) | Shows how do use a tool (function) in chat completions, with streaming response, for an AI model that supports tools |
|[sample_load_client.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_load_client.py) | Shows how do use the function `load_client` to create the appropriate synchronous client based on the provided endpoint URL. In this example, it creates a synchronous `ChatCompletionsClient`. |
|[sample_get_model_info.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_get_model_info.py) | Get AI model information using the chat completions client. Similarly can be done with all other clients. |
|[sample_chat_completions_with_model_extras.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_chat_completions_with_model_extras.py) | Chat completions with additional model-specific parameters. |
|[sample_chat_completions_azure_openai.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_chat_completions_azure_openai.py) | Chat completions against Azure OpenAI endpoint. |

### Text embeddings

|**File Name**|**Description**|
|----------------|-------------|
|[sample_embeddings.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_embeddings.py) | One embeddings operation using a synchronous client. The resulting embeddings format is a list of floating point values (the default format) |
|[sample_embeddings_with_base64_encoding.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_embeddings_with_base64_encoding.py) | One embeddings operation using a synchronous client. The resulting embeddings format is a base64 encoded string. |
|[sample_embeddings_with_defaults.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_embeddings_with_defaults.py) | One embeddings operation using a synchronous client, with default embeddings configuration set in the client constructor. |
|[sample_embeddings_azure_openai.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_embeddings_azure_openai.py) | One embeddings operation using a synchronous client, against Azure OpenAI endpoint. |

<!--
### Image embeddings

|**File Name**|**Description**|
|----------------|-------------|
|[sample_image_embeddings.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_image_embeddings.py) | One image embeddings operation, on two input images, using a synchronous client. |
-->

## Asynchronous client samples

### Chat completions

|**File Name**|**Description**|
|----------------|-------------|
|[sample_chat_completions_streaming_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/async_samples/sample_chat_completions_streaming_async.py) | One chat completion operation using an asynchronous client and streaming response. |
|[sample_chat_completions_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/async_samples/sample_chat_completions_async.py) | One chat completion operation using an asynchronous client. |
|[sample_load_client_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/async_samples/sample_load_client_async.py) | Shows how do use the function `load_client` to create the appropriate asynchronous client based on the provided endpoint URL. In this example, it creates an asynchronous `ChatCompletionsClient`. |
|[sample_chat_completions_from_input_bytes_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/async_samples/sample_chat_completions_from_input_bytes_async.py) | One chat completion operation using an asynchronous client, with input messages provided as `IO[bytes]`. |
|[sample_chat_completions_from_input_json_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/async_samples/sample_chat_completions_from_input_json_async.py) | One chat completion operation using an asynchronous client, with input messages provided as a dictionary (type `MutableMapping[str, Any]`) |
|[sample_chat_completions_streaming_azure_openai_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/async_samples/sample_chat_completions_streaming_azure_openai_async.py) | One chat completion operation using an asynchronous client and streaming response against an Azure OpenAI endpoint |

### Text embeddings

|**File Name**|**Description**|
|----------------|-------------|
|[sample_embeddings_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/async_samples/sample_embeddings_async.py) | One embeddings operation using an asynchronous client. |

<!--
### Image embeddings

|**File Name**|**Description**|
|----------------|-------------|
|[sample_image_embeddings_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/async_samples/sample_image_embeddings_async.py) | One image embeddings operation, on two input images, using an asynchronous client. |
-->

## Troubleshooting

See [Troubleshooting](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/README.md#troubleshooting) here.
