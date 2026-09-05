# Azure Web PubSub Chat service client library for Python

[Azure Web PubSub chat][product_docs] is a managed chat capability built on [Azure Web PubSub][webpubsub_docs]. It provides purpose-built client and server APIs for chat scenarios. Applications use the SDKs to communicate with the Azure service and work with chat-native concepts such as rooms, messages, members, and users. The service handles real-time message delivery and ordering, fan-out across a user's devices and browser tabs, room membership, and message persistence and retrieval.

Use this client library in an application server to:

- Create and manage chat roles and permissions.
- Create users, rooms, and room memberships.
- Get room conversations and query persisted message history.
- Update and delete persisted messages.
- Generate client access credentials for Chat WebSocket clients.


[Source code][source_code]
| [Package (PyPI)][package]
| [API reference documentation][api_reference]
| [Product documentation][product_docs]
| [Samples][samples]
| [Changelog][changelog]

## Getting started

### Prerequisites

- Python 3.10 or later.
- An [Azure subscription][azure_sub].
- An [Azure Web PubSub resource][create_instance].
- A Web PubSub hub with [Chat enabled][enable_chat].

### 1. Install the package

```bash
python -m pip install azure-messaging-webpubsubchatservice
```

To use Microsoft Entra ID authentication, also install `azure-identity`:

```bash
python -m pip install azure-identity
```

### 2. Create and authenticate a `WebPubSubChatServiceClient`

The client supports a connection string, an `AzureKeyCredential`, or a Microsoft Entra ID token credential. The hub passed to the client must have Chat enabled.

#### Use a connection string

Get the connection string from the Azure portal or Azure CLI, and store it securely. See [Web PubSub authorization][connection_string] for details.

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

#### Use an access key

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

#### Use Microsoft Entra ID

For recommended passwordless authentication, assign an appropriate Web PubSub data-plane role to the principal and use a credential from the [Azure Identity library][azure_identity]. The following example uses `DefaultAzureCredential`:

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

For more information, see [Authenticate Azure-hosted Python applications][azure_identity_auth] and [Microsoft Entra authorization for Azure Web PubSub][entra_authorization].

## Key concepts

### Client

`WebPubSubChatServiceClient` is the entry point for managing Chat resources in one Web PubSub hub. Create one client for each endpoint and hub combination. The client can be used as a context manager and is safe to reuse for multiple operations.

The asynchronous client is available from the `azure.messaging.webpubsubservice.chat.aio` namespace.

### Hub

A hub is a logical collection of WebSocket connections. A standard hub offers event-based real-time messaging through the Web PubSub subprotocol or a custom subprotocol. A chat hub adds built-in rooms, member management, message persistence, and chat-specific APIs.

This SDK applies only to chat hubs. Chat must be enabled on the target hub before the SDK can manage roles, users, rooms, members, conversations, or messages.

### Role and permission

A role is a named collection of Chat permissions. User role names start with `user.`, and room role names start with `room.`. Do not combine user and room permissions in one role.

User roles control operations such as creating rooms. Room roles control what a member can do in a particular room, such as publishing messages or reading message history.

### User

A user represents an application identity that can send and receive messages. In the service API, a user is identified by a user ID and assigned a user role. A human user also has a nickname. Client access credentials associate WebSocket connections with a user ID.

### Room

A room groups users together and is the primary organizational unit for chat interactions. Every room has an automatically created default conversation.

### Room member

A room member represents a user added to a room. Membership controls which users can receive and send messages in the room. In the service API, each room member is assigned a room role.

### Conversation and message history

A conversation is a message thread that belongs to a room. Every room has a default conversation and can contain multiple conversations.

Messages sent to a conversation are delivered in real time to the room's connected members. The chat service manages ordering and persistence, allowing members to load message history after reconnecting or joining later. The service client can list, update, and delete persisted messages.

## Examples

The following sections show common scenarios. See the [package samples][samples] for complete synchronous and asynchronous programs.

### Generate client access credentials

Generate credentials that a Chat WebSocket client can use to connect as a specific user:

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

The returned URL contains an access token. Send it only to the intended client, and do not log or persist it in production.

### Create and list roles

```python
from azure.messaging.webpubsubservice.chat.models import ChatPermission, ChatRole

role_name = "user.moderator"
try:
    role = client.create_or_replace_role(
        role_name,
        ChatRole(permissions=[ChatPermission.USER_CREATE_ROOM]),
    )
    print(role.name, role.permissions)

    for listed_role in client.list_roles():
        print(listed_role.name)
finally:
    client.delete_role(role_name)
```

### Create a user, room, and room membership

```python
from azure.messaging.webpubsubservice.chat.models import (
    ChatPermission,
    ChatRole,
    ChatRoom,
    ChatRoomMember,
    HumanChatUser,
)

client.create_or_replace_role(
    "user.room_creator",
    ChatRole(permissions=[ChatPermission.USER_CREATE_ROOM]),
)
client.create_or_replace_role(
    "room.contributor",
    ChatRole(permissions=[ChatPermission.ROOM_PUBLISH_MESSAGE]),
)
client.create_or_replace_user(
    "alice",
    HumanChatUser(nickname="Alice", role_name="user.room_creator"),
)
room = client.create_or_replace_room("general", ChatRoom(title="General"))
member = client.create_or_replace_room_member(
    room.id,
    "alice",
    ChatRoomMember(role_name="room.contributor"),
)
print(member.user_id, member.role_name)
```

Delete dependent resources in reverse order when they are no longer needed: room, user, and then roles.

### List persisted messages

```python
room = client.get_room("general")
for message in client.list_messages(room.default_conversation):
    print(message.id, message.created_by, message.content.text)
```

### Use the asynchronous client

```python
from azure.identity.aio import DefaultAzureCredential
from azure.messaging.webpubsubservice.chat.aio import WebPubSubChatServiceClient

credential = DefaultAzureCredential()
client = WebPubSubChatServiceClient(endpoint, hub, credential)
try:
    async for role in client.list_roles():
        print(role.name)
finally:
    await client.close()
    await credential.close()
```

## Troubleshooting

### Handle service errors

Service operations raise `HttpResponseError` or a more specific subclass when a request fails:

```python
from azure.core.exceptions import HttpResponseError

try:
    room = client.get_room("room-id")
except HttpResponseError as error:
    print(f"Chat service request failed with status {error.status_code}")
```

### Logging

This library uses the standard Python [logging][python_logging] library. Enable HTTP logging for a client by passing `logging_enable=True`:

```python
import logging
import sys

from azure.identity import DefaultAzureCredential
from azure.messaging.webpubsubservice.chat import WebPubSubChatServiceClient

logger = logging.getLogger("azure")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))

client = WebPubSubChatServiceClient(
    endpoint,
    hub,
    DefaultAzureCredential(),
    logging_enable=True,
)
```

HTTP logs can contain sensitive information. Do not enable detailed logging in production without reviewing how logs are collected and protected. For more information, see [Configure logging in the Azure SDK for Python][azure_sdk_logging].

### Authentication and authorization

- Confirm that the endpoint and hub name identify the Web PubSub resource and Chat-enabled hub you intend to use.
- For Microsoft Entra ID, confirm that the principal has an appropriate Web PubSub data-plane role and that role assignment propagation has completed.
- Connection-string and access-key authentication are unavailable when local authentication is disabled on the Web PubSub resource.

### Message history

If a newly sent message does not appear immediately, confirm that the sending user is a room member with publish permission and that message history is enabled for the member's room role.

## Next steps

Explore the [complete package samples][samples] to learn how to:

- Authenticate with a connection string, access key, or Microsoft Entra ID.
- Manage roles, permissions, users, rooms, and room members.
- Generate client access credentials.
- Query, update, and delete message history.
- Use synchronous and asynchronous clients.

## Additional resources

- [Azure Web PubSub documentation][webpubsub_docs]
- [Web PubSub Chat documentation][product_docs]
- [Web PubSub Chat REST API][rest_api]
- [Azure SDK for Python design guidelines][design_guidelines]

## Contributing

This project welcomes contributions and suggestions. See the [contributing guide][contributing] for instructions on building, testing, and submitting changes.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information, see the [Code of Conduct FAQ][code_of_conduct_faq] or contact opencode@microsoft.com with questions or comments.

<!-- LINKS -->
[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/webpubsub/azure-messaging-webpubsubchatservice
[package]: https://pypi.org/project/azure-messaging-webpubsubchatservice/
[api_reference]: https://learn.microsoft.com/python/api/overview/azure/messaging-webpubsubchatservice-readme?view=azure-python-preview
[product_docs]: https://learn.microsoft.com/azure/azure-web-pubsub/chat-overview
[samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples
[changelog]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/CHANGELOG.md
[azure_sub]: https://azure.microsoft.com/free/
[webpubsub_docs]: https://learn.microsoft.com/azure/azure-web-pubsub/
[create_instance]: https://learn.microsoft.com/azure/azure-web-pubsub/howto-develop-create-instance
[enable_chat]: https://learn.microsoft.com/azure/azure-web-pubsub/chat-howto-enable-chat
[connection_string]: https://learn.microsoft.com/azure/azure-web-pubsub/howto-websocket-connect#authorization
[azure_identity]: https://pypi.org/project/azure-identity/
[azure_identity_auth]: https://learn.microsoft.com/azure/developer/python/sdk/authentication-overview
[entra_authorization]: https://learn.microsoft.com/azure/azure-web-pubsub/concept-azure-ad-authorization
[python_logging]: https://docs.python.org/3/library/logging.html
[azure_sdk_logging]: https://learn.microsoft.com/azure/developer/python/sdk/azure-sdk-logging
[rest_api]: https://learn.microsoft.com/rest/api/webpubsub/dataplane/webpubsubchat/web-pub-sub-chat-service
[design_guidelines]: https://azure.github.io/azure-sdk/python_design.html
[contributing]: https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[code_of_conduct_faq]: https://opensource.microsoft.com/codeofconduct/faq/
