# Release History

## 1.1.0 (2025-11-03)

### Features Added

- Added support for Agent configuration through the new `AgentConfig` model
- Added `agent` field to `ResponseSession` model to support agent-based conversations
- The `AgentConfig` model includes properties for agent type, name, description, agent_id, and thread_id

## 1.1.0b1 (2025-10-06)

### Features Added

- **AgentConfig Support**: Re-introduced `AgentConfig` functionality with enhanced capabilities:
  - `AgentConfig` model added back to public API with full import and export support
  - `agent` field re-added to `ResponseSession` model for session-level agent configuration
  - Updated cross-language package mappings to include `AgentConfig` support
  - Provides foundation for advanced agent configuration scenarios

## 1.0.0 (2025-10-01)

### Features Added

- **Enhanced WebSocket Connection Options**: Significantly improved WebSocket connection configuration with transport-agnostic design:
  - Added new timeout configuration options: `receive_timeout`, `close_timeout`, and `handshake_timeout` for fine-grained control
  - Enhanced `compression` parameter to support both boolean and integer types for advanced zlib window configuration
  - Added `vendor_options` parameter for implementation-specific options passthrough (escape hatch for advanced users)
  - Improved documentation with clearer descriptions for all connection parameters
  - Better support for common aliases from other WebSocket ecosystems (`max_size`, `ping_interval`, etc.)
  - More robust option mapping with proper type conversion and safety checks
- **Enhanced Type Safety**: Improved type safety for content parts with proper enum usage:
  - `InputAudioContentPart`, `InputTextContentPart`, and `OutputTextContentPart` now use `ContentPartType` enum values instead of string literals
  - Better IntelliSense support and compile-time type checking for content part discriminators

### Breaking Changes

- **Improved Naming Conventions**: Updated model and enum names for better clarity and consistency:
  - `OAIVoice` enum renamed to `OpenAIVoiceName` for more descriptive naming
  - `ToolChoiceObject` model renamed to `ToolChoiceSelection` for better semantic meaning
  - `ToolChoiceFunctionObject` model renamed to `ToolChoiceFunctionSelection` for consistency
  - Updated type unions and imports to reflect the new naming conventions
  - Cross-language package mappings updated to maintain compatibility across SDKs
- **Session Model Architecture**: Separated `ResponseSession` and `RequestSession` models for better design clarity:
  - `ResponseSession` no longer inherits from `RequestSession` and now inherits directly from `_Model`
  - All session configuration fields are now explicitly defined in `ResponseSession` instead of being inherited
  - This provides clearer separation of concerns between request and response session configurations
  - May affect type checking and code that relied on the previous inheritance relationship
- **Model Cleanup**: Removed unused `AgentConfig` model and related fields from the public API:
  - `AgentConfig` class has been completely removed from imports and exports
  - `agent` field removed from `ResponseSession` model (including constructor parameter)
  - Updated cross-language package mappings to reflect the removal
- **Model Naming Convention Update**: Renamed `EOUDetection` to `EouDetection` for better naming consistency:
  - Class name changed from `EOUDetection` to `EouDetection` 
  - All inheritance relationships updated: `AzureSemanticDetection`, `AzureSemanticDetectionEn`, and `AzureSemanticDetectionMultilingual` now inherit from `EouDetection`
  - Type annotations updated in `AzureSemanticVad`, `AzureSemanticVadEn`, `AzureSemanticVadMultilingual`, and `ServerVad` classes
  - Import statements and exports updated to reflect the new naming
- **Enhanced Content Part Type Safety**: Content part discriminators now use enum values instead of string literals:
  - `InputAudioContentPart.type` now uses `ContentPartType.INPUT_AUDIO` instead of `"input_audio"`
  - `InputTextContentPart.type` now uses `ContentPartType.INPUT_TEXT` instead of `"input_text"`  
  - `OutputTextContentPart.type` now uses `ContentPartType.TEXT` instead of `"text"`

### Other Changes

- Initial GA release

## 1.0.0b5 (2025-09-26)

### Features Added

- **Enhanced Semantic Detection Type Safety**: Added new `EouThresholdLevel` enum for better type safety in end-of-utterance detection:
  - `LOW` for low sensitivity threshold level
  - `MEDIUM` for medium sensitivity threshold level  
  - `HIGH` for high sensitivity threshold level
  - `DEFAULT` for default sensitivity threshold level
- **Improved Semantic Detection Configuration**: Enhanced semantic detection classes with better type annotations:
  - `threshold_level` parameter now supports both string values and `EouThresholdLevel` enum
  - Cleaner type definitions for `AzureSemanticDetection`, `AzureSemanticDetectionEn`, and `AzureSemanticDetectionMultilingual`
  - Improved documentation for threshold level parameters
- **Comprehensive Unit Test Suite**: Added extensive unit test coverage with 200+ test cases covering:
  - All enum types and their functionality
  - Model creation, validation, and serialization
  - Async connection functionality with proper mocking
  - Client event handling and workflows
  - Voice configuration across all supported types
  - Message handling with content part hierarchy
  - Integration scenarios and real-world usage patterns
  - Recent changes validation and backwards compatibility
- **API Version Update**: Updated to API version `2025-10-01` (from `2025-05-01-preview`)
- **Enhanced Type Safety**: Added new `AzureVoiceType` enum with values for better Azure voice type categorization:
  - `AZURE_CUSTOM` for custom voice configurations
  - `AZURE_STANDARD` for standard voice configurations  
  - `AZURE_PERSONAL` for personal voice configurations
- **Improved Message Handling**: Added `MessageRole` enum for better role type safety in message items
- **Enhanced Model Documentation**: Comprehensive documentation improvements across all models:
  - Added detailed docstrings for model classes and their parameters
  - Enhanced enum value documentation with descriptions
  - Improved type annotations and parameter descriptions
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

- **Cross-Language Package Identity Update**: Updated package ID from `VoiceLive` to `VoiceLive.WebSocket` for better cross-language consistency
- **Model Refactoring**: 
  - Renamed `UserContentPart` to `MessageContentPart` for clearer content part hierarchy
  - All message items now require a `content` field with list of `MessageContentPart` objects
  - `OutputTextContentPart` now inherits from `MessageContentPart` instead of being standalone
- **Enhanced Type Safety**: 
  - Azure voice classes now use `AzureVoiceType` enum discriminators instead of string literals
  - Message role discriminators now use `MessageRole` enum values for better type safety
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
- **Model Rename**:
  - Renamed `AudioInputTranscriptionSettings` to `AudioInputTranscriptionOptions` for consistency with naming conventions
  - Renamed `AzureMultilingualSemanticVad` to `AzureSemanticVadMultilingual` for naming consistency with other multilingual variants
- **Enhanced Type Safety**: Turn detection discriminator types now use enum values instead of string literals for better type safety

### Bug Fixes

- **Serialization Improvements**: Fixed type casting issue in serialization utilities for better enum handling and type safety

### Other Changes

- **Testing Infrastructure**: Added comprehensive unit test suite with extensive coverage:
  - 8 main test files with 200+ individual test methods
  - Tests for all enums, models, async operations, client events, voice configurations, and message handling
  - Integration tests covering real-world scenarios and recent changes
  - Proper mocking for async WebSocket connections
  - Backwards compatibility validation
  - Test coverage for all recent changes and enhancements
- **API Documentation**: Updated API view properties to reflect model structure changes, new enums, and cross-language package identity
- **Documentation Updates**: Comprehensive updates to all markdown documentation:
  - Updated README.md to reflect async-only nature with updated examples and installation instructions
  - Updated samples README.md to remove sync sample references
  - Enhanced BASIC_VOICE_ASSISTANT.md with comprehensive async implementation guide
  - Added MIGRATION_GUIDE.md for users upgrading from previous versions

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
