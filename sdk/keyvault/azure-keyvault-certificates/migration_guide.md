# Guide for migrating to azure-keyvault-certificates from azure-keyvault

This guide is intended to assist in the migration to `azure-keyvault-certificates` from `azure-keyvault`. It will focus on side-by-side comparisons for similar operations between the two packages.

Familiarity with the `azure-keyvault` package is assumed. For those new to the Key Vault client library for Python, please refer to the [README for `azure-keyvault-certificates`](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-certificates/README.md) rather than this guide.

## Table of contents

* [Migration benefits](#migration-benefits)
* [Important changes](#important-changes)
    - [Separate packages and clients](#separate-packages-and-clients)
    - [Client constructors](#client-constructors)
    - [Async operations](#async-operations)
    - [Create a certificate](#create-a-certificate)
    - [Retrieve a certificate](#retrieve-a-certificate)
    - [List properties of certificates](#list-properties-of-certificates)
    - [Delete a certificate](#delete-a-certificate)
* [Additional samples](#additional-samples)

## Migration benefits

A natural question to ask when considering whether or not to adopt a new version or library is what the benefits of doing so would be. As Azure has matured and been embraced by a more diverse group of developers, we have been focused on learning the patterns and practices to best support developer productivity and to understand the gaps that the Python client libraries have.

There were several areas of consistent feedback expressed across the Azure client library ecosystem. One of the most important is that the client libraries for different Azure services have not had a consistent approach to organization, naming, and API structure. Additionally, many developers have felt that the learning curve was difficult, and the APIs did not offer a good, approachable, and consistent onboarding story for those learning Azure or exploring a specific Azure service.

To try and improve the development experience across Azure services, a set of uniform [design guidelines](https://azure.github.io/azure-sdk/python/guidelines/index.html) was created for all languages to drive a consistent experience with established API patterns for all services. A set of [Python-specific guidelines](https://azure.github.io/azure-sdk/python_design.html) was also introduced to ensure that Python clients have a natural and idiomatic feel with respect to the Python ecosystem. Further details are available in the guidelines for those interested.

### Cross Service SDK improvements

The modern Key Vault client library also provides the ability to share in some of the cross-service improvements made to the Azure development experience, such as
- using the new [`azure-identity`](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md) library to share a single authentication approach between clients
- a unified logging and diagnostics pipeline offering a common view of the activities across each of the client libraries

## Important changes

### Separate packages and clients

In the interest of simplifying the API `azure-keyvault` and `KeyVaultClient` were split into separate packages and clients:

- `azure-keyvault-certificates` contains `CertificateClient` for working with certificates.
- [`azure-keyvault-keys`](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-keys/README.md) contains `KeyClient` for working with keys and `CryptographyClient` for performing cryptographic operations.
- [`azure-keyvault-secrets`](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-secrets/README.md) contains `SecretClient` for working with secrets.

### Client constructors

Across all modern Azure client libraries, clients consistently take an endpoint or connection string along with token credentials. This differs from `KeyVaultClient`, which took an authentication delegate and could be used for multiple Key Vault endpoints.

#### Authenticating

Previously in `azure-keyvault` you could create a `KeyVaultClient` by using `ServicePrincipalCredentials` from `azure.common`:

```python
from azure.common.credentials import ServicePrincipalCredentials
from azure.keyvault import KeyVaultClient

credentials = ServicePrincipalCredentials(
    client_id="client id",
    secret="client secret",
    tenant="tenant id"
)

client = KeyVaultClient(credentials)
```

Now in `azure-keyvault-certificates` you can create a `CertificateClient` using any credential from [`azure-identity`](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md). Below is an example using [`DefaultAzureCredential`](https://docs.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential?view=azure-python):

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.certificates import CertificateClient

credential = DefaultAzureCredential()

certificate_client = CertificateClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
```

### Async operations

The modern `azure-keyvault-certificates` library includes a complete async API supported on Python 3.5+. To use it, you must first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/). See [azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#transport) for more information.

Async operations are available on async clients, which should be closed when they're no longer needed. Each async client is an async context manager and defines an async `close` method. For example:

```python
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.certificates.aio import CertificateClient

credential = DefaultAzureCredential()

# call close when the client is no longer needed
certificate_client = CertificateClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
...
await certificate_client.close()

# alternatively, use the client as an async context manager
certificate_client = CertificateClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
async with certificate_client:
  ...
```

### Create a certificate

In `azure-keyvault` you could create a certificate by using `KeyVaultClient`'s `create_certificate` method, which required a vault endpoint and certificate name. This method returned a `CertificateOperation`.

```python
operation = client.create_certificate(
    vault_base_url="https://my-key-vault.vault.azure.net/",
    certificate_name="cert-name"
)
```

Now in `azure-keyvault-certificates` you can use the `begin_create_certificate` method to create a new certificate or new version of an existing certificate with the specified name. Before creating a certificate, a management policy for the certificate can be created or a default policy can be used. This method returns a long running operation poller that can be used to check the status or result of the operation.

```python
create_certificate_poller = certificate_client.begin_create_certificate(
    certificate_name="cert-name",
    policy=CertificatePolicy.get_default()
)

# calling result() will block execution until the certificate creation operation completes
certificate = create_certificate_poller.result()
```

If you would like to check the status of your certificate creation, you can call `status()` on the poller or `get_certificate_operation` with the name of the certificate.

### Retrieve a certificate

In `azure-keyvault` you could retrieve a certificate (as a `CertificateBundle`) by using `get_certificate` and specifying the desired vault endpoint, certificate name, and certificate version. You could retrieve the versions of a certificate with the `get_certificate_versions` method, which returned an iterator-like object.

```python
from azure.keyvault import CertificateId

certificate_items = client.get_certificate_versions(
    vault_base_url="https://my-key-vault.vault.azure.net/",
    certificate_name="cert-name"
)

for certificate_item in certificate_items:
    certificate_id = CertificateId(certificate_item.id)
    certificate_version = certificate_id.version

    certificate = client.get_certificate(
        vault_base_url="https://my-key-vault.vault.azure.net/",
        certificate_name="cert-name",
        certificate_version=certificate_version
    )
```

Now in `azure-keyvault-certificates` you can retrieve the latest version of a certificate (as a `KeyVaultCertificate`) by using `get_certificate` and providing a certificate name.

```python
certificate = certificate_client.get_certificate(certificate_name="cert-name")

print(certificate.name)
print(certificate.properties.version)
print(certificate.policy.issuer_name)
```

You can use `get_certificate_version` to retrieve a specific version of a certificate.

```python
certificate = certificate_client.get_certificate_version(certificate_name="cert-name", version="cert-version")
```

### List properties of certificates

In `azure-keyvault` you could list the properties of certificates in a specified vault with the `get_certificates` method. This returned an iterator-like object containing `CertificateItem` instances.

```python
certificates = client.get_certificates(vault_base_url="https://my-key-vault.vault.azure.net/")

for certificate in certificates:
    print(certificate.attributes.created)
    print(certificate.x509_thumbprint)
```

Now in `azure-keyvault-certificates` you can list the properties of certificates in a vault with the `list_properties_of_certificates` method. This returns an iterator-like object containing `CertificateProperties` instances.

```python
certificates = certificate_client.list_properties_of_certificates()

for certificate in certificates:
    print(certificate.name)
    print(certificate.x509_thumbprint)
```

### Delete a certificate

In `azure-keyvault` you could delete all versions of a certificate with the `delete_certificate` method. This returned information about the deleted certificate (as a `DeletedCertificateBundle`), but you could not poll the deletion operation to know when it completed. This would be valuable information if you intended to permanently delete the deleted certificate with `purge_deleted_certificate`.

```python
deleted_certificate = client.delete_certificate(
    vault_base_url="https://my-key-vault.vault.azure.net/",
    certificate_name="cert-name"
)

# this purge would fail if deletion hadn't finished
client.purge_deleted_certificate(
    vault_base_url="https://my-key-vault.vault.azure.net/",
    certificate_name="cert-name"
)
```

Now in `azure-keyvault-certificates` you can delete a certificate with `begin_delete_certificate`, which returns a long operation poller object that can be used to wait/check on the operation. Calling `result()` on the poller will return information about the deleted certificate (as a `DeletedCertificate`) without waiting for the operation to complete, but calling `wait()` will wait for the deletion to complete. Again, `purge_deleted_certificate` will permanently delete your deleted certificate and make it unrecoverable.

```python
deleted_certificate_poller = certificate_client.begin_delete_certificate(certificate_name="cert-name")
deleted_certificate = deleted_certificate_poller.result()

deleted_certificate_poller.wait()
certificate_client.purge_deleted_certificate(certificate_name="cert-name")
```

## Additional samples

* [Key Vault certificates samples for Python](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-certificates/samples)
* [General Key Vault samples for Python](https://docs.microsoft.com/samples/browse/?products=azure-key-vault&languages=python)
