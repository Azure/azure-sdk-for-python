---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-ai
urlFragment: model-assistants-samples
---

# Samples for Azure AI Assistants client library for Python

Samples in this folder use the a synchronous clients. Samples in the subfolder `async_samples` use the asynchronous clients. The concepts are similar, you can easily modify any of the synchronous samples to asynchronous.

## Prerequisites

See [Prerequisites](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-assistants/README.md#prerequisites) here.

## Setup

* Clone or download this sample repository
* Open a command prompt / terminal window in this samples folder
* Install the client library for Python with pip:
  ```bash
  pip install azure-ai-assistants
  ```
  or update an existing installation:
  ```bash
  pip install --upgrade azure-ai-assistants
  ```
* If you plan to run the asynchronous client samples, insall the additional package [aiohttp](https://pypi.org/project/aiohttp/):
  ```bash
  pip install aiohttp
  ```

## Set environment variables

To construct any of the clients, you will need to pass in the endpoint URL. If you are using key authentication, you also need to pass in the key associated with your deployed AI model.

## Azure OpenAI endpoints

## Running the samples

To run the first sample, type:

```bash
python sample_chat_completions.py
```

similarly for the other samples.

## Samples

## Troubleshooting

See [Troubleshooting](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-assistants/README.md#troubleshooting) here.
