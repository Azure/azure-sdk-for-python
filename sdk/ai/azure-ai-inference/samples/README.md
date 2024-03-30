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

These are runnable console Python programs that show how to do chat completion using the model client. Most samples are in this folder
and use the a synchronous client. Samples in the subfolder `async_samples` use the asynchronous client.
The concepts are similar, you can easily modify any of the samples to your needs.

## Synchronous client samples

|**File Name**|**Description**|
|----------------|-------------|
|[sample_chat_completions.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_chat_completions.py) | One chat completion operation using a synchronous client. |
|[sample_embeddings.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/sample_embeddings.py) | One embeddings operation using a synchronous client. |

## Asynchronous client samples

|**File Name**|**Description**|
|----------------|-------------|
|[sample_chat_completions_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/async_samples/sample_chat_completions_async.py) | One chat completion operation using an asynchronous client. |
|[sample_embeddings_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/async_samples/sample_embeddings_async.py) | One embeddings operation using an asynchronous client. |

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

See [Set environment variables](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/README.md#set-environment-variables) here.

## Running the samples

To run the first sample, type:
```bash
python sample_chat_completion_async.py
```
similarly for the other samples.

## Example console output

The sample `sample_chat_completion_async.py` sends the following system and user messages in a single call:

- System: "You are an AI assistant that helps people find information."
- User: "How many feet are in a mile?"

And prints out the service response. It should look similar to the following:

```text
Chat Completions:
choices[0].message.content:   There are 5,280 feet in a mile.
choices[0].message.role: assistant
choices[0].finish_reason: stop
choices[0].index: 0
id: 93f5bea2-11ec-4b31-af73-cb663196ebd5
created: 1970-01-14 01:11:54+00:00
model: Llama-2-70b-chat
object: chat.completion
usage.prompt_tokens: 41
usage.completion_tokens: 15
usage.total_tokens: 56
```

## Troubleshooting

See [Troubleshooting](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/README.md#troubleshooting) here.


