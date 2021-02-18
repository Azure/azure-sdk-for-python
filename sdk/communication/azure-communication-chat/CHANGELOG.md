# Release History

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
