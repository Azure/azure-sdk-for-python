
# Samples for Azure Web PubSub client library for Python

These code samples show common scenario operations with the Azure Web PubSub client library.
The async versions of the samples require Python 3.6 or later.

You can authenticate your client with API key or through Azure Active Directory with a token credential from [azure-identity][azure_identity], there is introduction in [README.md][readme]  
about the authentication knowledge. These sample programs show common scenarios:

|**File Name**|**Description**|
|----------------|-------------|
|[send_message_aad.py][send_message_aad] |Send message through AAD authentication|
|[send_messages_aad_apim_proxy.py][send_messages_aad_apim_proxy] |Send message through AAD authentication with Api management proxy|
|[send_messages_connection_string.py][send_messages_connection_string] |Send message through connection string authentication|
|[send_messages_connection_string_apim_proxy.py][send_messages_connection_string_apim_proxy] |Send message through connection string authentication with Api management proxy|

## Prerequisites
* Python 2.7, or 3.6 or later is required to use this package (3.6 or later if using asyncio)
* You must have an [Azure Web PubSub account][azure_web_pubsub_account] to run these samples.
## Setup

1. Install the Azure Web PubSub client library for Python with [pip][pip]:

```bash
pip install azure-messaging-webpubsub
```

* If authenticating with Azure Active Directory, make sure you have [azure-identity][azure_identity_pip] installed:
  ```bash
  pip install azure-identity
  ```

2. Clone or download this sample repository

3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python send_message_aad.py`

[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
[readme]: ../README.md
[pip]: https://pypi.org/project/pip/
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[send_message_aad]: send_messages_aad.py
[send_messages_aad_apim_proxy]: send_messages_aad_apim_proxy.py
[send_messages_connection_string]: send_messages_connection_string.py
[send_messages_connection_string_apim_proxy]: send_messages_connection_string_apim_proxy.py
[azure_web_pubsub_account]: https://docs.microsoft.com/azure/azure-web-pubsub/howto-develop-create-instance