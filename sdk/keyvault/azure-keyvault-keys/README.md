# Azure Key Vault Keys client library for Python
Azure Key Vault helps solve the following problems:
- Cryptographic key management (this library) - create, store, and control
access to the keys used to encrypt your data
- Secrets management
([azure-keyvault-secrets](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-secrets)) -
securely store and control access to tokens, passwords, certificates, API keys,
and other secrets
- Certificate management
([azure-keyvault-certificates](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-certificates)) -
create, manage, and deploy public and private SSL/TLS certificates
- Vault administration ([azure-keyvault-administration](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-administration)) - role-based access control (RBAC), and vault-level backup and restore options

[Source code][key_client_src] | [Package (PyPI)][pypi_package_keys] | [API reference documentation][reference_docs] | [Product documentation][keyvault_docs] | [Samples][key_samples]

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

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
* Python 3.6 or later
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

If you have enabled role-based access control (RBAC) for Key Vault instead, you can find roles like "Key Vault Crypto Officer" in our [RBAC guide][rbac_guide].
If you are managing your keys using Managed HSM, read about its [access control][access_control] that supports different built-in roles isolated from Azure Resource Manager (ARM).

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
[Key Vault documentation](https://docs.microsoft.com/azure/key-vault/keys/about-keys).

[KeyClient][key_client_docs] can create keys in the vault, get existing keys
from the vault, update key metadata, and delete keys, as shown in the
[examples](#examples "examples") below.

## Examples
This section contains code snippets covering common tasks:
* [Create a key](#create-a-key "Create a key")
* [Retrieve a key](#retrieve-a-key "Retrieve a key")
* [Update an existing key](#update-an-existing-key "Update an existing key")
* [Delete a key](#delete-a-key "Delete a key")
* [Configure automatic key rotation](#configure-automatic-key-rotation "Configure automatic key rotation")
* [List keys](#list-keys "List keys")
* [Perform cryptographic operations](#cryptographic-operations)
* [Async API](#async-api "Async API")
* [Asynchronously create a key](#asynchronously-create-a-key "Asynchronously create a key")
* [Asynchronously list keys](#asynchronously-list-keys "Asynchronously list keys")

### Create a key
[create_rsa_key](https://aka.ms/azsdk/python/keyvault-keys/docs#azure.keyvault.keys.KeyClient.create_rsa_key) and
[create_ec_key](https://aka.ms/azsdk/python/keyvault-keys/docs#azure.keyvault.keys.KeyClient.create_ec_key)
create RSA and elliptic curve keys in the vault, respectively. If a key with the same name already exists, a new version
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

### Retrieve a key
[get_key](https://aka.ms/azsdk/python/keyvault-keys/docs#azure.keyvault.keys.KeyClient.get_key) retrieves a key
previously stored in the Vault.
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient

credential = DefaultAzureCredential()

key_client = KeyClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
key = key_client.get_key("key-name")
print(key.name)
```

### Update an existing key
[update_key_properties](https://aka.ms/azsdk/python/keyvault-keys/docs#azure.keyvault.keys.KeyClient.update_key_properties)
updates the properties of a key previously stored in the Key Vault.
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

### Delete a key
[begin_delete_key](https://aka.ms/azsdk/python/keyvault-keys/docs#azure.keyvault.keys.KeyClient.begin_delete_key)
requests Key Vault delete a key, returning a poller which allows you to wait for the deletion to finish. Waiting is
helpful when the vault has [soft-delete][soft_delete] enabled, and you want to purge (permanently delete) the key as
soon as possible. When [soft-delete][soft_delete] is disabled, `begin_delete_key` itself is permanent.

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient

credential = DefaultAzureCredential()

key_client = KeyClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
deleted_key = key_client.begin_delete_key("key-name").result()

print(deleted_key.name)
print(deleted_key.deleted_date)
```

### Configure automatic key rotation
[update_key_rotation_policy](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-keyvault-keys/4.5.0b5/azure.keyvault.keys.html#azure.keyvault.keys.KeyClient.update_key_rotation_policy)
allows you to configure automatic key rotation for a key by specifying a rotation policy.
In addition,
[rotate_key](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-keyvault-keys/4.5.0b5/azure.keyvault.keys.html#azure.keyvault.keys.KeyClient.rotate_key)
allows you to rotate a key on-demand by creating a new version of the given key.

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient, KeyRotationLifetimeAction, KeyRotationPolicyAction

credential = DefaultAzureCredential()
key_client = KeyClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)

# Set the key's automated rotation policy to rotate the key 30 days before the key expires
actions = [KeyRotationLifetimeAction(KeyRotationPolicyAction.ROTATE, time_before_expiry="P30D")]
# You may also specify the duration after which the newly rotated key will expire
# In this example, any new key versions will expire after 90 days
updated_policy = key_client.update_key_rotation_policy("key-name", expires_in="P90D", lifetime_actions=actions)

# You can get the current rotation policy for a key with get_key_rotation_policy
current_policy = key_client.get_key_rotation_policy("key-name")

# Finally, you can rotate a key on-demand by creating a new version of the key
rotated_key = key_client.rotate_key("key-name")
```

### List keys
[list_properties_of_keys](https://aka.ms/azsdk/python/keyvault-keys/docs#azure.keyvault.keys.KeyClient.list_properties_of_keys)
lists the properties of all of the keys in the client's vault.

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
[CryptographyClient](https://aka.ms/azsdk/python/keyvault-keys/crypto/docs#azure.keyvault.keys.crypto.CryptographyClient)
enables cryptographic operations (encrypt/decrypt, wrap/unwrap, sign/verify) using a particular key.

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
[package documentation][crypto_client_docs]
for more details of the cryptography API.

### Async API
This library includes a complete set of async APIs. To use them, you must
first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/).
See
[azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#transport)
for more information.

Async clients and credentials should be closed when they're no longer needed. These
objects are async context managers and define async `close` methods. For
example:

```py
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.keys.aio import KeyClient

credential = DefaultAzureCredential()

# call close when the client and credential are no longer needed
client = KeyClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
...
await client.close()
await credential.close()

# alternatively, use them as async context managers (contextlib.AsyncExitStack can help)
client = KeyClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
async with client:
  async with credential:
    ...
```

### Asynchronously create a key
[create_rsa_key](https://aka.ms/azsdk/python/keyvault-keys/aio/docs#azure.keyvault.keys.aio.KeyClient.create_rsa_key) and
[create_ec_key](https://aka.ms/azsdk/python/keyvault-keys/aio/docs#azure.keyvault.keys.aio.KeyClient.create_ec_key)
create RSA and elliptic curve keys in the vault, respectively. If a key with the same name already exists, a new
version of the key is created.

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
[list_properties_of_keys](https://aka.ms/azsdk/python/keyvault-keys/aio/docs#azure.keyvault.keys.aio.KeyClient.list_properties_of_keys)
lists the properties of all of the keys in the client's vault.

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

See the `azure-keyvault-keys`
[troubleshooting guide](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys/TROUBLESHOOTING.md)
for details on how to diagnose various failure scenarios.

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
[logging](https://docs.python.org/3/library/logging.html) library for logging.
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

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct].
For more information, see the
[Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact opencode@microsoft.com with any additional questions or comments.

[access_control]: https://docs.microsoft.com/azure/key-vault/managed-hsm/access-control
[azure_cloud_shell]: https://shell.azure.com/bash
[azure_core_exceptions]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core#azure-core-library-exceptions
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
[azure_identity_pypi]: https://pypi.org/project/azure-identity/
[azure_sub]: https://azure.microsoft.com/free/
[default_cred_ref]: https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[hello_world_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-keys/samples/hello_world.py
[hello_world_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-keys/samples/hello_world_async.py
[backup_operations_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-keys/samples/backup_restore_operations.py
[backup_operations_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-keys/samples/backup_restore_operations_async.py
[list_operations_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-keys/samples/list_operations.py
[list_operations_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-keys/samples/list_operations_async.py
[recover_purge_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-keys/samples/recover_purge_operations.py
[recover_purge_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-keys/samples/recover_purge_operations_async.py
[keyvault_docs]: https://docs.microsoft.com/azure/key-vault/
[pip]: https://pypi.org/project/pip/
[pypi_package_keys]: https://pypi.org/project/azure-keyvault-keys/
[rbac_guide]: https://docs.microsoft.com/azure/key-vault/general/rbac-guide
[reference_docs]: https://aka.ms/azsdk/python/keyvault-keys/docs
[key_client_docs]: https://aka.ms/azsdk/python/keyvault-keys/docs#azure.keyvault.keys.KeyClient
[crypto_client_docs]: https://aka.ms/azsdk/python/keyvault-keys/crypto/docs
[key_client_src]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys/azure/keyvault/keys
[key_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys/samples
[soft_delete]: https://docs.microsoft.com/azure/key-vault/general/soft-delete-overview

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Fkeyvault%2Fazure-keyvault-keys%2FREADME.png)
