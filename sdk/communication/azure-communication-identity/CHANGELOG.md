# Release History

## 1.4.0b2 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

## 1.4.0b1 (2023-04-05)

### Features Added
- Added support for a new communication identifier `MicrosoftBotIdentifier`.

## 1.3.1 (2022-10-28)

### Bug Fixes

- Fixed the logic of `PhoneNumberIdentifier` to always maintain the original phone number string whether it included the leading + sign or not.

## 1.3.0 (2022-10-13)

### Features Added

- Added support to customize the Communication Identity access token's validity period:
    - `create_user_and_token` and `get_token` methods in both sync and async clients can now accept keyword argument `token_expires_in: ~datetime.timedelta` that provides the ability to create a Communication Identity access token with custom expiration.
- Added a new API version `ApiVersion.V2022_10_01` that is now the default API version.
- Added the ability specify the API version by an optional `api_version` keyword parameter.

## 1.2.0 (2022-08-24)

### Features Added

- Exported types `MicrosoftTeamsUserIdentifier`, `PhoneNumberIdentifier`, `UnknownIdentifier` for non Azure Communication Services `CommunicationIdentifier` identities. Exported related types: `MicrosoftTeamsUserProperties` and `PhoneNumberProperties`.
- Added `identifier_from_raw_id` and ensured that `CommunicationIdentifier.raw_id` is populated on creation. Together, these can be used to translate between a `CommunicationIdentifier` and its underlying canonical raw ID representation. Developers can now use the raw ID as an encoded format for identifiers to store in their databases or as stable keys in general.

## 1.1.0 (2022-08-01)

### Features Added

- Added support to integrate communication as Teams user with Azure Communication Services:
    - Added `get_token_for_teams_user(aad_token, client_id, user_object_id)` method that provides the ability to exchange an Azure AD access token of a Teams user for a Communication Identity access token to `CommunicationIdentityClient`.
- Removed `ApiVersion.V2021_10_31_preview` from API versions.
- Added a new API version `ApiVersion.V2022_06_01` that is now the default API version

### Other Changes
- Python 2.7 is no longer supported. Please use Python version 3.7 or later. For more details, please read our page on [Azure SDK for Python version support policy](https://github.com/Azure/azure-sdk-for-python/wiki/Azure-SDKs-Python-version-support-policy).

## 1.1.0b1 (2021-11-09)

### Features Added

- Added support to integrate communication as Teams user with Azure Communication Services:
  - `CommunicationIdentityClient` added a new method `get_token_for_teams_user` that provides the ability to exchange an Azure AD access token of a Teams user for a Communication Identity access token

## 1.0.1 (2021-06-08)

### Bug Fixes

- Fixed async client to use async bearer token credential policy instead of sync policy.

## 1.0.0 (2021-03-29)

- Stable release of `azure-communication-identity`.

## 1.0.0b5 (2021-03-09)

### Breaking

- CommunicationIdentityClient's (synchronous and asynchronous) `issue_token` function is now renamed to `get_token`.
- The CommunicationIdentityClient constructor uses type `TokenCredential` and `AsyncTokenCredential` for the credential parameter.
- Dropped support for 3.5

## 1.0.0b4 (2021-02-09)

### Added

- Added CommunicationIdentityClient (originally was part of the azure.communication.administration package).
- Added ability to create a user and issue token for it at the same time.

### Breaking

- CommunicationIdentityClient.revoke_tokens now revoke all the currently issued tokens instead of revoking tokens issued prior to a given time.
- CommunicationIdentityClient.issue_tokens returns an instance of `azure.core.credentials.AccessToken` instead of `CommunicationUserToken`.

<!-- LINKS -->

[read_me]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/communication/azure-communication-identity/README.md
[documentation]: https://docs.microsoft.com/azure/communication-services/quickstarts/access-tokens?pivots=programming-language-python
