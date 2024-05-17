# Release History

## 1.0.0 (Unreleased)

### Features Added
  - Added support for Entra Id authentication.

### Breaking Changes

  - All calls to the client using parameter 'content' have been changed to use parameter 'body'.
  - Users can call methods using just a string type instead of complex objects.
  - get_languages methods were changed to get_supported_languages.
  - sent_len property was renamed to sentences_lengths.
  - from_parameter parameter was renamed to source_language.
  - score parameter was renamed to confidence.
  - from_script parameter was renamed to source_language_script.
  - to_script parameter was renamed to _target_langauge_script.

### Bugs Fixed

### Other Changes

## 1.0.0b1 (2023-04-19)

  - Initial Release
