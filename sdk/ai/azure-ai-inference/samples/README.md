---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-ai
urlFragment: model-inference-samples
---

# Samples for the model client library for Python

These are runnable console Python programs that show how to do chat completion, embeddings and image geneartion using the clients in this package. Samples are in this folder
and use the a synchronous client. Samples in the subfolder `async_samples` use the asynchronous client.
The concepts are similar, you can easily modify any of the samples to your needs.

## Synchronous client samples

|**File Name**|**Description**|
|----------------|-------------|
|[sample_chat_completions_streaming.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_chat_completions_streaming.py) | One chat completion operation using a synchronous client and streaming response. |
|[sample_chat_completions.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_chat_completions.py) | One chat completion operation using a synchronous client. |
|[sample_embeddings.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_embeddings.py) | One embeddings operation using a synchronous client. |
|[sample_image_generation.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_image_generation.py) | Generate an image from a prompt using a synchronous client. |

## Asynchronous client samples

|**File Name**|**Description**|
|----------------|-------------|
|[sample_chat_completions_streaming_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/async_samples/sample_chat_completions_streaming_async.py) | One chat completion operation using an asynchronous client and streaming response. |
|[sample_chat_completions_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/async_samples/sample_chat_completions_async.py) | One chat completion operation using an asynchronous client. |
|[sample_embeddings_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/async_samples/sample_embeddings_async.py) | One embeddings operation using an asynchronous client. |
|[sample_image_generation_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/async_samples/sample_image_generation_async.py) | Generate an image from a prompt using an asynchronous client. |

## Prerequisites

See [Prerequisites](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/README.md#prerequisites) here.

## Setup

* Clone or download this sample repository
* Open a command prompt / terminal window in this samples folder
* Install the Image Analysis client library for Python with pip:
  ```bash
  pip install azure-ai-inference
  ```
* If you plan to run the asynchronous client samples, insall the additional package [aiohttp](https://pypi.org/project/aiohttp/):
  ```bash
  pip install aiohttp
  ```

## Set environment variables

To construct any of the clients, you will need to pass in the endpoint URL and key associated with your deployed AI model.

* The endpoint URL has the form `https://your-deployment-name.your-azure-region.inference.ai.azure.com`, where `your-deployment-name` is your unique model deployment name and `your-azure-region` is the Azure region where the model is deployed (e.g. `eastus2`).

* The key is a 32-character string.

For convenience, and to promote the practice of not hard-coding secrets in your source code, all samples here assume the endpoint URL and key are stored in environment variables. You will need to set these environment variables before running the samples as-is. These are the environment variables used:

| Sample type | Endpoint environment variable name | Key environment variable name  |
|----------|----------|----------|
| Chat completions | `CHAT_COMPLETIONS_ENDPOINT` | `CHAT_COMPLETIONS_KEY` |
| Embeddings | `EMBEDDINGS_ENDPOINT` | `EMBEDDINGS_KEY` |
| Image generation | `IMAGE_GENERATION_ENDPOINT` | `IMAGE_GENERATION_KEY` |

Note that the client library does not directly read these environment variable at run time. The sample code reads the environment variables and constructs the relevant client with these values.

## Running the samples

To run the first sample, type:
```bash
python sample_chat_completions.py
```
similarly for the other samples.

## Troubleshooting

See [Troubleshooting](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/README.md#troubleshooting) here.


