# Release History

## 1.4.0b2 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

## 1.4.0b1 (2024-11-22)

### Features Added

- Added support for ConnectAPI to enable streaming and real-time transcription
- Enhanced media streaming with bidirectional capabilities, enabling support for audio formats in both directions. Currently, it supports sample rates of 24kHz and 16kHz

### Other Changes

- Introduced audio streaming and transcription data parsing capabilities.

## 1.3.0 (2024-11-22)

### Features Added

- Support multiple play sources for Play and Recognize
- Support for PlayStarted event in Play/Recognize
- Hold and Unhold the participant
- CallDisconnected now includes more information on why the call has ended
- Support to manage the rooms/servercall/group call using connect API
- Expose original PSTN number target from incoming call event in call connection properties
- Support for VoIP to PSTN transfer scenario

### Other Changes

- Added CreateCallFailed event to signify when create call API fails to establish a call
- Added AnswerFailed event to signify when answer call API fails to answer a call

## 1.3.0b2 (2024-10-28)

### Features Added

- Added CreateCallFailed event to signify when create call API fails to establish a call

## 1.3.0b1 (2024-08-02)

### Features Added

- Support multiple play sources for Play and Recognize
- Support for PlayStarted event in Play/Recognize
- Support for the real time transcription
- Monetization for real-time transcription and audio streaming
- Hold and Unhold the participant
- Support to manage the rooms/servercall/group call using connect API
- Support for the audio streaming
- Expose original PSTN number target from incoming call event in call connection properties
- Support for VoIP to PSTN transfer scenario

## 1.2.0 (2024-04-15)

### Features Added

- Support for Bring Your Own Storage recording option
- Support for PauseOnStart recording option 
- Support for Recording state change with new recording kind's

### Other Changes
- Support for MicrosoftTeamsAppIdentifier CommunicationIdentifier

## 1.1.0 (2023-11-23)
### Features Added
- Mid Call actions support overriding callback url.
- Cancel adding Participant invitation.
- Support transfer a participant in a group call to another participant.
- Add Custom Context payload to Transfer and AddParticipant API.

## 1.1.0b1 (2023-08-17)
### Features Added
- Play and recognize supports TTS and SSML source prompts.
- Recognize supports choices and freeform speech.
- Start/Stop continuous DTMF recognition by subscribing/unsubscribing to tones.
- Send DTMF tones to a participant in the call.
- Mute participants in the call.

### Other Changes
- The models `ServerCallLocator` and `GroupCallLocator` have been deprecated, and the ID values can now be passed directly into `CallAutomationClient.start_recording` as keyword arguments.
- The model `CallInvite` has been deprecated and now the target `CommunicationIdentifier` and associated properties can be passed directly into `create_call`, `redirect_call` and `add_participant`.
- The method `CallAutomationClient.create_group_call` has been deprecated, this can now be achieved by passing a list of `CommunicationIdentifier`s into `create_call`.
- The method `CallConnectionClient.play_media_to_all` has been deprecated, this can now be achieved as the default behaviour of `play_media`.
- The `MicrosoftBotIdentifier` has been deprecated.

## 1.0.0 (2023-06-14)
Call Automation enables developers to build call workflows. Personalise customer interactions by listening to call events and take actions based on your business logic. For more information, please see the [README][read_me].

### Features Added
- Create outbound calls to an Azure Communication Service user or a phone number.
- Answer/Redirect/Reject incoming call from an Azure Communication Service user or a phone number.
- Transfer the call to another participant.
- List, add or remove participant from the call.
- Hangup or terminate the call.
- Play audio files to one or more participants in the call.
- Recognize incoming DTMF in the call.
- Record calls with option to start/resume/stop.
- Record mixed and unmixed audio recordings.
- Download recordings.

<!-- LINKS -->
[read_me]: https://github.com/Azure/azure-sdk-for-net/blob/main/sdk/communication/Azure.Communication.CallAutomation/README.md
[Overview]: https://learn.microsoft.com/azure/communication-services/concepts/voice-video-calling/call-automation
[Demo Video]: https://ignite.microsoft.com/sessions/14a36f87-d1a2-4882-92a7-70f2c16a306a
[Incoming Call Concept]: https://learn.microsoft.com/azure/communication-services/concepts/voice-video-calling/incoming-call-notification
[Build a customer interaction workflow using Call Automation]: https://learn.microsoft.com/azure/communication-services/quickstarts/voice-video-calling/callflows-for-customer-interactions