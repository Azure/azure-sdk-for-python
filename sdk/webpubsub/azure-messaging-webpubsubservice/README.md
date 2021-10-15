# Azure WebPubSubService client library for Python

[Azure Web PubSub Service](https://aka.ms/awps/doc) is a service that enables you to build real-time messaging web applications using WebSockets and the publish-subscribe pattern. Any platform supporting WebSocket APIs can connect to the service easily, e.g. web pages, mobile applications, edge devices, etc. The service manages the WebSocket connections for you and allows up to 100K concurrent connections. It provides powerful APIs for you to manage these clients and deliver real-time messages.

Any scenario that requires real-time publish-subscribe messaging between server and clients or among clients, can use Azure Web PubSub service. Traditional real-time features that often require polling from server or submitting HTTP requests, can also use Azure Web PubSub service.

We list some examples that are good to use Azure Web PubSub service:

- **High frequency data updates:** gaming, voting, polling, auction.
- **Live dashboards and monitoring:** company dashboard, financial market data, instant sales update, multi-player game leader board, and IoT monitoring.
- **Cross-platform live chat:** live chat room, chat bot, on-line customer support, real-time shopping assistant, messenger, in-game chat, and so on.
- **Real-time location on map:** logistic tracking, delivery status tracking, transportation status updates, GPS apps.
- **Real-time targeted ads:** personalized real-time push ads and offers, interactive ads.
- **Collaborative apps:** coauthoring, whiteboard apps and team meeting software.
- **Push instant notifications:** social network, email, game, travel alert.
- **Real-time broadcasting:** live audio/video broadcasting, live captioning, translating, events/news broadcasting.
- **IoT and connected devices:** real-time IoT metrics, remote control, real-time status, and location tracking.
- **Automation:** real-time trigger from upstream events.

Use the client library to:

- Send messages to hubs and groups.
- Send messages to particular users and connections.
- Organize users and connections into groups.
- Close connections
- Grant/revoke/check permissions for an existing connection

[Source code](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubservice) | [Package (Pypi)][package] | [API reference documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubservice) | [Product documentation][webpubsubservice_docs]

## Getting started

### Installating the package

```bash
python -m pip install azure-messaging-webpubsubservice
```

#### Prequisites

- Python 2.7, or 3.6 or later is required to use this package.
- You need an [Azure subscription][azure_sub], and a [Azure WebPubSub service instance][webpubsubservice_docs] to use this package.
- An existing Azure Web PubSub service instance.

### Authenticating the client

#### 1. Create the client from the service connection string

You can get the [API key][api_key] or [Connection string][connection_string] in the [Azure Portal][azure_portal].
Once you have the value for the API key, you can pass it as a string into an instance of [AzureKeyCredential][azure-key-credential]. 
Use the key as the credential parameter to authenticate the client:

```python
>>> from azure.messaging.webpubsubservice import WebPubSubServiceClient
>>> from azure.core.credentials import AzureKeyCredential

>>> client = WebPubSubServiceClient(endpoint='<endpoint>', credential=AzureKeyCredential("<api_key>"))
```

Once you have the value for the connection string, you can pass it as a string into the function `from_connection_string` and it will 
authenticate the client:
```python
>>> from azure.messaging.webpubsubservice import WebPubSubServiceClient

>>> client = WebPubSubServiceClient.from_connection_string(connection_string='<connection_string>')
```

#### 2. Create with an Azure Active Directory Credential
To use an [Azure Active Directory (AAD) token credential][authenticate_with_token],
provide an instance of the desired credential type obtained from the
[azure-identity][azure_identity_credentials] library.

To authenticate with AAD, you must first [pip][pip] install [`azure-identity`][azure_identity_pip] and
[enable AAD authentication on your Webpubsub resource][enable_aad]

After setup, you can choose which type of [credential][azure_identity_credentials] from azure.identity to use.
As an example, [DefaultAzureCredential][default_azure_credential]
can be used to authenticate the client:

Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET

Use the returned token credential to authenticate the client:

```python
>>> from azure.messaging.webpubsubservice import WebPubSubServiceClient
>>> from azure.identity import DefaultAzureCredential
>>> client = WebPubSubServiceClient(endpoint='<endpoint>', credential=DefaultAzureCredential())
```

## Examples

### Broadcast messages 

```python
>>> from azure.messaging.webpubsubservice import WebPubSubServiceClient
>>> from azure.identity import DefaultAzureCredential
>>> from azure.core.exceptions import HttpResponseError

>>> client = WebPubSubServiceClient(endpoint='<endpoint>', credential=DefaultAzureCredential())
>>> with open('file.json', 'r') as f:
    try:
        client.send_to_all('ahub', content=f, content_type='application/json')
    except HttpResponseError as e:
        print('service responds error: {}'.format(e.response.json()))

```

## Key concepts

### Connection

Connections, represented by a connection id, represent an individual websocket connection to the Web PubSub service. Connection id is always unique.

### Hub

Hub is a logical concept for a set of connections. Connections are always connected to a specific hub. Messages that are broadcast to the hub are dispatched to all connections to that hub. Hub can be used for different applications, different applications can share one Azure Web PubSub service by using different hub names.

### Group

Group allow broadcast messages to a subset of connections to the hub. You can add and remove users and connections as needed. A client can join multiple groups, and a group can contain multiple clients.

### User

Connections to Web PubSub can belong to one user. A user might have multiple connections, for example when a single user is connected across multiple devices or multiple browser tabs.

### Message

Using this library, you can send messages to the client connections. A message can either be string text, JSON or binary payload.

## Troubleshooting

### Logging

This SDK uses Python standard logging library.
You can configure logging print out debugging information to the stdout or anywhere you want.

```python
import sys
import logging
from azure.identity import DefaultAzureCredential
>>> from azure.messaging.webpubsubservice import WebPubSubServiceClient

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

endpoint = "<endpoint>"
credential = DefaultAzureCredential()

# This client will log detailed information about its HTTP sessions, at DEBUG level
client = WebPubSubServiceClient(endpoint=endpoint, credential=credential, logging_enable=True)
```

Similarly, `logging_enable` can enable detailed logging for a single call,
even when it isn't enabled for the client:

```python
result = client.send_to_all(..., logging_enable=True)
```

Http request and response details are printed to stdout with this logging config.

## Next steps

More examples are coming soon...

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact opencode@microsoft.com with any
additional questions or comments.

<!-- LINKS -->
[webpubsubservice_docs]: https://aka.ms/awps/doc
[azure_cli]: https://docs.microsoft.com/cli/azure
[azure_sub]: https://azure.microsoft.com/free/
[package]: https://pypi.org/project/azure-messaging-webpubsubservice/
[default_cred_ref]: https://aka.ms/azsdk-python-identity-default-cred-ref
[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
[authenticate_with_token]: https://docs.microsoft.com/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-an-authentication-token
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[pip]: https://pypi.org/project/pip/
[enable_aad]: https://docs.microsoft.com/azure/azure-web-pubsub/howto-develop-create-instance
[api_key]: https://docs.microsoft.com/azure/azure-web-pubsub/howto-websocket-connect?tabs=browser#authorization
[connection_string]: https://docs.microsoft.com/azure/azure-web-pubsub/howto-websocket-connect?tabs=browser#authorization
[azure_portal]: https://docs.microsoft.com/azure/azure-web-pubsub/howto-develop-create-instance
[azure-key-credential]: https://aka.ms/azsdk-python-core-azurekeycredential
