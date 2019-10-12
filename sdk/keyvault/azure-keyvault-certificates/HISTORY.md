# Release History

## 4.0.0b5
### Breaking changes
- Removed redundant method `get_pending_certificate_signing_request()`. A pending CSR can be retrieved via `get_certificate_operation()`.
- Renamed `create_certificate` to `begin_create_certificate`

## 4.0.0b4 (2019-10-08)
### Breaking changes
- Enums `JsonWebKeyCurveName` and `JsonWebKeyType` have been renamed to `KeyCurveName` and `KeyType`, respectively.
- Both async and sync versions of `create_certificate` now return pollers that return the created `Certificate` if creation is successful,
and a `CertificateOperation` if not.
- `Certificate` now has attribute `properties`, which holds certain properties of the
certificate, such as `version`. This changes the shape of the `Certificate` type,
as certain properties of `Certificate` (such as `version`) have to be accessed
through the `properties` property. See the updated [docs](https://azure.github.io/azure-sdk-for-python/ref/azure.keyvault.certificates.html)
for details.
- `update_certificate` has been renamed to `update_certificate_properties`
- The `vault_url` parameter of `CertificateClient` has been renamed to `vault_endpoint`
- The property `vault_url` has been renamed to `vault_endpoint` in all models


## 4.0.0b3 (2019-09-11)
Version 4.0.0b3 is the first preview of our efforts to create a user-friendly and Pythonic client library for Azure Key Vault's certificates.

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
- Authentication using `azure-identity` credentials
  - see this package's
  [documentation](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys/README.md)
  , and the
  [Azure Identity documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md)
  for more information

### New Features:
- Distributed tracing framework OpenCensus is now supported
- Asynchronous API supported on Python 3.5.3+
    - the `azure.keyvault.certificates.aio` namespace contains an async equivalent of
    the synchronous client in `azure.keyvault.certificates`
    - Async clients use [aiohttp](https://pypi.org/project/aiohttp/) for transport
    by default. See [azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md/#transport)
    for more information about using other transports.
