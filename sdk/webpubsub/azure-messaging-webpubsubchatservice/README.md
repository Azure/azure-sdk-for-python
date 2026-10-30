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
| [Examples](#examples)
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

### Hub

A hub is a logical collection of WebSocket connections. A chat hub adds built-in rooms, member management, message persistence, and chat-specific APIs.

This SDK applies only to chat hubs. Chat must be enabled on the target hub before the SDK can manage roles, users, rooms, members, conversations, or messages.

### Role and permission

A role is a named collection of Chat permissions. User role names start with `user.`, and room role names start with `room.`. Do not combine user and room permissions in one role.

User roles control operations such as creating rooms. Room roles control what a member can do in a particular room, such as publishing messages or reading message history.

### User

A user represents an identity participating in chat, such as a human end user or an application. Client access credentials associate WebSocket connections with a user ID.

### Room

A room groups users together and is the primary organizational unit for chat interactions. Every room has an automatically created default conversation.

### Room member

A room member represents a user added to a room. Membership controls which users can receive and send messages in the room. In the service API, each room member is assigned a room role.

### Conversation and message history

A conversation is an ordered message stream within a room. Every room has a default conversation, and additional named conversations can be created through topics.

Messages sent to a conversation are delivered in real time to the room's connected members. The chat service manages ordering and persistence, allowing members to load message history after reconnecting or joining later. The service client can list, update, and delete persisted messages.

`ChatConversation.room_id` identifies the room containing the conversation.
`list_messages` returns messages from latest to earliest, using message IDs as
pagination cursors. The returned pager follows the service's `nextLink`
automatically. To resume a page iteration, pass its continuation token to
`by_page(continuation_token=...)`, not to `list_messages` itself.

### Topic

A topic represents a named conversation within a room. Topics can be created,
renamed, archived, and soft deleted independently of the room's default conversation.

## Examples

The async snippet
uses a client from `azure.messaging.webpubsubchatservice.aio`.
Replace placeholders such as `<room-id>` with your application's resource identifiers.

### Request-body styles

You can supply a JSON request body in three ways:

- **Model-based:** use classes from `azure.messaging.webpubsubchatservice.models`
  with Python-style attributes and SDK-managed serialization.
- **Typed dictionary:** use the `TypedDict` definitions from
  `azure.messaging.webpubsubchatservice.types` for static checking of dictionaries
  that use JSON field names.
- **Plain dictionary:** pass a dictionary using JSON field names.

Model-based usage is recommended for getting started and is used throughout the
examples below. Dictionaries are useful when your application already works with
JSON-shaped data. All three styles call the same client methods; typed dictionaries
are ordinary dictionaries at runtime and do not add runtime validation. See the
[examples guide](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/README.md#request-body-styles)
for a comparison and examples of each style.

Explore the examples:

- [Model-based and scenario examples][examples], including complete synchronous and
  asynchronous programs.
- [Model, typed-dictionary, and plain-dictionary comparison](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_request_body_styles.py).
- [Complete operation index](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/README.md#complete-operation-index),
  linking to handwritten examples for each service operation.

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

Create operations use dedicated request models such as `ChatRoleCreateOrReplace` and
`ChatRoomCreateOrReplace`. PATCH operations use `ChatTopicUpdate` and `ChatMessageUpdate`,
whose fields can be omitted to leave existing values unchanged. The operations
return resource models such as `ChatRole`, `ChatRoom`, and `ChatTopic`, which
include service-assigned identifiers and ETags.

Use the `ChatRoleCreateOrReplace` model and `ChatPermission` enum instead of a dictionary with
permission string literals.

<!-- SNIPPET:sample_roles_and_permissions.create_role -->

```python
from azure.messaging.webpubsubchatservice.models import ChatPermission, ChatRoleCreateOrReplace

role = client.create_or_replace_role(
    "user.example",
    ChatRoleCreateOrReplace(permissions=[ChatPermission.USER_CREATE_ROOM]),
)
print(role.name, role.permissions)
```

<!-- END SNIPPET -->

See the [synchronous role example](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_roles_and_permissions.py)
and [asynchronous role example](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_roles_and_permissions_async.py)
for runnable model-and-enum examples. The selected role is created or replaced
and remains in the hub; these examples do not create users or rooms.

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
from azure.messaging.webpubsubchatservice.models import HumanChatUserCreateOrReplace

user = client.create_or_replace_user(
    "alice",
    HumanChatUserCreateOrReplace(nickname="Alice", role_name="user.room_creator"),
)
print(user.id, user.nickname)
```

<!-- END SNIPPET -->

### Create a room

<!-- SNIPPET:sample_readme_snippets.create_room -->

```python
from azure.messaging.webpubsubchatservice.models import ChatRoomCreateOrReplace

room = client.create_or_replace_room("general", ChatRoomCreateOrReplace(title="General"))
print(room.id, room.default_conversation)
```

<!-- END SNIPPET -->

### Add a room member

The room `general`, user `alice`, and room role `room.contributor` must already exist.

<!-- SNIPPET:sample_readme_snippets.add_room_member -->

```python
from azure.messaging.webpubsubchatservice.models import ChatRoomMemberCreateOrReplace

member = client.create_or_replace_room_member(
    "general",
    "alice",
    ChatRoomMemberCreateOrReplace(role_name="room.contributor"),
)
print(member.user_id, member.role_name)
```

<!-- END SNIPPET -->

### List persisted messages

Replace `<conversation-id>` with an existing conversation ID.

<!-- SNIPPET:sample_readme_snippets.list_messages -->

```python
for message in client.list_messages("<conversation-id>"):
    print(message.id, message.created_by, message.content.text)
```

<!-- END SNIPPET -->

### Manage room topics

Replace `<room-id>` with an existing room ID and `<topic-id>` with the topic ID.

#### Create a topic

`ChatTopicCreateOrReplace` requires a title. When replacing an existing topic,
you can also supply `state`, for example
`ChatTopicCreateOrReplace(title="Announcements", state=ChatTopicState.ARCHIVED)`.
Import `ChatTopicState` from `azure.messaging.webpubsubchatservice.models`.
Omit `state` when creating a topic.

<!-- SNIPPET:sample_readme_snippets.create_topic -->

```python
from azure.messaging.webpubsubchatservice.models import ChatTopicCreateOrReplace

topic = client.create_or_replace_topic(
    "<room-id>",
    "<topic-id>",
    ChatTopicCreateOrReplace(title="Announcements"),
)
print(topic.id, topic.etag)
```

<!-- END SNIPPET -->

#### List topics

<!-- SNIPPET:sample_readme_snippets.list_topics -->

```python
for topic in client.list_topics("<room-id>", max_page_size=10):
    print(topic.id, topic.title, topic.conversation_id)
```

<!-- END SNIPPET -->

#### Get a topic

<!-- SNIPPET:sample_readme_snippets.get_topic -->

```python
topic = client.get_topic("<room-id>", "<topic-id>")
print(topic.id, topic.title, topic.state, topic.etag)
```

<!-- END SNIPPET -->

#### Archive a topic

Replace `<topic-etag>` with the ETag returned by a previous create or get
operation, preserving its quotes. The update below changes only `state`; the existing title is left
unchanged. To change only the title, use `ChatTopicUpdate(title="New title")`.

<!-- SNIPPET:sample_readme_snippets.archive_topic -->

```python
from azure.core import MatchConditions
from azure.messaging.webpubsubchatservice.models import ChatTopicUpdate, ChatTopicState

topic = client.update_topic(
    "<room-id>",
    "<topic-id>",
    ChatTopicUpdate(state=ChatTopicState.ARCHIVED),
    etag='"<topic-etag>"',
    match_condition=MatchConditions.IfNotModified,
)
print(topic.id, topic.state, topic.etag)
```

<!-- END SNIPPET -->

#### Soft delete a topic

Replace `<topic-etag>` with the current ETag, including any change from an update.

<!-- SNIPPET:sample_readme_snippets.delete_topic -->

```python
from azure.core import MatchConditions

client.delete_topic(
    "<room-id>",
    "<topic-id>",
    etag='"<topic-etag>"',
    match_condition=MatchConditions.IfNotModified,
)
```

<!-- END SNIPPET -->

Use the topic's `conversation_id` with `get_conversation` and `list_messages`.

For conditional updates and deletes, pass the current ETag with
`MatchConditions.IfNotModified`. A stale ETag prevents overwriting a topic
that another caller has changed. Deleting a topic is a soft delete.

For individual API calls, see the
[operation examples](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/README.md#complete-operation-index).

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

Replace `<user-id>` with an existing user ID.

<!-- SNIPPET:sample_readme_snippets.list_rooms_for_user -->

```python
for room in client.list_rooms_for_user("<user-id>"):
    print(room.id, room.title)
```

<!-- END SNIPPET -->

For basic list calls, see the functions in
[the README snippet sources](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_readme_snippets.py).
Listing rooms for a user requires an existing user ID.

Collection iterators automatically fetch subsequent pages.

### Use the asynchronous client

Run this snippet inside an async function with an authenticated async `client`; see
[the asynchronous client access example](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_client_access_async.py)
for the complete program.

<!-- SNIPPET:sample_client_access_async.client_access_async -->

```python
access = await client.get_client_access_token(user_id="sample-user")
# Give access["url"] to the intended client to connect; it includes the access token.
# Print only the token-free base URL here. Do not log access["url"].
print(access["baseUrl"])
```

<!-- END SNIPPET -->

### Run the examples

Set `WPS_CHAT_CONNECTION_STRING` and optionally `WPS_CHAT_HUB` (default: `test_hub`).
The role examples use `user.example`; replace it with a role name reserved for
the example. An existing role with that name is replaced.
Install `aiohttp` to run async examples.

From the package directory, run, for example:

```bash
python samples/sample_roles_and_permissions.py
python samples/sample_roles_and_permissions_async.py
```

## Troubleshooting

### Handle service errors

Service operations raise `HttpResponseError` or a more specific subclass when a request fails:

The [service error example](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_errors.py) reads an existing role,
prints the status on failure, and re-raises the error. Replace `user.example`
with the role name to read.

<!-- SNIPPET:sample_errors.handle_service_errors -->

```python
from azure.core.exceptions import HttpResponseError

try:
    role = client.get_role("user.example")
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

## Next steps

Explore the [README snippet sources](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_readme_snippets.py) and
[complete package examples][examples] to learn how to:

- Authenticate with a connection string, access key, or Microsoft Entra ID.
- Manage roles, permissions, users, rooms, and room members.
- Generate client access credentials.
- Query, update, and delete message history.
- Manage topic lifecycles and iterate over room and user collections.
- Use synchronous and asynchronous clients.

See also the [request-body style comparison](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_request_body_styles.py).

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
[examples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples
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
