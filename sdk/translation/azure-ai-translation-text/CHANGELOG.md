# Release History

## 2.0.0b1 (2026-01-08)

### Features Added

- Added support for the Azure AI Translator API 2025-10-01-preview, including translations using LLM models, adaptive custom translations, tone variant translations, and gender-specific language translations.
- Added `TranslationTarget` for configuring translation options.

### Breaking Changes

- Dictionary, sentence boundaries and text alignments features have been removed, and relevant models and properties have been removed.
- Added `models` property to `GetSupportedLanguagesResult` to include the list of LLM models available for translations.
- Renamed property `confidence` to `score` in `DetectedLanguage`.
- Removed property `source_text` in `TranslatedTextItem`.

## 1.0.1 (2024-06-24)

### Bugs Fixed
  - Fixed a bug where Entra Id authentication couldn't be used with custom endpoint.

## 1.0.0 (2024-05-23)

### Features Added
  - Added support for Entra Id authentication.

### Breaking Changes

  - All calls to the client using parameter `content` have been changed to use parameter `body`.
  - Users can call methods using just a string type instead of complex objects.
  - `get_languages` methods were changed to `get_supported_languages`.
  - renamed `from_parameter` to `from_language`.
  - renamed `to` parameter to `to_language`.

## 1.0.0b1 (2023-04-19)

  - Initial Release
