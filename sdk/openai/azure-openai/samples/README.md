---
page_type: sample
languages:
  - python
products:
  - azure-openai
urlFragment: openai-samples
---

# Samples for OpenAI client library for Python

These code samples show common scenario operations calling to Azure OpenAI.

You can authenticate your client with an API key or through Microsoft Entra ID with a token credential from [azure-identity][azure_identity].

These sample programs show common scenarios for using Azure OpenAI offerings.

|**File Name**|**Description**|
|----------------|-------------|
|[chat_completions_aoai_quickstart.py][chat_completions_aoai_quickstart]|Use Chat Completions with Azure OpenAI|
|[chat_completions_oyd.py][chat_completions_oyd]|Use Chat Completions with Azure OpenAI on your data|

## Prerequisites

* Python 3.8 or greater
* You must have an [Azure subscription][azure_subscription] and
* Access granted to Azure OpenAI in the desired Azure subscription
  Currently, access to this service is granted only by application. You can apply for access to Azure OpenAI by completing the form at <https://aka.ms/oai/access>.
* An Azure OpenAI Service resource with either the `gpt-35-turbo` or the `gpt-4` models deployed. For more information about model deployment, see the [resource deployment guide][aoai-resource_deployment].

## Setup

1. Install the OpenAI client library for Python with [pip][pip]:

```bash
pip install openai
```

> [!NOTE]
> This library is maintained by OpenAI. Refer to the [release history][versioning_history] to track the latest updates to the library.

* If authenticating with Azure Active Directory, make sure you have [azure-identity][azure_identity_pip] installed:

  ```bash
  pip install azure-identity
  ```

2. Clone the repo or download the sample file
3. Open the sample file in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python chat_completions_oyd.py`

## Next steps

Check out [Azure OpenAI samples][aoai_samples] to learn more about
what you can do with Azure OpenAI.

[versioning_history]: https://github.com/openai/openai-python/releases
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
[chat_completions_aoai_quickstart]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/openai/azure-openai/samples/chat_completions_aoai_quickstart.py
[chat_completions_oyd]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/openai/azure-openai/samples/chat_completions_oyd.py
[pip]: https://pypi.org/project/pip/
[azure_subscription]: https://azure.microsoft.com/free/
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[aoai_samples]: https://aka.ms/azai
[aoai-resource_deployment]: https://learn.microsoft.com/azure/ai-services/openai/how-to/create-resource
