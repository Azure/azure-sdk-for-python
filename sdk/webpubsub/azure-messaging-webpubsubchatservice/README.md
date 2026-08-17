# Azure Web PubSub Chat service client library for Python

Use this client library to manage server-side Chat resources hosted by Azure Web PubSub. Applications use the service client to manage roles, rooms, users, room membership, and persisted message history. Connected clients send real-time messages separately over WebSockets.

## Getting started

### Install the package

```bash
python -m pip install azure-messaging-webpubsubchatservice
```

### Prerequisites

- Python 3.10 or later is required to use this package.
- An [Azure subscription][azure_sub].
- An [Azure Web PubSub resource][webpubsub_docs] with Chat enabled for the target hub.

### Use with AI tools

AI coding tools such as VS Code and GitHub Copilot can help you write and debug code that uses this library. See [Using the Azure SDK for Python with AI tools](https://aka.ms/azsdk/python/ai) for available integrations.

### Create and authenticate the client

Use a connection string:

<!-- SNIPPET:sample_authentication.connection_string_auth -->

```python
import os
from azure.messaging.webpubsubservice.chat import WebPubSubChatServiceClient

hub = os.environ.get("WPS_CHAT_HUB", "test_hub")
with WebPubSubChatServiceClient.from_connection_string(
    os.environ["WPS_CHAT_CONNECTION_STRING"], hub
) as connection_string_client:
    print(type(connection_string_client).__name__)
```

<!-- END SNIPPET -->

Use an access key:

<!-- SNIPPET:sample_authentication.key_auth -->

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.messaging.webpubsubservice.chat import WebPubSubChatServiceClient

endpoint = os.environ["WPS_CHAT_ENDPOINT"]
hub = os.environ.get("WPS_CHAT_HUB", "test_hub")
with WebPubSubChatServiceClient(
    endpoint,
    hub,
    AzureKeyCredential(os.environ["WPS_CHAT_ACCESS_KEY"]),
) as key_client:
    print(type(key_client).__name__)
```

<!-- END SNIPPET -->

Use Microsoft Entra ID after installing `azure-identity` and assigning the appropriate Web PubSub data-plane role:

<!-- SNIPPET:sample_authentication.entra_auth -->

```python
import os
from azure.identity import DefaultAzureCredential
from azure.messaging.webpubsubservice.chat import WebPubSubChatServiceClient

endpoint = os.environ["WPS_CHAT_ENDPOINT"]
hub = os.environ.get("WPS_CHAT_HUB", "test_hub")
with WebPubSubChatServiceClient(endpoint, hub, DefaultAzureCredential()) as entra_client:
    print(type(entra_client).__name__)
```

<!-- END SNIPPET -->

## Key concepts

- **Role**: A named set of user or room permissions.
- **User**: A Chat profile assigned to a user role.
- **Room**: A server-side Chat room with a default persisted conversation.
- **Room member**: A user assigned a room role within a room.
- **Message history**: Messages sent by connected WebSocket clients and persisted by the Chat service. The REST API lists, updates, and deletes messages; it does not create them.

## Examples

### Generate client access credentials

<!-- SNIPPET:sample_client_access.client_access -->

```python
import os
from azure.messaging.webpubsubservice.chat import WebPubSubChatServiceClient

connection_string = os.environ["WPS_CHAT_CONNECTION_STRING"]
with WebPubSubChatServiceClient.from_connection_string(
    connection_string,
    os.environ.get("WPS_CHAT_HUB", "test_hub"),
) as client:
    access = client.get_client_access_token(user_id="sample-user")
    print(access["url"])
```

<!-- END SNIPPET -->

### Create a custom role

```python
from azure.messaging.webpubsubservice.chat import UserPermissions
from azure.messaging.webpubsubservice.chat.models import ChatRole

client.create_or_replace_role(
    "user.moderator",
    ChatRole(permissions=[UserPermissions.CREATE_ROOM]),
)
for role in client.list_roles():
    print(role.name, role.permissions)
client.delete_role("user.moderator")
```

### Handle service errors

```python
from azure.core.exceptions import HttpResponseError

try:
    room = client.get_room("room-id")
except HttpResponseError as error:
    print(f"Chat service request failed: {error}")
```

See the executable [package samples][samples] for authentication, sync and async resource management, built-in constants, client access generation, and message history.

## Troubleshooting

Enable SDK logging by passing `logging_enable=True` when creating the client. HTTP headers and bodies can contain sensitive information; do not enable detailed logging in production without reviewing the output.

The client access API returns a WebSocket URL containing an access token. Do not log or persist that URL. Connection strings and access keys must also be treated as secrets.

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
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[azure_sub]: https://azure.microsoft.com/free/
[webpubsub_docs]: https://learn.microsoft.com/azure/azure-web-pubsub/overview
[samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples
