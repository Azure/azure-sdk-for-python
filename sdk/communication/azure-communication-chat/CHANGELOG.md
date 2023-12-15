# Release History

## 1.2.1 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

## 1.2.0 (2023-12-04)

### Features Added

- Added the support to receive inline images from Microsoft Teams users in an interoperability Chat with new type `ChatAttachment`
- Added support for proactive refreshing of tokens
- `CommunicationTokenCredential` exposes a new boolean keyword argument `proactive_refresh` that defaults to `False`. If set to `True`, the refreshing of the token will be scheduled in the background ensuring continuous authentication state.
- Added disposal function `close` for `CommunicationTokenCredential`.
- Added `identifier_from_raw_id` and ensured that `CommunicationIdentifier.raw_id` is populated on creation. Together, these can be used to translate between a `CommunicationIdentifier` and its underlying canonical raw ID representation. Developers can now use the raw ID as an encoded format for identifiers to store in their databases or as stable keys in general.

### Bugs Fixed

- Fixed bug where invalid participants were not being correctly deserialized in the response of `create_chat_thread`.

### Other Changes

Python 2.7 is no longer supported. Please use Python version 3.7 or later. For more details, please read our page on [Azure SDK for Python version support policy](https://github.com/Azure/azure-sdk-for-python/wiki/Azure-SDKs-Python-version-support-policy).

## 1.1.0 (2021-09-15)

- Updated `azure-communication-chat` version.

## 1.1.0b1 (2021-08-16)

### Added

- Added support to add `metadata` for `message`
- Added support to add `sender_display_name` for `ChatThreadClient.send_typing_notification`

## 1.0.0 (2021-03-29)

### Breaking Changes

- Renamed `ChatThread` to `ChatThreadProperties`.
- Renamed `get_chat_thread` to `get_properties`.
- Moved `get_properties` under `ChatThreadClient`.
- Renamed `ChatThreadInfo` to `ChatThreadItem`.
- Removed `ChatThreadClient.add_participant` method.
- Renamed `repeatability_request_id` to `idempotency_token`.
- Changed return type of `send_message` to `SendChatMessageResult`.
- Replaced `CommunicationError` with `ChatError`.
- Refactored `CommunicationTokenCredential` constructor to accept `token` instead of `CommunicationTokenRefreshOptions`.
- Renamed `ChatThreadParticipant` to `ChatParticipant`.
- Renamed attribute `ChatParticipant.user` to `ChatParticipant.identifier`.
- Renamed argument `user` to `identifier` in `ChatThreadClient.remove_participant`.
- Refactored implementation of `CommunicationUserIdentifier`, `PhoneNumberIdentifier`, `MicrosoftTeamsUserIdentifier`, `UnknownIdentifier` to use a `dict` property bag.

## 1.0.0b5 (2021-03-09)

### Breaking Changes

- Added support for communication identifiers instead of raw strings.
- Changed return type of `create_chat_thread`: `ChatThreadClient -> CreateChatThreadResult`
- Changed return types `add_participants`: `None -> list[(ChatThreadParticipant, CommunicationError)]`
- Added check for failure in `add_participant`
- Dropped support for Python 3.5

### Added

- Removed nullable references from method signatures.

## 1.0.0b4 (2021-02-09)

### Breaking Changes

- Uses `CommunicationUserIdentifier` and `CommunicationIdentifier` in place of `CommunicationUser`, and `CommunicationTokenCredential` instead of `CommunicationUserCredential`.
- Removed priority field (ChatMessage.Priority).
- Renamed PhoneNumber to PhoneNumberIdentifier.

### Added

- Support for CreateChatThreadResult and AddChatParticipantsResult to handle partial errors in batch calls.
- Added idempotency identifier parameter for chat creation calls.
- Added support for readreceipts and getparticipants pagination.
- Added new model for messages anc ontent types : Text, Html, ParticipantAdded, ParticipantRemoved, TopicUpdated.
- Added new model for errors (CommunicationError).
- Added `MicrosoftTeamsUserIdentifier`.

## 1.0.0b3 (2020-11-16)

- Updated `azure-communication-chat` version.

## 1.0.0b2 (2020-10-06)

- Updated `azure-communication-chat` version.

## 1.0.0b1 (2020-09-22)

- Add ChatClient and ChatThreadClient.
