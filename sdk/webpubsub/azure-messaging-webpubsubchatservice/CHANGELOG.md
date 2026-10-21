# Release History

## 1.0.0b2 (Unreleased)

### Features Added

  - Added topic lifecycle operations (create or replace, list, get, update, and soft delete)
  - Added room, user, and user-room collection operations

### Other Changes

  - Changed the default service API version from `2026-02-01-preview` to `2026-08-01-preview` for both existing and newly added Chat operations

### Breaking Changes

  - Create or replace operations now accept dedicated `ChatRoleCreateOrReplace`, `ChatRoomCreateOrReplace`, `ChatRoomMemberCreateOrReplace`, and `ChatUserCreateOrReplace` (including `HumanChatUserCreateOrReplace`) request models instead of resource response models.
  - Topic creation or replacement accepts `ChatTopicCreateOrReplace`, which requires only `title`. Topic updates accept `ChatTopicUpdate`, whose fields are optional.
  - Message updates accept `ChatMessageUpdate`, whose fields are optional, instead of `ChatMessage`. Resource response model names are unchanged.

## 1.0.0b1 (2026-10-08)

### Features Added

  - Initial preview release of the Azure Web PubSub Chat Service client library for Python
  - Added connection string, access key, and Microsoft Entra ID authentication
  - Added client access token generation for connected Chat clients
  - Added built-in Chat role and permission constants
  - Support for room management (create, get, update, delete rooms)
  - Support for user management (create, get, delete users)
  - Support for room membership management (add, list, delete room members)
  - Support for message operations (list, update, delete messages)
  - Support for role-based access control (create, get, list, delete roles)
