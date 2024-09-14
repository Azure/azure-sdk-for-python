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

To run any of the samples, type the following command with the respective sample script:

```bash
python <sample_script_name>.py
```

For example, to run the assistant basics sample, you would type:
```bash
python sample_assistant_basics.py
```

Here is the list of available samples:

- `sample_assistant_basics.py`
- `sample_assistant_code_interpreter.py`
- `sample_assistant_file_search.py`
- `sample_assistant_functions.py`
- `sample_assistant_run_with_toolset.py`
- `sample_assistant_stream_iteration.py`

## Samples

## Troubleshooting

See [Troubleshooting](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-assistants/README.md#troubleshooting) here.