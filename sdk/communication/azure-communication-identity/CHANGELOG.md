# Release History

## 1.0.0-beta.5 (Unreleased)

### Breaking
- CommunicationIdentityClient's (synchronous and asynchronous) `issue_token` function is now renamed to `get_token`.

## 1.0.0b4 (2021-02-09)

### Added
- Added CommunicationIdentityClient (originally was part of the azure.communication.administration package).
- Added ability to create a user and issue token for it at the same time.

### Breaking
- CommunicationIdentityClient.revoke_tokens now revoke all the currently issued tokens instead of revoking tokens issued prior to a given time.
- CommunicationIdentityClient.issue_tokens returns an instance of `azure.core.credentials.AccessToken` instead of `CommunicationUserToken`.

<!-- LINKS -->
[read_me]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/communication/azure-communication-identity/README.md
[documentation]: https://docs.microsoft.com/azure/communication-services/quickstarts/access-tokens?pivots=programming-language-python