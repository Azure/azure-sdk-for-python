# Release History

## 1.0.0b4 (Unreleased)

### Features Added

- **Audio Format Improvements**: Reorganized audio format enums with separate `InputAudioFormat` and `OutputAudioFormat` enums for better clarity
- **Enhanced Output Audio Format Support**: Added more granular output audio format options including specific sampling rates (8kHz, 16kHz) for PCM16

### Breaking Changes

- **Model Cleanup**: Removed experimental classes `AzurePlatformVoice`, `LLMVoice`, `AzureSemanticVadServer`, `InputAudio`, `NoTurnDetection`, and `ToolChoiceFunctionObjectFunction`
- **Enum Reorganization**:
  - Replaced `AudioFormat` enum with separate `InputAudioFormat` and `OutputAudioFormat` enums
  - Removed `Phi4mmVoice` enum
  - Removed `EMOTION` value from `AnimationOutputType` enum
  - Removed `IN_PROGRESS` value from `ItemParamStatus` enum
- **Server Events**: Removed `RESPONSE_EMOTION_HYPOTHESIS` from `ServerEventType` enum

### Other Changes

- **Package Configuration**: Updated package structure and build configuration in pyproject.toml
- **Sample Updates**: Improved async function calling sample and basic voice assistant async sample
- **Code Optimization**: Streamlined model definitions with significant code reduction

## 1.0.0b3 (2025-09-17)

### Features Added

- **Transcription improvement**: Added phrase list
- **New Voice Types**: Added `AzurePlatformVoice` and `LLMVoice` classes
- **Enhanced Speech Detection**: Added `AzureSemanticVadServer` class
- **Improved Function Calling**: Enhanced async function calling sample with better error handling
- **English-Specific Detection**: Added `AzureSemanticDetectionEn` class for optimized English-only semantic end-of-utterance detection
- **English-Specific Voice Activity Detection**: Added `AzureSemanticVadEn` class for enhanced English-only voice activity detection

### Breaking Changes

- **Transcription**: Removed `custom_model` and `enabled` from `AudioInputTranscriptionSettings`.
- **Async Authentication**: Fixed credential handling for async scenarios
- **Model Serialization**: Improved error handling and deserialization

### Other Changes

- **Code Modernization**: Updated type annotations throughout

## 1.0.0b2 (2025-09-10)

### Features Added

- Async function call

### Bugs Fixed

- Fixed function calling: ensure `FunctionCallOutputItem.output` is properly serialized as a JSON string before sending to the service.

## 1.0.0b1 (2025-08-28)

### Features Added

- Added WebSocket connection support through `connect()`.
- Added `VoiceLiveConnection` for managing WebSocket connections.
- Added models of Voice Live preview.
- Added WebSocket-based examples in the samples directory.

### Other Changes

- Initial preview release.
