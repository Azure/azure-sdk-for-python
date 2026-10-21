# Azure Web PubSub Chat samples

Use the [package README](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/README.md) for installation, authentication, and
Chat hub prerequisites.

## Sample styles

The model-based examples in this directory use model classes from
`azure.messaging.webpubsubchatservice.models`. These classes use Python property
names such as `role_name`. The [generated samples](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples) use
ordinary dictionary literals with JSON field names such as `roleName`.
The `TypedDict` definitions in `azure.messaging.webpubsubchatservice.types`
describe those dictionary shapes for static type checking; they do not create
model instances or validate values at runtime. Both request-body styles are
accepted by the corresponding client operations.

Both styles call the same client methods; these are not separate convenience
and protocol method APIs.

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
in each file and the [README run instructions](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/README.md#run-the-samples).
Some samples create, replace, or delete resources; use sample-specific
identifiers and review each file before running it.

## Complete operation index

Each operation has a runnable model-based sample and a dictionary-based sample
generated from specification examples. For operations without request bodies,
both styles use the same parameter types.

Run model-based samples from the package directory, for example:

```bash
python samples/sample_list_rooms.py
python samples/sample_create_or_replace_topic.py
```

Set `WPS_CHAT_CONNECTION_STRING` and optionally `WPS_CHAT_HUB` (default:
`test_hub`). Each sample reports any additional missing variables without
contacting the service. Identifiers must refer to existing resources for get,
list, update, membership, and delete operations.

| Variable | Used for |
| --- | --- |
| `WPS_CHAT_ROLE_NAME` | Role operations. Use a `room.` name when running the role creation sample. |
| `WPS_CHAT_ROOM_ID` | Room, room member, and topic operations. |
| `WPS_CHAT_USER_ID` | User, membership, and user-room operations. |
| `WPS_CHAT_USER_ROLE_NAME` | Existing `user.` role for user creation. |
| `WPS_CHAT_ROOM_ROLE_NAME` | Existing `room.` role for adding a member. |
| `WPS_CHAT_TOPIC_ID` | Topic operations. |
| `WPS_CHAT_TOPIC_ETAG` | Current ETag from get/create for conditional topic update and delete. Refresh it after an update. |
| `WPS_CHAT_CONVERSATION_ID` | Conversation and message operations. Obtain it from a room or topic. |
| `WPS_CHAT_MESSAGE_ID` | Existing persisted message to update or delete. |

Create/replace operations can overwrite existing resources; delete operations
remove the specified resource (topic deletion is a soft delete). Use isolated
sample resources and review each operation before running it. The samples do
not create unrelated prerequisites or send WebSocket messages.

Dictionary-based samples use placeholder endpoints and example identifiers;
replace them and configure authentication as described in each file.

| Operation | Dictionary-based sample | Model-based sample |
| --- | --- | --- |
| `get_client_access_token` | SDK convenience method; no generated sample. | [Sync](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_client_access.py) / [async](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_client_access_async.py) |
| `create_or_replace_role` | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/create_or_replace_role.py) | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_create_or_replace_role.py) |
| `get_role` | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/get_role.py) | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_get_role.py) |
| `list_roles` | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/list_roles.py) | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_list_roles.py) |
| `delete_role` | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/delete_role.py) | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_delete_role.py) |
| `create_or_replace_room` | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/create_or_replace_room.py) | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_create_or_replace_room.py) |
| `get_room` | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/get_room.py) | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_get_room.py) |
| `list_rooms` | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/list_rooms.py) | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_list_rooms.py) |
| `delete_room` | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/delete_room.py) | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_delete_room.py) |
| `create_or_replace_room_member` | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/create_or_replace_room_member.py) | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_create_or_replace_room_member.py) |
| `list_room_members` | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/list_room_members.py) | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_list_room_members.py) |
| `delete_room_member` | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/delete_room_member.py) | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_delete_room_member.py) |
| `create_or_replace_user` | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/create_or_replace_user.py) | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_create_or_replace_user.py) |
| `get_user` | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/get_user.py) | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_get_user.py) |
| `list_users` | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/list_users.py) | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_list_users.py) |
| `delete_user` | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/delete_user.py) | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_delete_user.py) |
| `list_rooms_for_user` | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/list_rooms_for_user.py) | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_list_rooms_for_user.py) |
| `create_or_replace_topic` | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/create_or_replace_topic.py) | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_create_or_replace_topic.py) |
| `get_topic` | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/get_topic.py) | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_get_topic.py) |
| `list_topics` | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/list_topics.py) | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_list_topics.py) |
| `update_topic` | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/update_topic.py) | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_update_topic.py) |
| `delete_topic` | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/delete_topic.py) | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_delete_topic.py) |
| `get_conversation` | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/get_conversation.py) | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_get_conversation.py) |
| `list_messages` | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/list_messages.py) | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_list_messages.py) |
| `update_message` | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/update_message.py) | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_update_message.py) |
| `delete_message` | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/generated_samples/delete_message.py) | [Sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/webpubsub/azure-messaging-webpubsubchatservice/samples/sample_delete_message.py) |

The synchronous and asynchronous clients expose the same service operations.
Await asynchronous non-paging calls, and use `async for` to iterate asynchronous
paged results.
