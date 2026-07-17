# Release History

## 1.0.1b1 (Unreleased)

### Other Changes

- Documented that `locales` is now honored in Enhanced Mode. The service operates in multilingual mode by default; if specified, the first locale is used as a hint to guide recognition.

## 1.0.0 (2026-05-18)

### Features Added

- First stable release of the Azure AI Transcription client library for Python.

## 1.0.0b4 (2026-04-20)

### Other Changes

- Moved the package to a new service category folder `transcription`.

## 1.0.0b3 (2026-02-04)

### Features Added

- Enhanced Mode now automatically sets `enabled=True` when `task`, `target_language`, or `prompt` are specified

### Bugs Fixed

- Fixed Enhanced Mode not being activated when using `EnhancedModeProperties` without explicitly setting `enabled=True`

## 1.0.0b2 (2025-12-19)

### Bugs Fixed

- Fixed API reference link

## 1.0.0b1 (2025-12-03)

### Other Changes

- Initial version
