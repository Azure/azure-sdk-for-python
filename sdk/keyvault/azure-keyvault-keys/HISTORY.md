# Release History

## 4.0.0b2 (2019-08-06)
### Breaking changes:
- Removed `azure.core.Configuration` from the public API in preparation for a
revamped configuration API. Static `create_config` methods have been renamed
`_create_config`, and will be removed in a future release.
- Removed `wrap_key` and `unwrap_key` from `KeyClient`. These are now available
through `CryptographyClient`.
- This version of the library requires `azure-core` 1.0.0b2
  - If you later want to revert to a version requiring azure-core 1.0.0b1,
  of this or another Azure SDK library, you must explicitly install azure-core
  1.0.0b1 as well. For example:
  `pip install azure-core==1.0.0b1 azure-keyvault-keys==4.0.0b1`

### New features:
- Added `CryptographyClient`, a client for performing cryptographic operations
(encrypt/decrypt, wrap/unwrap, sign/verify) with a key.
- Distributed tracing framework OpenCensus is now supported
- Added support for HTTP challenge based authentication, allowing clients to
interact with vaults in sovereign clouds.

### Other changes:
- Async clients use [aiohttp](https://pypi.org/project/aiohttp/) for transport
by default. See
[azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md/#transport)
for more information about using other transports.

## 4.0.0b1 (2019-06-28)
Version 4.0.0b1 is the first preview of our efforts to create a user-friendly
and Pythonic client library for Azure Key Vault. For more information about
preview releases of other Azure SDK libraries, please visit
https://aka.ms/azure-sdk-preview1-python.

This library is not a direct replacement for `azure-keyvault`. Applications
using that library would require code changes to use `azure-keyvault-keys`.
This package's
[documentation](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys/README.md)
and
[samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys/samples)
demonstrate the new API.

### Major changes from `azure-keyvault`
- Packages scoped by functionality
    - `azure-keyvault-keys` contains a client for key operations,
    `azure-keyvault-secrets` contains a client for secret operations
- Client instances are scoped to vaults (an instance interacts with one vault
only)
- Asynchronous API supported on Python 3.5.3+
    - the `azure.keyvault.keys.aio` namespace contains an async equivalent of
    the synchronous client in `azure.keyvault.keys`
- Authentication using `azure-identity` credentials
  - see this package's
  [documentation](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys/README.md)
  , and the
  [Azure Identity documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md)
  for more information

### `azure-keyvault` features not implemented in this release
- Certificate management APIs
- Cryptographic operations, e.g. sign, un/wrap_key, verify, en- and
decrypt
- National cloud support. This release supports public global cloud vaults,
    e.g. https://{vault-name}.vault.azure.net
