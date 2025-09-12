# Release History

## 1.0.0b3 (Unreleased)

### Features Added

- Phrase list.

### Breaking Changes

- Removed `custom_model` and `enabled` from `AudioInputTranscriptionSettings`.
  - `custom_model` → Use `customSpeech` key–value settings instead.
  - `enabled` → Transcription is enabled by providing `AudioInputTranscriptionSettings` (or by specifying a `model`). Remove this flag.

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
