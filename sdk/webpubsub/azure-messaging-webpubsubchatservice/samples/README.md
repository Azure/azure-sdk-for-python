# Azure Web PubSub Chat samples

Use the [package README](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/README.md) for installation, authentication, and
Chat hub prerequisites.

## Request-body styles

Operations with a JSON request body support three styles:

- **Model-based (recommended for getting started):** construct a class from
  `azure.messaging.webpubsubchatservice.models`, using Python names such as
  `role_name`. Models provide attribute access, type hints, and SDK-managed
  serialization. See the model-based operation examples below and `model_based`
  in the [three-style comparison](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_request_body_styles.py).
- **Typed dictionary:** annotate a dictionary with a `TypedDict` from
  `azure.messaging.webpubsubchatservice.types`, using JSON names such as
  `roleName`. A type checker can check its keys and value types. See
  `typed_dictionary` in the [three-style comparison](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_request_body_styles.py).
- **Plain dictionary:** pass a JSON-shaped dictionary directly, without an
  explicit `TypedDict` annotation. See `plain_dictionary` in the
  [three-style comparison](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_request_body_styles.py).

For example, these request bodies express the same room membership:

```python
from azure.messaging.webpubsubchatservice import models, types

model = models.ChatRoomMemberCreateOrReplace(role_name="room.member")
typed: types.ChatRoomMemberCreateOrReplace = {"roleName": "room.member"}
plain = {"roleName": "room.member"}
```

All three styles call the same client methods. A typed dictionary is an ordinary
dictionary at runtime; its annotation does not add runtime validation. These
examples use "JSON" to mean a dictionary of JSON fields, not a JSON-encoded string.
Dictionary literals can also be checked against the method's type hints.

GET, LIST, and DELETE operations in this client have no JSON request body, so
there is no request-body style to choose. GET and LIST still return model
instances or paged models; their examples are not duplicated by input style.

## Scenario samples

| Sample | Purpose |
| --- | --- |
| [Authentication](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_authentication.py) | Connection string, access key, and Microsoft Entra ID authentication. |
| [Client access credentials](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_client_access.py) / [async](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_client_access_async.py) | Generate credentials for a Chat WebSocket client. |
| [Roles and permissions](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_roles_and_permissions.py) / [async](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_roles_and_permissions_async.py) | Create or replace a role using a model and permission enums. |
| [Message management](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_message_management.py) | Update and delete persisted messages. |
| [Service errors](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_errors.py) | Handle and re-raise an HTTP service error. |
| [Logging](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_logging.py) | Enable SDK HTTP logging. |
| [README snippet sources](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_readme_snippets.py) | Independent functions used by the README, not a standalone program. |

For runnable scenario samples, follow the environment-variable instructions
in each file and the [README run instructions](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/README.md#run-the-examples).
Replace resource ID placeholders such as `<conversation-id>` and `<message-id>`
with existing resource identifiers before running the examples.
Some samples create, replace, or delete resources; use sample-specific
identifiers and review each file before running it.

## Complete operation index

The model-based operation examples expose a `sample(client)` function. Supply an
authenticated client as shown in the [authentication sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_authentication.py)
and replace the example identifiers with your own. These functions illustrate
API usage; they are not standalone command-line programs.

Membership examples assume an existing room, user, and `room.member` role. User
creation assumes an existing `user.member` role. Topic examples assume an
existing room; update examples assume an existing topic or persisted message.
The topic update example reads the current ETag before issuing a conditional
update. No extra resource environment variables or shared runner are needed.

Create/replace operations can overwrite existing resources; delete operations
remove the specified resource (topic deletion is a soft delete). Use isolated
sample resources and review each operation before running it. The samples do
not create unrelated prerequisites or send WebSocket messages.

Standalone generated examples are not included. The handwritten examples below
cover every service operation; use the three-style comparison for dictionary inputs.

| Operation | Handwritten example |
| --- | --- |
| `get_client_access_token` | [Sync](sample_client_access.py) / [async](sample_client_access_async.py) |
| `create_or_replace_role` | [Model request](sample_create_or_replace_role.py) |
| `create_or_replace_room` | [Model request](sample_create_or_replace_room.py) |
| `create_or_replace_room_member` | [Model request](sample_create_or_replace_room_member.py) / [dictionary styles](sample_request_body_styles.py) |
| `create_or_replace_user` | [Model request](sample_create_or_replace_user.py) |
| `create_or_replace_topic` | [Model request](sample_create_or_replace_topic.py) / [typed dictionary replacement](sample_request_body_styles.py) |
| `update_topic` | [Model request](sample_update_topic.py) |
| `update_message` | [Model request](sample_update_message.py) |
| `get_role`, `get_room`, `get_user`, `get_topic`, `get_conversation` | [Read operation functions](sample_read_operations.py) |
| `list_roles`, `list_rooms`, `list_room_members`, `list_users`, `list_topics`, `list_rooms_for_user`, `list_messages` | [List operation functions](sample_read_operations.py) |
| `delete_role`, `delete_room`, `delete_room_member`, `delete_user`, `delete_topic`, `delete_message` | [Delete operation functions](sample_delete_operations.py) |

The synchronous and asynchronous clients expose the same service operations.
Await asynchronous non-paging calls, and use `async for` to iterate asynchronous
paged results.
