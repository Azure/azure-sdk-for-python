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

Samples in this folder use the synchronous clients. Samples in the subfolder `async_samples` use the asynchronous clients. The concepts are similar, you can easily modify any of the synchronous samples to asynchronous.

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

- `sample_assistant_basics.py`: This sample demonstrates how to use basic assistant operations from the Azure Assistants service using a synchronous client. It includes creating an assistant, sending messages, processing runs, and polling for the completion status.
- `sample_assistant_code_interpreter.py`: This sample shows how to use the Azure AI Assistants client for interpreting and processing code. It demonstrates uploading a file, creating a code interpreter tool, and generating charts based on data analysis.
- `sample_assistant_file_search.py`: This sample demonstrates how to use the Assistants client for file search and processing. It includes uploading a file, creating a vector store, and querying information about specific content present in the files.
- `sample_assistant_functions.py`: This sample showcases how to enhance assistant operations with user-defined functions. It covers creating an assistant with function tools, processing function calls, and handling tool outputs.
- `sample_assistant_run_with_toolset.py`: This sample illustrates how to use multiple tools in a single run of the Assistants client. It includes creating an assistant with various tools such as function tools and code interpreter tools, and managing threaded communication.
- `sample_assistant_stream_iteration.py`: This sample demonstrates how to use the streaming capabilities of the Azure Assistants service. It covers creating an assistant, sending messages, and handling streaming events to process responses in real time.

## Samples

## Troubleshooting

See [Troubleshooting](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-assistants/README.md#troubleshooting) here.