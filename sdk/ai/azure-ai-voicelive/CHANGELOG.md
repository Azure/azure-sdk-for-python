# Release History

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
