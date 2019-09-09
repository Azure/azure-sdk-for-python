# Release History

## 4.0.0b1 (2019-09-09)
Version 4.0.0b1 is the first preview of our efforts to create a user-friendly and Pythonic client library for Azure Key Vault.
For more information about preview releases of other Azure SDK libraries, please visit https://aka.ms/azure-sdk-preview1-python.

 This library is not a direct replacement for `azure-keyvault`. Applications
using that library would require code changes to use `azure-keyvault-certificates`.
This package's
[documentation](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-certificates/README.md)
and
[samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-certificates/samples)
demonstrate the new API.

### Breaking changes from `azure-keyvault`:
- Packages scoped by functionality
    - `azure-keyvault-certificates` contains a client for certificate operations
- Client instances are scoped to vaults (an instance interacts with one vault
only)
- Removed `azure.core.Configuration` from the public API in preparation for a
revamped configuration API. Static `create_config` methods have been renamed
`_create_config`, and will be removed in a future release.
- Authentication using `azure-identity` credentials
  - see this package's
  [documentation](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys/README.md)
  , and the
  [Azure Identity documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md)
  for more information

### New Features:
- Added support for HTTP challenge based authentication, allowing clients to
interact with vaults in sovereign clouds.
- Distributed tracing framework OpenCensus is now supported
- Asynchronous API supported on Python 3.5.3+
    - the `azure.keyvault.certificates.aio` namespace contains an async equivalent of
    the synchronous client in `azure.keyvault.certificates`
    - Async clients use [aiohttp](https://pypi.org/project/aiohttp/) for transport
    by default. See [azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md/#transport)
    for more information about using other transports.
