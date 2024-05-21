# Release History

## 1.0.0 (2024-05-21)

### Features Added
  - Added support for Entra Id authentication.

### Breaking Changes

  - All calls to the client using parameter `content` have been changed to use parameter `body`.
  - Users can call methods using just a string type instead of complex objects.
  - `get_languages` methods were changed to `get_supported_languages`.

## 1.0.0b1 (2023-04-19)

  - Initial Release
