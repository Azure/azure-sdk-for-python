# Azure Key Vault Keys client library for Python
Azure Key Vault helps solve the following problems:
- Cryptographic key management (this library) - create, store, and control
access to the keys used to encrypt your data
- Secrets management
([azure-keyvault-secrets](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-secrets)) -
securely store and control access to tokens, passwords, certificates, API keys,
and other secrets
- Certificate management
([azure-keyvault-certificates](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-certificates)) -
create, manage, and deploy public and private SSL/TLS certificates

[Source code][key_client_src] | [Package (PyPI)][pypi_package_keys] | [API reference documentation][reference_docs] | [Product documentation][keyvault_docs] | [Samples][key_samples]

## Getting started
### Install packages
Install [azure-keyvault-keys][pypi_package_keys] and
[azure-identity][azure_identity_pypi] with [pip][pip]:
```Bash
pip install azure-keyvault-keys azure-identity
```
[azure-identity][azure_identity] is used for Azure Active Directory
authentication as demonstrated below.

### Prerequisites
* An [Azure subscription][azure_sub]
* Python 2.7, 3.5.3, or later
* A Key Vault. If you need to create one, you can use the
[Azure Cloud Shell][azure_cloud_shell] to create one with these commands
(replace `"my-resource-group"` and `"my-key-vault"` with your own, unique
names):

  (Optional) if you want a new resource group to hold the Key Vault:
  ```sh
  az group create --name my-resource-group --location westus2
  ```

  Create the Key Vault:
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

  > The `"vaultUri"` property is the `vault_url` used by [KeyClient][key_client_docs]

### Authenticate the client
This document demonstrates using [DefaultAzureCredential][default_cred_ref]
to authenticate as a service principal. However, [KeyClient][key_client_docs]
accepts any [azure-identity][azure_identity] credential. See the
[azure-identity][azure_identity] documentation for more information about other
credentials.

#### Create a service principal (optional)
This [Azure Cloud Shell][azure_cloud_shell] snippet shows how to create a
new service principal. Before using it, replace "your-application-name" with
a more appropriate name for your service principal.

Create a service principal:
```Bash
az ad sp create-for-rbac --name http://my-application --skip-assignment
```

> Output:
> ```json
> {
>     "appId": "generated app id",
>     "displayName": "my-application",
>     "name": "http://my-application",
>     "password": "random password",
>     "tenant": "tenant id"
> }
> ```

Use the output to set **AZURE_CLIENT_ID** ("appId" above), **AZURE_CLIENT_SECRET**
("password" above) and **AZURE_TENANT_ID** ("tenant" above) environment variables.
The following example shows a way to do this in Bash:
```Bash
export AZURE_CLIENT_ID="generated app id"
export AZURE_CLIENT_SECRET="random password"
export AZURE_TENANT_ID="tenant id"
```

Authorize the service principal to perform key operations in your Key Vault:
```Bash
az keyvault set-policy --name my-key-vault --spn $AZURE_CLIENT_ID --key-permissions backup delete get list create update decrypt encrypt
```
> Possible permissions:
> - Key management: backup, delete, get, list, purge, recover, restore, create, update, import
> - Cryptographic operations: decrypt, encrypt, unwrapKey, wrapKey, verify, sign


#### Create a client
Once the **AZURE_CLIENT_ID**, **AZURE_CLIENT_SECRET** and
**AZURE_TENANT_ID** environment variables are set,
[DefaultAzureCredential][default_cred_ref] will be able to authenticate the
[KeyClient][key_client_docs].

Constructing the client also requires your vault's URL, which you can
get from the Azure CLI or the Azure Portal. In the Azure Portal, this URL is
the vault's "DNS Name".

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient

credential = DefaultAzureCredential()

key_client = KeyClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
```

## Key concepts
### Keys
Azure Key Vault can create and store RSA and elliptic curve keys. Both can
optionally be protected by hardware security modules (HSMs). Azure Key Vault
can also perform cryptographic operations with them. For more information about
keys and supported operations and algorithms, see the
[Key Vault documentation](https://docs.microsoft.com/en-us/azure/key-vault/about-keys-secrets-and-certificates#key-vault-keys).

[KeyClient](key_client_docs) can create keys in the vault, get existing keys
from the vault, update key metadata, and delete keys, as shown in the
[examples](#examples "examples") below.

## Examples
This section contains code snippets covering common tasks:
* [Create a Key](#create-a-key "Create a Key")
* [Retrieve a Key](#retrieve-a-key "Retrieve a Key")
* [Update an existing Key](#update-an-existing-key "Update an existing Key")
* [Delete a Key](#delete-a-key "Delete a Key")
* [List Keys](#list-keys "List Keys")
* [Asynchronously create a Key](#asynchronously-create-a-key "Asynchronously create a Key")
* [Asynchronously list Keys](#asynchronously-list-keys "Asynchronously list Keys")
* [Perform cryptographic operations](#cryptographic-operations)

### Create a Key
[create_rsa_key](https://aka.ms/azsdk-python-keyvault-keys-create-rsa-key-ref) and
[create_ec_key](https://aka.ms/azsdk-python-keyvault-keys-create-ec-key-rf) create RSA and elliptic curve keys in the
vault, respectively. If a key with the same name already exists, a new version
of that key is created.

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient

credential = DefaultAzureCredential()

key_client = KeyClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)

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
[get_key](https://aka.ms/azsdk-python-keyvault-keys-get-key-ref) retrieves a key previously stored in the vault.
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient

credential = DefaultAzureCredential()

key_client = KeyClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
key = key_client.get_key("key-name")
print(key.name)
```

### Update an existing Key
[update_key_properties](https://aka.ms/azsdk-python-keyvault-keys-update-key-ref) updates the properties of a key previously stored in the Key Vault.
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient

credential = DefaultAzureCredential()

key_client = KeyClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)

# we will now disable the key for further use
updated_key = key_client.update_key_properties("key-name", enabled=False)

print(updated_key.name)
print(updated_key.properties.enabled)
```

### Delete a Key
[begin_delete_key](https://aka.ms/azsdk-python-keyvault-keys-begin-delete-key-ref) requests Key Vault delete a key, returning a poller which allows you to
wait for the deletion to finish. Waiting is helpful when the vault has [soft-delete][soft_delete]
enabled, and you want to purge (permanently delete) the key as soon as possible.
When [soft-delete][soft_delete] is disabled, `begin_delete_key` itself is permanent.

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient

credential = DefaultAzureCredential()

key_client = KeyClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
deleted_key = key_client.begin_delete_key("key-name").result()

print(deleted_key.name)
print(deleted_key.deleted_date)
```
### List keys
[list_properties_of_keys](https://aka.ms/azsdk-python-keyvault-keys-list-properties-keys-ref) lists the
properties of all of the keys in the client's vault.

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient

credential = DefaultAzureCredential()

key_client = KeyClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
keys = key_client.list_properties_of_keys()

for key in keys:
    # the list doesn't include values or versions of the keys
    print(key.name)
```

### Cryptographic operations
[CryptographyClient][crypto_client_docs] enables cryptographic operations (encrypt/decrypt,
wrap/unwrap, sign/verify) using a particular key.

```py
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.crypto import CryptographyClient, EncryptionAlgorithm

credential = DefaultAzureCredential()
key_client = KeyClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)

key = key_client.get_key("key-name")
crypto_client = CryptographyClient(key, credential=credential)
plaintext = b"plaintext"

result = crypto_client.encrypt(EncryptionAlgorithm.rsa_oaep, plaintext)
decrypted = crypto_client.decrypt(result.algorithm, result.ciphertext)
```

See the
[package documentation](https://aka.ms/azsdk-python-keyvault-keys-crypto-ref)
for more details of the cryptography API.

### Async API
This library includes a complete async API supported on Python 3.5+. To use it, you must
first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/).
See
[azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md#transport)
for more information.

### Asynchronously create a Key
[create_rsa_key](https://aka.ms/azsdk-python-keyvault-keys-async-create-rsa-key-ref) and
[create_ec_key](https://aka.ms/azsdk-python-keyvault-keys-async-create-ec-key-ref) create RSA and elliptic curve keys in the vault, respectively.
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
[list_properties_of_keys](https://aka.ms/azsdk-python-keyvault-keys-async-list-properties-keys-ref) lists the
properties of all of the keys in the client's vault.

```python
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.keys.aio import KeyClient

credential = DefaultAzureCredential()
key_client = KeyClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
keys = key_client.list_properties_of_keys()

async for key in keys:
    print(key.name)
```

## Troubleshooting
### General
Key Vault clients raise exceptions defined in [azure-core][azure_core_exceptions].
For example, if you try to get a key that doesn't exist in the vault, [KeyClient][key_client_docs]
raises [ResourceNotFoundError](https://aka.ms/azsdk-python-core-exceptions-resource-not-found-error):

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient
from azure.core.exceptions import ResourceNotFoundError

credential = DefaultAzureCredential()
key_client = KeyClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)

try:
    key_client.get_key("which-does-not-exist")
except ResourceNotFoundError as e:
    print(e.message)
```

### Logging
This library uses the standard
[logging](https://docs.python.org/3.5/library/logging.html) library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

Detailed DEBUG level logging, including request/response bodies and unredacted
headers, can be enabled on a client with the `logging_enable` argument:
```py
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient
import sys
import logging

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

credential = DefaultAzureCredential()

# This client will log detailed information about its HTTP sessions, at DEBUG level
client = KeyClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential, logging_enable=True)
```

Similarly, `logging_enable` can enable detailed logging for a single operation,
even when it isn't enabled for the client:
```py
client.get_key("my-key", logging_enable=True)
```

## Next steps
Several samples are available in the Azure SDK for Python GitHub repository.
These provide example code for additional Key Vault scenarios:
* [hello_world.py][hello_world_sample] and
[hello_world_async.py][hello_world_async_sample] - create/get/update/delete keys
* [list_operations.py][list_operations_sample] and
[list_operations_async.py][list_operations_async_sample] - basic list operations for keys
* [backup_restore_operations.py][backup_operations_sample] and
[backup_restore_operations_async.py][backup_operations_async_sample] - backup and
recover keys
* [recover_purge_operations.py][recover_purge_sample] and
[recover_purge_operations_async.py][recover_purge_async_sample] - recovering and purging keys

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
[azure_core_exceptions]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/core/azure-core#azure-core-library-exceptions
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity
[azure_identity_pypi]: https://pypi.org/project/azure-identity/
[azure_sub]: https://azure.microsoft.com/free/
[default_cred_ref]: https://aka.ms/azsdk-python-identity-default-cred-ref
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[hello_world_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-keys/samples/hello_world.py
[hello_world_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-keys/samples/hello_world_async.py
[backup_operations_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-keys/samples/backup_restore_operations.py
[backup_operations_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-keys/samples/backup_restore_operations_async.py
[list_operations_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-keys/samples/list_operations.py
[list_operations_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-keys/samples/list_operations_async.py
[recover_purge_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-keys/samples/recover_purge_operations.py
[recover_purge_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-keys/samples/recover_purge_operations_async.py
[keyvault_docs]: https://docs.microsoft.com/en-us/azure/key-vault/
[pip]: https://pypi.org/project/pip/
[pypi_package_keys]: https://pypi.org/project/azure-keyvault-keys/
[reference_docs]: https://aka.ms/azsdk-python-keyvault-keys-docs
[key_client_docs]: https://aka.ms/azsdk-python-keyvault-keys-keyclient
[crypto_client_docs]: https://aka.ms/azsdk-python-keyvault-keys-cryptographyclient
[key_client_src]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys/azure/keyvault/keys
[key_samples]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys/samples
[soft_delete]: https://docs.microsoft.com/en-us/azure/key-vault/key-vault-ovw-soft-delete
[test_examples_keys]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-keys/tests/test_samples_keys.py
[test_example_keys_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-keys/tests/test_samples_keys_async.py

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Fkeyvault%2Fazure-keyvault-keys%2FFREADME.png)
