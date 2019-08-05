# Release History

## 1.0.0b2
Breaking changes:
- Removed `Configuration` from the public API in prepration for entirely
kwargs-based configuration. Static `create_config` methods have been renamed
`_create_config`, and will be removed entirely in a future release.
- This version of the library requires [`azure-core`](https://pypi.org/project/azure-core/)
1.0.0b2 and [MSAL](https://pypi.org/project/msal/) 0.4.1

New credentials:
- Added credentials for authenticating users:
[`DeviceCodeCredential`](https://azure.github.io/azure-sdk-for-python/ref/azure.identity.html#azure.identity.DeviceCodeCredential),
[`InteractiveBrowserCredential`](https://azure.github.io/azure-sdk-for-python/ref/azure.identity.html#azure.identity.InteractiveBrowserCredential),
[`UsernamePasswordCredential`](https://azure.github.io/azure-sdk-for-python/ref/azure.identity.html#azure.identity.UsernamePasswordCredential)
  - async versions of these credentials will be added in a future release

## 1.0.0b1 (2019-06-28)
Version 1.0.0b1 is the first preview of our efforts to create a user-friendly
and Pythonic authentication API for Azure SDK client libraries. For more
information about preview releases of other Azure SDK libraries, please visit
https://aka.ms/azure-sdk-preview1-python.

This release supports service principal and managed identity authentication.
See the
[documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md)
for more details. User authentication will be added in an upcoming preview
release.

This release supports only global Azure Active Directory tenants, i.e. those
using the https://login.microsoftonline.com authentication endpoint.
