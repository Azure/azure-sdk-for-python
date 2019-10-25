# Azure Key Vault Keys client library for Python
Azure Key Vault helps solve the following problems:
- Cryptographic key management (this library) - create, store, and control
access to the keys used to encrypt your data
- Secrets management
([`azure-keyvault-secrets`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-secrets)) -
securely store and control access to tokens, passwords, certificates, API keys,
and other secrets
- Certificate management
([`azure-keyvault-certificates`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-certificates)) -
create, manage, and deploy public and private SSL/TLS certificates

[Source code][key_client_src] | [Package (PyPI)][pypi_package_keys] | [API reference documentation][reference_docs] | [Product documentation][keyvault_docs] | [Samples][key_samples]

## Getting started
### Install the package
Install the Azure Key Vault Keys client library for Python with [pip][pip]:

```Bash
pip install azure-keyvault-keys
```

### Prerequisites
* An [Azure subscription][azure_sub]
* Python 2.7, 3.5.3, or later
* A Key Vault. If you need to create one, you can use the
[Azure Cloud Shell][azure_cloud_shell] to create one with these commands
(replace `"my-resource-group"` and `"my-key-vault"` with your own, unique
names):
  * (Optional) if you want a new resource group to hold the Key Vault:
    ```sh
    az group create --name my-resource-group --location westus2
    ```
  * Create the Key Vault:
    ```Bash
    az keyvault create --resource-group my-resource-group --name my-key-vault
    ```

    Output:
    ```json
    {
        "id": "...",
        "location": "westus2",
        "name": "my-key-vault",
        "properties": {
            "accessPolicies": [...],
            "createMode": null,
            "enablePurgeProtection": null,
            "enableSoftDelete": null,
            "enabledForDeployment": false,
            "enabledForDiskEncryption": null,
            "enabledForTemplateDeployment": null,
            "networkAcls": null,
            "provisioningState": "Succeeded",
            "sku": { "name": "standard" },
            "tenantId": "...",
            "vaultUri": "https://my-key-vault.vault.azure.net/"
        },
        "resourceGroup": "my-resource-group",
        "type": "Microsoft.KeyVault/vaults"
    }
    ```

    > The `"vaultUri"` property is the `vault_url` used by `KeyClient`.

### Authenticate the client
To interact with a Key Vault's keys, you'll need an instance of the
[KeyClient][key_client_docs] class. Creating one requires a **vault url** and
**credential**. This document demonstrates using `DefaultAzureCredential` as
the credential, authenticating with a service principal's client id, secret,
and tenant id. Other authentication methods are supported. See the
[azure-identity][azure_identity] documentation for more details.

#### Create a service principal
This [Azure Cloud Shell][azure_cloud_shell] snippet shows how to create a
new service principal. Before using it, replace "your-application-name" with
a more appropriate name for your service principal.

 * Create a service principal:
    ```Bash
    az ad sp create-for-rbac --name http://my-application --skip-assignment
    ```
    Output:
    ```json
    {
        "appId": "generated app id",
        "displayName": "my-application",
        "name": "http://my-application",
        "password": "random password",
        "tenant": "tenant id"
    }
    ```

* Use the output to set **AZURE_CLIENT_ID** (appId), **AZURE_CLIENT_SECRET**
(password) and **AZURE_TENANT_ID** (tenant) environment variables. The
following example shows a way to do this in Bash:
  ```Bash
   export AZURE_CLIENT_ID="generated app id"
   export AZURE_CLIENT_SECRET="random password"
   export AZURE_TENANT_ID="tenant id"
  ```

* Authorize the service principal to perform key operations in your Key Vault:
    ```Bash
    az keyvault set-policy --name my-key-vault --spn $AZURE_CLIENT_ID --key-permissions backup delete get list create
    ```
    > Possible key permissions:
    > - Key management: backup, delete, get, list, purge, recover, restore, create, update, import
    > - Cryptographic operations: decrypt, encrypt, unwrapKey, wrapKey, verify, sign


#### Create a client
After setting the **AZURE_CLIENT_ID**, **AZURE_CLIENT_SECRET** and
**AZURE_TENANT_ID** environment variables, you can create the
[KeyClient][key_client_docs]:

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient

credential = DefaultAzureCredential()

key_client = KeyClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
```

## Key concepts
With a `KeyClient`, you can get keys from the vault, create new keys and new
versions of existing keys, update key metadata, and delete keys, as shown in
the [examples](#examples) below.

### Keys
Azure Key Vault can create and store RSA and elliptic curve keys. Both can
optionally be protected by hardware security modules (HSMs). Azure Key Vault
can also perform cryptographic operations with them. For more information about
keys and supported operations and algorithms, see the
[Key Vault documentation](https://docs.microsoft.com/en-us/azure/key-vault/about-keys-secrets-and-certificates#key-vault-keys)
.

## Examples
This section contains code snippets covering common tasks:
* [Create a Key](#create-a-key)
* [Retrieve a Key](#retrieve-a-key)
* [Update an existing Key](#update-an-existing-key)
* [Delete a Key](#delete-a-key)
* [List Keys](#list-keys)
* [Asynchronously create a Key](#asynchronously-create-a-key)
* [Asynchronously list Keys](#asynchronously-list-keys)
* [Perform cryptographic operations](#cryptographic-operations)

### Create a Key
`create_rsa_key` and `create_ec_key` create RSA and elliptic curve keys in the
vault, respectively. If a key with the same name already exists, a new version
of that key is created.

```python
# Create an RSA key
rsa_key = key_client.create_rsa_key("rsa-key-name", size=2048)
print(rsa_key.name)
print(rsa_key.key_type)

# Create an elliptic curve key
ec_key = key_client.create_ec_key("ec-key-name", curve="P-256")
print(ec_key.name)
print(ec_key.key_type)
```

### Retrieve a Key
`get_key` retrieves a key previously stored in the vault.
```python
key = key_client.get_key("key-name")
print(key.name)
```

### Update an existing Key
`update_key` updates a key previously stored in the Key Vault.
```python
# Clients may specify additional application-specific metadata in the form of tags.
tags = {"foo": "updated tag"}

updated_key_properties = key_client.update_key_properties("key-name", tags=tags)

print(updated_key_properties.name)
print(updated_key_properties.version)
print(updated_key_properties.updated_on)
print(updated_key_properties.tags)
```

### Delete a Key
`begin_delete_key` requests Key Vault delete a key, returning a poller which allows you to
wait for the deletion to finish. Waiting is helpful when the vault has [soft-delete][soft_delete]
enabled, and you want to purge (permanently delete) the key as soon as possible.
When [soft-delete][soft_delete] is disabled, deletion is always permanent.

```python
deleted_key = key_client.begin_delete_key("key-name").result()

print(deleted_key.name)
print(deleted_key.deleted_date)
```
### List keys
This example lists all the keys in the client's vault.

```python
keys = key_client.list_properties_of_keys()

for key in keys:
    # the list doesn't include values or versions of the keys
    print(key.name)
```

### Cryptographic operations
`CryptographyClient` enables cryptographic operations (encrypt/decrypt,
wrap/unwrap, sign/verify) using a particular key.

```py
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.crypto import CryptographyClient, EncryptionAlgorithm

credential = DefaultAzureCredential()
key_client = KeyClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)

key = key_client.get_key("mykey")
crypto_client = CryptographyClient(key, credential=credential)

result = crypto_client.encrypt(EncryptionAlgorithm.rsa_oaep, plaintext)
decrypted = crypto_client.decrypt(result.algorithm, result.ciphertext)
```

See the
[package documentation](https://azure.github.io/azure-sdk-for-python/ref/azure.keyvault.keys.crypto.html)
for more details of the cryptography API.

### Async operations
This library includes a complete async API supported on Python 3.5+. To use it, you must
first install an async transport, such as [`aiohttp`](https://pypi.org/project/aiohttp/).
See
[azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md#transport)
for more information.

### Asynchronously create a Key
`create_rsa_key` and `create_ec_key` create RSA and elliptic curve keys in the vault, respectively.
If a key with the same name already exists, a new version of the key is created.

```python
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.keys.aio import KeyClient

credential = DefaultAzureCredential()
key_client = KeyClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)

# Create an RSA key
rsa_key = await key_client.create_rsa_key("rsa-key-name", size=2048)
print(rsa_key.name)
print(rsa_key.key_type)

# Create an elliptic curve key
ec_key = await key_client.create_ec_key("ec-key-name", curve="P-256")
print(ec_key.name)
print(ec_key.key_type)
```

### Asynchronously list keys
This example lists all the keys in the client's vault:

```python
keys = key_client.list_properties_of_keys()

async for key in keys:
    print(key.name)
```

## Troubleshooting
### General
Key Vault clients raise exceptions defined in [`azure-core`][azure_core_exceptions].
For example, if you try to get a key that doesn't exist in the vault, `KeyClient`
raises `ResourceNotFoundError`:

```python
from azure.core.exceptions import ResourceNotFoundError

key_client.begin_delete_key("my-key").wait()

try:
    key_client.get_key("my-key")
except ResourceNotFoundError as e:
    print(e.message)
```

### Logging
Network trace logging is disabled by default for this library. When enabled,
HTTP requests will be logged at DEBUG level using the `logging` library. You
can configure logging to print debugging information to stdout or write it
to a file:

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient
import sys
import logging

# Create a logger for the 'azure' SDK
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

credential = DefaultAzureCredential()

# Enable network trace logging. Each HTTP request will be logged at DEBUG level.
client = KeyClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential, logging_enable=True)
```

Network trace logging can also be enabled for any single operation:
```python
key = key_client.get_key("key-name", logging_enable=True)
```

## Next steps
Several samples are available in the Azure SDK for Python GitHub repository.
These provide example code for additional Key Vault scenarios:
* [test_samples_keys.py][test_examples_keys] and
[test_samples_keys_async.py][test_example_keys_async] - code snippets from
the library's documentation
* [hello_world.py][hello_world_sample] and
[hello_world_async.py][hello_world_async_sample] - create/get/update/delete keys
* [backup_restore_operations.py][backup_operations_sample] and
[backup_restore_operations_async.py][backup_operations_async_sample] - backup and
recover keys

###  Additional Documentation
For more extensive documentation on Azure Key Vault, see the
[API reference documentation][reference_docs].

## Contributing
This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact opencode@microsoft.com with any
additional questions or comments.

[azure_cloud_shell]: https://shell.azure.com/bash
[azure_core_exceptions]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/docs/exceptions.md
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity
[azure_sub]: https://azure.microsoft.com/free/
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[hello_world_sample]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys/samples/hello_world.py
[hello_world_async_sample]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys/samples/hello_world_async.py
[JWK]: https://tools.ietf.org/html/rfc7517
[keyvault_docs]: https://docs.microsoft.com/en-us/azure/key-vault/
[backup_operations_sample]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys/samples/backup_restore_operations.py
[backup_operations_async_sample]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys/samples/backup_restore_operations_async.py
[pip]: https://pypi.org/project/pip/
[pypi_package_keys]: https://pypi.org/project/azure-keyvault-keys/
[reference_docs]: https://azure.github.io/azure-sdk-for-python/ref/azure.keyvault.keys.html
[key_client_docs]: https://azure.github.io/azure-sdk-for-python/ref/azure.keyvault.keys.html#azure.keyvault.keys.KeyClient
[key_client_src]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys/azure/keyvault/keys
[key_samples]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys/samples
[soft_delete]: https://docs.microsoft.com/en-us/azure/key-vault/key-vault-ovw-soft-delete
[test_examples_keys]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-keys/tests/test_samples_keys.py
[test_example_keys_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-keys/tests/test_samples_keys_async.py

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Fkeyvault%2Fazure-keyvault-keys%2FFREADME.png)
