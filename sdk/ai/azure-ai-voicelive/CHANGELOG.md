# Release History

## 1.0.0b5 (Unreleased)

### Features Added

- **Enhanced Semantic Detection**: Added improved configuration options for all semantic detection classes:
  - Added `threshold_level` parameter with options: `"low"`, `"medium"`, `"high"`, `"default"` (recommended over deprecated `threshold`)
  - Added `timeout_ms` parameter for timeout configuration in milliseconds (recommended over deprecated `timeout`)
- **Video Background Support**: Added new `Background` model for video background customization:
  - Support for solid color backgrounds in hex format (e.g., `#00FF00FF`)
  - Support for image URL backgrounds
  - Mutually exclusive color and image URL options
- **Enhanced Video Parameters**: Extended `VideoParams` model with:
  - `background` parameter for configuring video backgrounds using the new `Background` model
  - `gop_size` parameter for Group of Pictures (GOP) size control, affecting compression efficiency and seeking performance
- **Improved Type Safety**: Added `TurnDetectionType` enum for better type safety and IntelliSense support
- **Package Structure Modernization**: Simplified package initialization with namespace package support
- **Enhanced Error Handling**: Added `ConnectionError` and `ConnectionClosed` exception classes to the async API for better WebSocket error management

### Breaking Changes

- **Removed Deprecated Parameters**: Completely removed deprecated parameters from semantic detection classes:
  - Removed `threshold` parameter from all semantic detection classes (`AzureSemanticDetection`, `AzureSemanticDetectionEn`, `AzureSemanticDetectionMultilingual`)
  - Removed `timeout` parameter from all semantic detection classes
  - Users must now use `threshold_level` and `timeout_ms` parameters respectively
- **Removed Synchronous API**: Completely removed synchronous WebSocket operations to focus exclusively on async patterns:
  - Removed sync `connect()` function and sync `VoiceLiveConnection` class from main patch implementation
  - Removed sync `basic_voice_assistant.py` sample (only async version remains)
  - Simplified sync patch to minimal structure with empty exports
  - All functionality now available only through async patterns
- **Updated Dependencies**: Modified package dependencies to reflect async-only architecture:
  - Moved `aiohttp>=3.9.0,<4.0.0` from optional to required dependency
  - Removed `websockets` optional dependency as sync API no longer exists
  - Removed optional dependency groups `websockets`, `aiohttp`, and `all-websockets`
- **Model Rename**: Renamed `AzureMultilingualSemanticVad` to `AzureSemanticVadMultilingual` for naming consistency with other multilingual variants
- **Enhanced Type Safety**: Turn detection discriminator types now use enum values instead of string literals for better type safety

### Other Changes

- **Documentation Updates**: Comprehensive updates to all markdown documentation:
  - Updated README.md to reflect async-only nature with updated examples and installation instructions
  - Updated samples README.md to remove sync sample references
  - Enhanced BASIC_VOICE_ASSISTANT.md with comprehensive async implementation guide
  - Added MIGRATION_GUIDE.md for users upgrading from previous versions
- **API Documentation**: Updated API view properties to reflect model structure changes

## 1.0.0b4 (2025-09-19)

### Features Added

- **Personal Voice Models**: Added `PersonalVoiceModels` enum with support for `DragonLatestNeural`, `PhoenixLatestNeural`, and `PhoenixV2Neural` models
- **Enhanced Animation Support**: Added comprehensive server event classes for animation blendshapes and viseme handling:
  - `ServerEventResponseAnimationBlendshapeDelta` and `ServerEventResponseAnimationBlendshapeDone`
  - `ServerEventResponseAnimationVisemeDelta` and `ServerEventResponseAnimationVisemeDone`
- **Audio Timestamp Events**: Added `ServerEventResponseAudioTimestampDelta` and `ServerEventResponseAudioTimestampDone` for better audio timing control
- **Improved Error Handling**: Added `ErrorResponse` class for better error management
- **Enhanced Base Classes**: Added `ConversationItemBase` and `SessionBase` for better code organization and inheritance
- **Token Usage Improvements**: Renamed `Usage` to `TokenUsage` for better clarity
- **Audio Format Improvements**: Reorganized audio format enums with separate `InputAudioFormat` and `OutputAudioFormat` enums for better clarity
- **Enhanced Output Audio Format Support**: Added more granular output audio format options including specific sampling rates (8kHz, 16kHz) for PCM16

### Breaking Changes

- **Model Cleanup**: Removed experimental classes `AzurePlatformVoice`, `LLMVoice`, `AzureSemanticVadServer`, `InputAudio`, `NoTurnDetection`, and `ToolChoiceFunctionObjectFunction`
- **Class Rename**: Renamed `Usage` class to `TokenUsage` for better clarity
- **Enum Reorganization**:
  - Replaced `AudioFormat` enum with separate `InputAudioFormat` and `OutputAudioFormat` enums
  - Removed `Phi4mmVoice` enum
  - Removed `EMOTION` value from `AnimationOutputType` enum
  - Removed `IN_PROGRESS` value from `ItemParamStatus` enum
- **Server Events**: Removed `RESPONSE_EMOTION_HYPOTHESIS` from `ServerEventType` enum

### Other Changes

- **Package Structure**: Simplified package initialization with namespace package support
- **Sample Updates**: Improved basic voice assistant samples
- **Code Optimization**: Streamlined model definitions with significant code reduction
- **API Configuration**: Updated API view properties for better tooling support

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
