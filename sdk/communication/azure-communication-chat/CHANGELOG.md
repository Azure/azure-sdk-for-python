# Release History

## 1.0.0b6 (Unreleased)
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
