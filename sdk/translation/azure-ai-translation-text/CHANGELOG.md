# Release History

## 1.0.1 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

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
