# Azure Web PubSub Chat samples

Use the [package README](../README.md) for installation, authentication, and
Chat hub prerequisites.

## Sample styles

The hand-written request-body examples in this directory use model classes from
`azure.messaging.webpubsubchatservice.models`. These classes use Python property
names such as `role_name`. The [generated samples](../generated_samples) use
ordinary dictionary literals with JSON field names such as `roleName`.
The `TypedDict` definitions in `azure.messaging.webpubsubchatservice.types`
describe those dictionary shapes for static type checking; they do not create
model instances or validate values at runtime. Both request-body styles are
accepted by the corresponding client operations.

`HumanChatUserCreateOrReplace` automatically supplies `"kind": "Human"` when serialized.
Dictionary requests must supply that field explicitly. See
[request models and dictionaries](../README.md#request-models-and-dictionaries)
for details.

## Hand-written samples

| Sample | Purpose |
| --- | --- |
| [Authentication](sample_authentication.py) | Connection string, access key, and Microsoft Entra ID authentication. |
| [Client access credentials](sample_client_access.py) / [async](sample_client_access_async.py) | Generate credentials for a Chat WebSocket client. |
| [Roles and permissions](sample_roles_and_permissions.py) / [async](sample_roles_and_permissions_async.py) | Create or replace a role using a model and permission enums. |
| [Message management](sample_message_management.py) | Update and delete persisted messages. |
| [Service errors](sample_errors.py) | Handle and re-raise an HTTP service error. |
| [Logging](sample_logging.py) | Enable SDK HTTP logging. |
| [README snippet sources](sample_readme_snippets.py) | Independent functions used by the README, not a standalone program. |

For runnable hand-written samples, follow the environment-variable instructions
in each file and the [README run instructions](../README.md#run-the-samples).
Some samples create, replace, or delete resources; use sample-specific
identifiers and review each file before running it.

## Complete operation index

Each generated sample demonstrates one service operation using specification
examples. Replace placeholders and example resource identifiers, and configure
authentication as described in each file. Hand-written examples are linked
where available; README snippet functions require an authenticated client and
are not standalone programs.

| Operation | Generated sample | Hand-written example |
| --- | --- | --- |
| `get_client_access_token` | Not generated; SDK convenience method. | [Sync](sample_client_access.py) / [async](sample_client_access_async.py) |
| `create_or_replace_role` | [Sample](../generated_samples/create_or_replace_role.py) | [Sync](sample_roles_and_permissions.py) / [async](sample_roles_and_permissions_async.py) |
| `get_role` | [Sample](../generated_samples/get_role.py) | [Service errors](sample_errors.py) |
| `list_roles` | [Sample](../generated_samples/list_roles.py) | [README snippets](sample_readme_snippets.py) |
| `delete_role` | [Sample](../generated_samples/delete_role.py) | - |
| `create_or_replace_room` | [Sample](../generated_samples/create_or_replace_room.py) | [README snippets](sample_readme_snippets.py) |
| `get_room` | [Sample](../generated_samples/get_room.py) | - |
| `list_rooms` | [Sample](../generated_samples/list_rooms.py) | [README snippets](sample_readme_snippets.py) |
| `delete_room` | [Sample](../generated_samples/delete_room.py) | - |
| `create_or_replace_room_member` | [Sample](../generated_samples/create_or_replace_room_member.py) | [README snippets](sample_readme_snippets.py) |
| `list_room_members` | [Sample](../generated_samples/list_room_members.py) | - |
| `delete_room_member` | [Sample](../generated_samples/delete_room_member.py) | - |
| `create_or_replace_user` | [Sample](../generated_samples/create_or_replace_user.py) | [README snippets](sample_readme_snippets.py) |
| `get_user` | [Sample](../generated_samples/get_user.py) | - |
| `list_users` | [Sample](../generated_samples/list_users.py) | [README snippets](sample_readme_snippets.py) |
| `delete_user` | [Sample](../generated_samples/delete_user.py) | - |
| `list_rooms_for_user` | [Sample](../generated_samples/list_rooms_for_user.py) | [README snippets](sample_readme_snippets.py) |
| `create_or_replace_topic` | [Sample](../generated_samples/create_or_replace_topic.py) | [README snippets](sample_readme_snippets.py) |
| `get_topic` | [Sample](../generated_samples/get_topic.py) | [README snippets](sample_readme_snippets.py) |
| `list_topics` | [Sample](../generated_samples/list_topics.py) | [README snippets](sample_readme_snippets.py) |
| `update_topic` | [Sample](../generated_samples/update_topic.py) | [README snippets](sample_readme_snippets.py) |
| `delete_topic` | [Sample](../generated_samples/delete_topic.py) | [README snippets](sample_readme_snippets.py) |
| `get_conversation` | [Sample](../generated_samples/get_conversation.py) | - |
| `list_messages` | [Sample](../generated_samples/list_messages.py) | [README snippets](sample_readme_snippets.py) |
| `update_message` | [Sample](../generated_samples/update_message.py) | [Message management](sample_message_management.py) |
| `delete_message` | [Sample](../generated_samples/delete_message.py) | [Message management](sample_message_management.py) |

The synchronous and asynchronous clients expose the same service operations.
Await asynchronous non-paging calls, and use `async for` to iterate asynchronous
paged results.
