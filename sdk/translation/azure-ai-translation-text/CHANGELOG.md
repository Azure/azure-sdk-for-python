# Release History

## 1.0.0 (2024-05-21)

### Features Added
  - Added support for Entra Id authentication.

### Breaking Changes

  - All calls to the client using parameter 'content' have been changed to use parameter 'body'.
  - Users can call methods using just a string type instead of complex objects.
  - get_languages methods were changed to get_supported_languages.
  - sent_len property was renamed to sent_len.
  - from_parameter parameter was renamed to from_parameter.
  - score parameter was renamed to confidence.
  - from_script parameter was renamed to from_script.
  - to_script parameter was renamed to _target_langauge_script.

## 1.0.0b1 (2023-04-19)

  - Initial Release
