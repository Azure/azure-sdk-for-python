# Azure Web PubSub Chat service client library for Python

[Azure Web PubSub chat][product_docs] is a managed chat capability built on [Azure Web PubSub][webpubsub_docs]. It provides purpose-built client and server APIs for chat scenarios. Applications use the SDKs to communicate with the Azure service and work with chat-native concepts such as rooms, messages, members, and users. The service handles real-time message delivery and ordering, fan-out across a user's devices and browser tabs, room membership, and message persistence and retrieval.

Use this client library in an application server to:

- Create and manage chat roles and permissions.
- Create users, rooms, and room memberships.
- List rooms, users, and the rooms associated with a user.
- Create, list, update, and soft delete room topics.
- Get room conversations and query persisted message history.
- Update and delete persisted messages.
- Generate client access credentials for Chat WebSocket clients.


[Source code][source_code]
| [Package (PyPI)][package]
| [API reference documentation][api_reference]
| [Product documentation][product_docs]
| [Samples][samples]
| [Generated samples][generated_samples]
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
from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient

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
from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient

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
from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient

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

The asynchronous client is available from the `azure.messaging.webpubsubchatservice.aio` namespace.

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

### Topic

A topic is a named thread within a room with its own conversation. The service returns its
ID, creation time, creator, conversation ID, and ETag in responses. Topic IDs are specified
by the application in the request path. Topics have a lifecycle state of `Normal`, `Archived`,
or `SoftDeleted`. Creating a topic requires a title; updating a topic can change its title
and state. Deleting a topic is a soft delete.

The default service API version is `2026-08-01-preview`, which adds topics and the
room, user, and user-room collection operations.

## Examples

The following sections show common scenarios. Each operation snippet assumes an
authenticated `client`, created as shown in Getting started. The async snippet
uses a client from `azure.messaging.webpubsubchatservice.aio`.
See the [package samples][samples] for complete synchronous and asynchronous programs.

### Generate client access credentials

Generate credentials that a Chat WebSocket client can use to connect as a specific user:

<!-- SNIPPET:sample_client_access.client_access -->

```python
access = client.get_client_access_token(user_id="sample-user")
# Give access["url"] to the intended client to connect; it includes the access token.
# Print only the token-free base URL here. Do not log access["url"].
print(access["baseUrl"])
```

<!-- END SNIPPET -->

The returned URL contains an access token. Send it only to the intended client, and do not log or persist it in production.

### Create a role

Use the `ChatRole` model and `ChatPermission` enum instead of a dictionary with
permission string literals. This example assumes `os` is imported.

<!-- SNIPPET:sample_roles_and_permissions.create_role -->

```python
from azure.messaging.webpubsubchatservice.models import ChatPermission, ChatRole

role = client.create_or_replace_role(
    os.environ.get("WPS_CHAT_ROLE_NAME", "user.python_sample"),
    ChatRole(permissions=[ChatPermission.USER_CREATE_ROOM]),
)
print(role.name, role.permissions)
```

<!-- END SNIPPET -->

See [sample_roles_and_permissions.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_roles_and_permissions.py)
and [sample_roles_and_permissions_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_roles_and_permissions_async.py)
for runnable model-and-enum examples. The selected role is created or replaced
and remains in the hub; these samples do not create users or rooms.

### List roles

<!-- SNIPPET:sample_readme_snippets.list_roles -->

```python
for role in client.list_roles():
    print(role.name)
```

<!-- END SNIPPET -->

### Create a user

The user role `user.room_creator` must already exist.

<!-- SNIPPET:sample_readme_snippets.create_user -->

```python
from azure.messaging.webpubsubchatservice.models import HumanChatUser

user = client.create_or_replace_user(
    "alice",
    HumanChatUser(nickname="Alice", role_name="user.room_creator"),
)
print(user.id, user.nickname)
```

<!-- END SNIPPET -->

### Create a room

<!-- SNIPPET:sample_readme_snippets.create_room -->

```python
from azure.messaging.webpubsubchatservice.models import ChatRoom

room = client.create_or_replace_room("general", ChatRoom(title="General"))
print(room.id, room.default_conversation)
```

<!-- END SNIPPET -->

### Add a room member

The room `general`, user `alice`, and room role `room.contributor` must already exist.

<!-- SNIPPET:sample_readme_snippets.add_room_member -->

```python
from azure.messaging.webpubsubchatservice.models import ChatRoomMember

member = client.create_or_replace_room_member(
    "general",
    "alice",
    ChatRoomMember(role_name="room.contributor"),
)
print(member.user_id, member.role_name)
```

<!-- END SNIPPET -->

### List persisted messages

Set `WPS_CHAT_CONVERSATION_ID` to an existing conversation ID.

<!-- SNIPPET:sample_readme_snippets.list_messages -->

```python
import os

for message in client.list_messages(os.environ["WPS_CHAT_CONVERSATION_ID"]):
    print(message.id, message.created_by, message.content.text)
```

<!-- END SNIPPET -->

### Manage room topics

These examples use an existing room identified by `WPS_CHAT_ROOM_ID` and a
topic ID specified by `WPS_CHAT_TOPIC_ID`.

#### Create a topic

<!-- SNIPPET:sample_readme_snippets.create_topic -->

```python
import os
from azure.messaging.webpubsubchatservice.models import ChatTopic

topic = client.create_or_replace_topic(
    os.environ["WPS_CHAT_ROOM_ID"],
    os.environ["WPS_CHAT_TOPIC_ID"],
    ChatTopic({"title": "Announcements"}),
)
print(topic.id, topic.etag)
```

<!-- END SNIPPET -->

#### List topics

<!-- SNIPPET:sample_readme_snippets.list_topics -->

```python
import os

for topic in client.list_topics(os.environ["WPS_CHAT_ROOM_ID"], max_page_size=10):
    print(topic.id, topic.title, topic.conversation_id)
```

<!-- END SNIPPET -->

#### Get a topic

<!-- SNIPPET:sample_readme_snippets.get_topic -->

```python
import os

topic = client.get_topic(os.environ["WPS_CHAT_ROOM_ID"], os.environ["WPS_CHAT_TOPIC_ID"])
print(topic.id, topic.title, topic.state, topic.etag)
```

<!-- END SNIPPET -->

#### Archive a topic

Set `WPS_CHAT_TOPIC_ETAG` to the ETag returned by a previous create or get
operation.

<!-- SNIPPET:sample_readme_snippets.archive_topic -->

```python
import os
from azure.core import MatchConditions
from azure.messaging.webpubsubchatservice.models import ChatTopic, ChatTopicState

topic = client.update_topic(
    os.environ["WPS_CHAT_ROOM_ID"],
    os.environ["WPS_CHAT_TOPIC_ID"],
    ChatTopic(title="Announcements", state=ChatTopicState.ARCHIVED),
    etag=os.environ["WPS_CHAT_TOPIC_ETAG"],
    match_condition=MatchConditions.IfNotModified,
)
print(topic.id, topic.state, topic.etag)
```

<!-- END SNIPPET -->

#### Soft delete a topic

Set `WPS_CHAT_TOPIC_ETAG` to the current ETag, including any change from an update.

<!-- SNIPPET:sample_readme_snippets.delete_topic -->

```python
import os
from azure.core import MatchConditions

client.delete_topic(
    os.environ["WPS_CHAT_ROOM_ID"],
    os.environ["WPS_CHAT_TOPIC_ID"],
    etag=os.environ["WPS_CHAT_TOPIC_ETAG"],
    match_condition=MatchConditions.IfNotModified,
)
```

<!-- END SNIPPET -->

Use the topic's `conversation_id` with `get_conversation` and `list_messages`.

For conditional updates and deletes, pass the current ETag with
`MatchConditions.IfNotModified`. A stale ETag prevents overwriting a topic
that another caller has changed. Deleting a topic is a soft delete.

For individual API calls, see the generated samples for
[create or replace](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/create_or_replace_topic.py),
[list](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/list_topics.py), [get](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/get_topic.py),
[update](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/update_topic.py), and
[delete](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/delete_topic.py).

### List rooms and users

#### List rooms

<!-- SNIPPET:sample_readme_snippets.list_rooms -->

```python
for room in client.list_rooms(max_page_size=10):
    print(room.id, room.title)
```

<!-- END SNIPPET -->

#### List users

<!-- SNIPPET:sample_readme_snippets.list_users -->

```python
for user in client.list_users(max_page_size=10):
    print(user.id, user.kind)
```

<!-- END SNIPPET -->

#### List rooms for a user

Set `WPS_CHAT_USER_ID` to an existing user ID.

<!-- SNIPPET:sample_readme_snippets.list_rooms_for_user -->

```python
import os

for room in client.list_rooms_for_user(os.environ["WPS_CHAT_USER_ID"]):
    print(room.id, room.title)
```

<!-- END SNIPPET -->

For basic list calls, see [list_rooms.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/list_rooms.py),
[list_users.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/list_users.py), and
[list_rooms_for_user.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/list_rooms_for_user.py).
Listing rooms for a user requires an existing user ID.

Collection iterators automatically fetch subsequent pages.

### Use the asynchronous client

Run this snippet inside an async function with an authenticated async `client`; see
[sample_client_access_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_client_access_async.py)
for the complete program.

<!-- SNIPPET:sample_client_access_async.client_access_async -->

```python
access = await client.get_client_access_token(user_id="sample-user")
# Give access["url"] to the intended client to connect; it includes the access token.
# Print only the token-free base URL here. Do not log access["url"].
print(access["baseUrl"])
```

<!-- END SNIPPET -->

### Run the samples

Set `WPS_CHAT_CONNECTION_STRING` and optionally `WPS_CHAT_HUB` (default: `test_hub`).
The role samples accept `WPS_CHAT_ROLE_NAME` (default: `user.python_sample`).
Use a role name reserved for the sample: an existing role with that name is
replaced. Install `aiohttp` to run async samples.

From the package directory, run, for example:

```bash
python samples/sample_roles_and_permissions.py
python samples/sample_roles_and_permissions_async.py
```

## Troubleshooting

### Handle service errors

Service operations raise `HttpResponseError` or a more specific subclass when a request fails:

The [sample_errors.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_errors.py) example reads an existing role,
prints the status on failure, and re-raises the error. Set `WPS_CHAT_ROLE_NAME`
to the role to read (default: `user.python_sample`).

<!-- SNIPPET:sample_errors.handle_service_errors -->

```python
import os
from azure.core.exceptions import HttpResponseError

try:
    role = client.get_role(os.environ.get("WPS_CHAT_ROLE_NAME", "user.python_sample"))
    print(role.name, role.permissions)
except HttpResponseError as error:
    print(f"Chat service request failed with status {error.status_code}")
    raise
```

<!-- END SNIPPET -->

### Logging

This library uses the standard Python [logging][python_logging] library. Enable HTTP logging for a client by passing `logging_enable=True`:

<!-- SNIPPET:sample_logging.configure_logging -->

```python
import logging
import os
import sys

from azure.identity import DefaultAzureCredential
from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient

logger = logging.getLogger("azure")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))

with DefaultAzureCredential() as credential:
    with WebPubSubChatServiceClient(
        os.environ["WPS_CHAT_ENDPOINT"],
        os.environ.get("WPS_CHAT_HUB", "test_hub"),
        credential,
        logging_enable=True,
    ) as client:
        print(type(client).__name__)
```

<!-- END SNIPPET -->

HTTP logs can contain sensitive information. Do not enable detailed logging in production without reviewing how logs are collected and protected. For more information, see [Configure logging in the Azure SDK for Python][azure_sdk_logging].

### Authentication and authorization

- Confirm that the endpoint and hub name identify the Web PubSub resource and Chat-enabled hub you intend to use.
- For Microsoft Entra ID, confirm that the principal has an appropriate Web PubSub data-plane role and that role assignment propagation has completed.
- Connection-string and access-key authentication are unavailable when local authentication is disabled on the Web PubSub resource.

### Message history

If a newly sent message does not appear immediately, confirm that the sending user is a room member with publish permission and that message history is enabled for the member's room role.

## Next steps

Explore the [README snippet sources](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_readme_snippets.py) and
[complete package samples][samples] to learn how to:

- Authenticate with a connection string, access key, or Microsoft Entra ID.
- Manage roles, permissions, users, rooms, and room members.
- Generate client access credentials.
- Query, update, and delete message history.
- Manage topic lifecycles and iterate over room and user collections.
- Use synchronous and asynchronous clients.

See also the [generated operation samples][generated_samples], produced from the
specification's examples. Each file demonstrates one operation. Replace
`ENDPOINT`, `HUB`, and any example resource identifiers before running them,
and configure authentication as described in each file. These generated files
are refreshed during SDK generation. The README snippet source contains
independent functions, not a combined workflow or a standalone program.
The runnable hand-written samples demonstrate model and permission-enum usage,
authentication, client access credentials, errors, and logging.

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
[generated_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples
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
[rest_api]: https://learn.microsoft.com/rest/api/webpubsub/dataplane/webpubsubchat/web-pub-sub-chat-service-client
[design_guidelines]: https://azure.github.io/azure-sdk/python_design.html
[contributing]: https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[code_of_conduct_faq]: https://opensource.microsoft.com/codeofconduct/faq/
