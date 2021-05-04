# Guide for migrating to azure-keyvault-keys from azure-keyvault

This guide is intended to assist in the migration to `azure-keyvault-keys` from `azure-keyvault`. It will focus on side-by-side comparisons for similar operations between the two packages.

Familiarity with the `azure-keyvault` package is assumed. For those new to the Key Vault client library for Python, please refer to the [README for `azure-keyvault-keys`](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-keys/README.md) rather than this guide.

## Table of contents

* [Migration benefits](#migration-benefits)
* [Important changes](#important-changes)
    - [Separate packages and clients](#separate-packages-and-clients)
    - [Client constructors](#client-constructors)
    - [Async operations](#async-operations)
    - [Create a key](#create-a-key)
    - [Retrieve a key](#retrieve-a-key)
    - [List properties of keys](#list-properties-of-keys)
    - [Delete a key](#delete-a-key)
    - [Perform cryptographic operations](#perform-cryptographic-operations)
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

- [`azure-keyvault-certificates`](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-certificates/README.md) contains `CertificateClient` for working with certificates.
- `azure-keyvault-keys` contains `KeyClient` for working with keys and `CryptographyClient` for performing cryptographic operations.
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

Now in `azure-keyvault-keys` you can create a `KeyClient` using any credential from [`azure-identity`](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md). Below is an example using [`DefaultAzureCredential`](https://docs.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential?view=azure-python):

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient

credential = DefaultAzureCredential()

key_client = KeyClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
```

You can also create a `CryptographyClient` to perform cryptographic operations (encrypt/decrypt, wrap/unwrap, sign/verify) using a particular key.

```python
from azure.keyvault.keys.crypto import CryptographyClient

key = key_client.get_key("key-name")
crypto_client = CryptographyClient(key=key, credential=credential)
```

### Async operations

The modern `azure-keyvault-keys` library includes a complete async API supported on Python 3.5+. To use it, you must first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/). See [azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#transport) for more information.

Async operations are available on async clients, which should be closed when they're no longer needed. Each async client is an async context manager and defines an async `close` method. For example:

```python
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.keys.aio import KeyClient

credential = DefaultAzureCredential()

# call close when the client is no longer needed
client = KeyClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
...
await client.close()

# alternatively, use the client as an async context manager
client = KeyClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
async with client:
  ...
```

### Create a key

In `azure-keyvault` you could create a key by using `KeyVaultClient`'s `create_key` method, which required a vault endpoint, key name, and key type. This method returned a `KeyBundle` containing the key.

```python
# create an RSA key
key_bundle = client.create_key(
    vault_base_url="https://my-key-vault.vault.azure.net/",
    key_name="key-name",
    kty="RSA"
)
key = key_bundle.key

# create an elliptic curve key
key_bundle = client.create_key(
    vault_base_url="https://my-key-vault.vault.azure.net/",
    key_name="key-name",
    kty="EC"
)
key = key_bundle.key
```

Now in `azure-keyvault-keys` there are multiple ways to create keys. You can provide a key name and type to the general `create_key` method, or provide just a name to `create_rsa_key` or `create_ec_key`. These methods all return the created key as a `KeyVaultKey`.

```python
from azure.keyvault.keys import KeyType, KeyCurveName

# create a key with specified type
key = key_client.create_key(name="key-name", key_type=KeyType.ec)
print(key.name)
print(key.key_type)

# create an RSA key
rsa_key = key_client.create_rsa_key(name="rsa-key-name", size=2048)

# create an elliptic curve key
ec_key = key_client.create_ec_key(name="ec-key-name", curve=KeyCurveName.p_256)
```

### Retrieve a key

In `azure-keyvault` you could retrieve a key (in a `KeyBundle`) by using `get_key` and specifying the desired vault endpoint, key name, and key version. You could retrieve the versions of a key with the `get_key_versions` method, which returned an iterator-like object.

```python
from azure.keyvault import KeyId

key_items = client.get_key_versions(
    vault_base_url="https://my-key-vault.vault.azure.net/",
    key_name="key-name"
)

for key_item in key_items:
    key_id = KeyId(key_item.kid)
    key_version = key_id.version

    key_bundle = client.get_key(
        vault_base_url="https://my-key-vault.vault.azure.net/",
        key_name="key-name",
        key_version=key_version
    )
    key = key_bundle.key
```

Now in `azure-keyvault-keys` you can retrieve the latest version of a key (as a `KeyVaultKey`) by using `get_key` and providing a key name.

```python
key = key_client.get_key(name="key-name")

print(key.name)
print(key.key_type)

# get the version of the key
key_version = key.properties.version
```

### List properties of keys

In `azure-keyvault` you could list the properties of keys in a specified vault with the `get_keys` method. This returned an iterator-like object containing `KeyItem` instances.

```python
keys = client.get_keys(vault_base_url="https://my-key-vault.vault.azure.net/")

for key in keys:
    print(key.attributes.created)
```

Now in `azure-keyvault-keys` you can list the properties of keys in a vault with the `list_properties_of_keys` method. This returns an iterator-like object containing `KeyProperties` instances.

```python
keys = key_client.list_properties_of_keys()

for key in keys:
    print(key.name)
    print(key.created_on)
```

### Delete a key

In `azure-keyvault` you could delete all versions of a key with the `delete_key` method. This returned information about the deleted key (as a `DeletedKeyBundle`), but you could not poll the deletion operation to know when it completed. This would be valuable information if you intended to permanently delete the deleted key with `purge_deleted_key`.

```python
deleted_key = client.delete_key(vault_base_url="https://my-key-vault.vault.azure.net/", key_name="key-name")

# this purge would fail if deletion hadn't finished
client.purge_deleted_key(vault_base_url="https://my-key-vault.vault.azure.net/", key_name="key-name")
```

Now in `azure-keyvault-keys` you can delete a key with `begin_delete_key`, which returns a long operation poller object that can be used to wait/check on the operation. Calling `result()` on the poller will return information about the deleted key (as a `DeletedKey`) without waiting for the operation to complete, but calling `wait()` will wait for the deletion to complete. Again, `purge_deleted_key` will permanently delete your deleted key and make it unrecoverable.

```python
deleted_key_poller = key_client.begin_delete_key(name="key-name")
deleted_key = deleted_key_poller.result()

deleted_key_poller.wait()
key_client.purge_deleted_key(name="key-name")
```

### Perform cryptographic operations

In `azure-keyvault` you could perform cryptographic operations with keys by using the `encrypt`/`decrypt`, `wrap_key`/`unwrap_key`, and `sign`/`verify` methods. Each of these methods accepted a vault endpoint, key name, key version, and algorithm along with other parameters.

```python
from azure.keyvault import KeyId

key_bundle = client.create_key(
    vault_base_url="https://my-key-vault.vault.azure.net/",
    key_name="key-name",
    kty="RSA"
)
key = key_bundle.key
key_id = KeyId(key.kid)
key_version = key_id.version

plaintext = b"plaintext"

# encrypt data using the key
operation_result = client.encrypt(
    vault_base_url="https://my-key-vault.vault.azure.net/",
    key_name="key-name",
    key_version=key_version,
    algorithm="RSA-OAEP-256",
    value=plaintext
)
ciphertext = operation_result.result
```

Now in `azure-keyvault-keys` you can perform these cryptographic operations by using a `CryptographyClient`. The key used to create the client will be used for these operations. Cryptographic operations are now performed locally by the client when it's intialized with the necessary key material or is able to get that material from Key Vault, and are only performed by the Key Vault service when required key material is unavailable.

```python
from azure.keyvault.keys.crypto import CryptographyClient, EncryptionAlgorithm

key = key_client.get_key(name="key-name")
crypto_client = CryptographyClient(key=key, credential=credential)

plaintext = b"plaintext"

# encrypt data using the key
result = crypto_client.encrypt(algorithm=EncryptionAlgorithm.rsa_oaep_256, plaintext=plaintext)
ciphertext = result.ciphertext
```

## Additional samples

* [Key Vault keys samples for Python](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys/samples)
* [General Key Vault samples for Python](https://docs.microsoft.com/samples/browse/?products=azure-key-vault&languages=python)
