# Guide for migrating to azure-keyvault-secrets from azure-keyvault

This guide is intended to assist in the migration to `azure-keyvault-secrets` from `azure-keyvault`. It will focus on side-by-side comparisons for similar operations between the two packages.

Familiarity with the `azure-keyvault` package is assumed. For those new to the Key Vault client library for Python, please refer to the [README for `azure-keyvault-secrets`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-secrets/README.md) rather than this guide.

## Table of contents

* [Migration benefits](#migration-benefits)
* [Important changes](#important-changes)
    - [Separate packages and clients](#separate-packages-and-clients)
    - [Client constructors](#client-constructors)
    - [Async operations](#async-operations)
    - [Set a secret](#set-a-secret)
    - [Retrieve a secret](#retrieve-a-secret)
    - [List properties of secrets](#list-properties-of-secrets)
    - [Delete a secret](#delete-a-secret)
* [Additional samples](#additional-samples)

## Migration benefits

A natural question to ask when considering whether or not to adopt a new version or library is what the benefits of doing so would be. As Azure has matured and been embraced by a more diverse group of developers, we have been focused on learning the patterns and practices to best support developer productivity and to understand the gaps that the Python client libraries have.

There were several areas of consistent feedback expressed across the Azure client library ecosystem. One of the most important is that the client libraries for different Azure services have not had a consistent approach to organization, naming, and API structure. Additionally, many developers have felt that the learning curve was difficult, and the APIs did not offer a good, approachable, and consistent onboarding story for those learning Azure or exploring a specific Azure service.

To try and improve the development experience across Azure services, a set of uniform [design guidelines](https://azure.github.io/azure-sdk/python/guidelines/index.html) was created for all languages to drive a consistent experience with established API patterns for all services. A set of [Python-specific guidelines](https://azure.github.io/azure-sdk/python_design.html) was also introduced to ensure that Python clients have a natural and idiomatic feel with respect to the Python ecosystem. Further details are available in the guidelines for those interested.

### Cross Service SDK improvements

The modern Key Vault client library also provides the ability to share in some of the cross-service improvements made to the Azure development experience, such as
- using the new [`azure-identity`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md) library to share a single authentication approach between clients
- a unified logging and diagnostics pipeline offering a common view of the activities across each of the client libraries

## Important changes

### Separate packages and clients

In the interest of simplifying the API `azure-keyvault` and `KeyVaultClient` were split into separate packages and clients:

- [`azure-keyvault-certificates`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/README.md) contains `CertificateClient` for working with certificates.
- [`azure-keyvault-keys`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-keys/README.md) contains `KeyClient` for working with keys and `CryptographyClient` for performing cryptographic operations.
- `azure-keyvault-secrets` contains `SecretClient` for working with secrets.

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

Now in `azure-keyvault-secrets` you can create a `SecretClient` using any credential from [`azure-identity`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md). Below is an example using [`DefaultAzureCredential`](https://docs.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential?view=azure-python):

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()

secret_client = SecretClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
```

### Async operations

The modern `azure-keyvault-secrets` library includes a complete async API supported on Python 3.5+. To use it, you must first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/). See [azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#transport) for more information.

Async operations are available on async clients, which should be closed when they're no longer needed. Each async client is an async context manager and defines an async `close` method. For example:

```python
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.secrets.aio import SecretClient

credential = DefaultAzureCredential()

# call close when the client is no longer needed
client = SecretClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
...
await client.close()

# alternatively, use the client as an async context manager
client = SecretClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
async with client:
  ...
```

### Set a secret

In `azure-keyvault` you could set a secret by using `KeyVaultClient`'s `set_secret` method, which required a vault endpoint, secret name, and value. This method returned a `SecretBundle` containing the secret.

```python
secret_bundle = client.set_secret(
    vault_base_url="https://my-key-vault.vault.azure.net/",
    secret_name="secret-name",
    value="secret-value"
)
secret_value = secret_bundle.value
```

Now in `azure-keyvault-secrets` you can set a secret by using `set_secret` with a secret name and value. This returns the created secret (as a `KeyVaultSecret`).

```python
secret = secret_client.set_secret(name="secret-name", value="secret-value")
secret_value = secret.value
```

### Retrieve a secret

In `azure-keyvault` you could retrieve a secret (in a `SecretBundle`) by using `get_secret` and specifying the desired vault endpoint, secret name, and secret version. You could retrieve the versions of a secret with the `get_secret_versions` method, which returned an iterator-like object.

```python
from azure.keyvault import SecretId

secret_items = client.get_secret_versions(
    vault_base_url="https://my-key-vault.vault.azure.net/",
    secret_name="secret-name"
)

for secret_item in secret_items:
    secret_id = SecretId(secret_item.id)
    secret_version = secret_id.version

    secret_bundle = client.get_secret(
        vault_base_url="https://my-key-vault.vault.azure.net/",
        secret_name="secret-name",
        secret_version=secret_version
    )
    secret_value = secret_bundle.value
```

Now in `azure-keyvault-secrets` you can retrieve the latest version of a secret (as a `KeyVaultSecret`) by using `get_secret` and providing a secret name.

```python
secret = secret_client.get_secret(name="secret-name")

print(secret.name)
print(secret.value)

# get the version of the secret
secret_version = secret.properties.version
```

### List properties of secrets

In `azure-keyvault` you could list the properties of secrets in a specified vault with the `get_secrets` method. This returned an iterator-like object containing `SecretItem` instances.

```python
secrets = client.get_secrets(vault_base_url="https://my-key-vault.vault.azure.net/")

for secret in secrets:
    print(secret.attributes.content_type)
```

Now in `azure-keyvault-secrets` you can list the properties of secrets in a vault with the `list_properties_of_secrets` method. This returns an iterator-like object containing `SecretProperties` instances.

```python
secrets = secret_client.list_properties_of_secrets()

for secret in secrets:
    print(secret.name)
    print(secret.content_type)
```

### Delete a secret

In `azure-keyvault` you could delete all versions of a secret with the `delete_secret` method. This returned information about the deleted secret (as a `DeletedSecretBundle`), but you could not poll the deletion operation to know when it completed. This would be valuable information if you intended to permanently delete the deleted secret with `purge_deleted_secret`.

```python
deleted_secret = client.delete_secret(
    vault_base_url="https://my-key-vault.vault.azure.net/",
    secret_name="secret-name"
)

# this purge would fail if deletion hadn't finished
client.purge_deleted_secret(
    vault_base_url="https://my-key-vault.vault.azure.net/",
    secret_name="secret-name"
)
```

Now in `azure-keyvault-secrets` you can delete a secret with `begin_delete_secret`, which returns a long operation poller object that can be used to wait/check on the operation. Calling `result()` on the poller will return information about the deleted secret (as a `DeletedSecret`) without waiting for the operation to complete, but calling `wait()` will wait for the deletion to complete. Again, `purge_deleted_secret` will permanently delete your deleted secret and make it unrecoverable.

```python
deleted_secret_poller = secret_client.begin_delete_secret(name="secret-name")
deleted_secret = deleted_secret_poller.result()

deleted_secret_poller.wait()
secret_client.purge_deleted_secret(name="secret-name")
```

## Additional samples

* [Key Vault secrets samples for Python](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-secrets/samples)
* [General Key Vault samples for Python](https://docs.microsoft.com/samples/browse/?products=azure-key-vault&languages=python)