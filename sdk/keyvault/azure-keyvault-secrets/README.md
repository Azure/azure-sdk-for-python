# Azure Key Vault Secrets client library for Python
Azure Key Vault helps solve the following problems:

- Secrets management (this library) -
securely store and control access to tokens, passwords, certificates, API keys,
and other secrets
- Cryptographic key management
([azure-keyvault-keys](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys)) -
create, store, and control access to the keys used to encrypt your data
- Certificate management
([azure-keyvault-certificates](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-certificates)) -
create, manage, and deploy public and private SSL/TLS certificates
- Vault administration ([azure-keyvault-administration](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-administration)) - role-based access control (RBAC), and vault-level backup and restore options

[Source code][secret_client_src] | [Package (PyPI)][pypi_package_secrets] | [API reference documentation][reference_docs] | [Product documentation][keyvault_docs] | [Samples][secret_samples]

## Getting started
### Install packages
Install [azure-keyvault-secrets][pypi_package_secrets] and
[azure-identity][azure_identity_pypi] with [pip][pip]:
```Bash
pip install azure-keyvault-secrets azure-identity
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

  > The `"vaultUri"` property is the `vault_url` used by [SecretClient][secret_client_docs]

### Authenticate the client
This document demonstrates using [DefaultAzureCredential][default_cred_ref]
to authenticate as a service principal. However, [SecretClient][secret_client_docs]
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
az keyvault set-policy --name my-key-vault --spn $AZURE_CLIENT_ID --secret-permissions get set list delete backup recover restore purge
```
> Possible permissions:
> - Secret management: set, backup, delete, get, list, purge, recover, restore


#### Create a client
Once the **AZURE_CLIENT_ID**, **AZURE_CLIENT_SECRET** and
**AZURE_TENANT_ID** environment variables are set,
[DefaultAzureCredential][default_cred_ref] will be able to authenticate the
[SecretClient][secret_client_docs].

Constructing the client also requires your vault's URL, which you can
get from the Azure CLI or the Azure Portal. In the Azure Portal, this URL is
the vault's "DNS Name".

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()

secret_client = SecretClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
```

## Key concepts
### Secret
A secret consists of a secret value and its associated metadata and management
information. This library handles secret values as strings, but Azure Key Vault
doesn't store them as such. For more information about secrets and how Key
Vault stores and manages them, see the
[Key Vault documentation](https://docs.microsoft.com/azure/key-vault/about-keys-secrets-and-certificates#key-vault-secrets).

[SecretClient][secret_client_docs] can set secret values in the vault, update
secret metadata, and delete secrets, as shown in the
[examples](#examples "examples") below.

## Examples
This section contains code snippets covering common tasks:
* [Set a Secret](#set-a-secret "Set a Secret")
* [Retrieve a Secret](#retrieve-a-secret "Retrieve a Secret")
* [Update Secret metadata](#update-secret-metadata "Update Secret metadata")
* [Delete a Secret](#delete-a-secret "Delete a Secret")
* [List Secrets](#list-secrets "List Secrets")
* [Asynchronously create a Secret](#asynchronously-create-a-secret "Asynchronously create a Secret")
* [Asynchronously list Secrets](#asynchronously-list-secrets "Asynchronously list Secrets")

### Set a Secret
[set_secret](https://aka.ms/azsdk/python/keyvault-secrets/docs#azure.keyvault.secrets.SecretClient.set_secret)
creates new secrets and changes the values of existing secrets. If no secret with the
given name exists, `set_secret` creates a new secret with that name and the
given value. If the given name is in use, `set_secret` creates a new version
of that secret, with the given value.

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()

secret_client = SecretClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
secret = secret_client.set_secret("secret-name", "secret-value")

print(secret.name)
print(secret.value)
print(secret.properties.version)
```

### Retrieve a Secret
[get_secret](https://aka.ms/azsdk/python/keyvault-secrets/docs#azure.keyvault.secrets.SecretClient.get_secret)
retrieves a secret previously stored in the Key Vault.

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()

secret_client = SecretClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
secret = secret_client.get_secret("secret-name")

print(secret.name)
print(secret.value)
```

### Update Secret metadata
[update_secret_properites](https://aka.ms/azsdk/python/keyvault-secrets/docs#azure.keyvault.secrets.SecretClient.update_secret_properties)
updates a secret's metadata. It cannot change the secret's value; use [set_secret](#set-a-secret) to set a secret's
value.

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()

secret_client = SecretClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)

# Clients may specify the content type of a secret to assist in interpreting the secret data when it's retrieved
content_type = "text/plain"

# We will also disable the secret for further use

updated_secret_properties = secret_client.update_secret_properties("secret-name", content_type=content_type, enabled=False)

print(updated_secret_properties.updated_on)
print(updated_secret_properties.content_type)
print(updated_secret_properties.enabled)
```

### Delete a Secret
[begin_delete_secret](https://aka.ms/azsdk/python/keyvault-secrets/docs#azure.keyvault.secrets.SecretClient.begin_delete_secret)
requests Key Vault delete a secret, returning a poller which allows you to wait for the deletion to finish. Waiting is
helpful when the vault has [soft-delete][soft_delete] enabled, and you want to purge (permanently delete) the secret as
soon as possible. When [soft-delete][soft_delete] is disabled, `begin_delete_secret` itself is permanent.

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()

secret_client = SecretClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
deleted_secret = secret_client.begin_delete_secret("secret-name").result()

print(deleted_secret.name)
print(deleted_secret.deleted_date)
```

### List secrets
[list_properties_of_secrets](https://aka.ms/azsdk/python/keyvault-secrets/docs#azure.keyvault.secrets.SecretClient.list_properties_of_secrets)
lists the properties of all of the secrets in the client's vault. This list doesn't include the secret's values.

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()

secret_client = SecretClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
secret_properties = secret_client.list_properties_of_secrets()

for secret_property in secret_properties:
    # the list doesn't include values or versions of the secrets
    print(secret_property.name)
```

### Async API
This library includes a complete async API supported on Python 3.5+. To use it, you must
first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/).
See
[azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#transport)
for more information.

Async clients and credentials should be closed when they're no longer needed. These
objects are async context managers and define async `close` methods. For
example:

```py
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.secrets.aio import SecretClient

credential = DefaultAzureCredential()

# call close when the client and credential are no longer needed
client = SecretClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
...
await client.close()
await credential.close()

# alternatively, use them as async context managers (contextlib.AsyncExitStack can help)
client = SecretClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
async with client:
  async with credential:
    ...
```

### Asynchronously create a secret
[set_secret](https://aka.ms/azsdk/python/keyvault-secrets/aio/docs#azure.keyvault.secrets.aio.SecretClient.set_secret)
creates a secret in the Key Vault with the specified optional arguments.
```python
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.secrets.aio import SecretClient

credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)

secret = await secret_client.set_secret("secret-name", "secret-value")

print(secret.name)
print(secret.value)
print(secret.properties.version)
```

### Asynchronously list secrets
[list_properties_of_secrets](https://aka.ms/azsdk/python/keyvault-secrets/aio/docs#azure.keyvault.secrets.aio.SecretClient.list_properties_of_secrets)
lists the properties of all of the secrets in the client's vault.

```python
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.secrets.aio import SecretClient

credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
secret_properties = secret_client.list_properties_of_secrets()

async for secret_property in secret_properties:
    # the list doesn't include values or versions of the secrets
    print(secret_property.name)
```

## Troubleshooting
### General
Key Vault clients raise exceptions defined in [azure-core][azure_core_exceptions].
For example, if you try to get a key that doesn't exist in the vault,
[SecretClient][secret_client_docs] raises
[ResourceNotFoundError](https://aka.ms/azsdk-python-core-exceptions-resource-not-found-error):

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import ResourceNotFoundError

credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)

try:
    secret_client.get_secret("which-does-not-exist")
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
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
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
secret_client = SecretClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential, logging_enable=True)
```

Similarly, `logging_enable` can enable detailed logging for a single operation,
even when it isn't enabled for the client:
```py
secret_client.get_secret("my-secret", logging_enable=True)
```

## Next steps
Several samples are available in the Azure SDK for Python GitHub repository.
These provide example code for additional Key Vault scenarios:
* [hello_world.py][hello_world_sample] and
[hello_world_async.py][hello_world_async_sample] - create/get/update/delete secrets
* [list_operations.py][list_operations_sample] and
[list_operations_async.py][list_operations_async_sample] - basic list operations for secrets
* [backup_restore_operations.py][backup_operations_sample] and
[backup_restore_operations_async.py][backup_operations_async_sample] - backup and
restore secrets
* [recover_purge_operations.py][recover_purge_sample] and
[recover_purge_operations_async.py][recover_purge_async_sample] - recovering and purging secrets

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

[azure_cloud_shell]: https://shell.azure.com/bash
[azure_core_exceptions]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/core/azure-core#azure-core-library-exceptions
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity
[azure_identity_pypi]: https://pypi.org/project/azure-identity/
[azure_sub]: https://azure.microsoft.com/free/
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[default_cred_ref]: https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
[hello_world_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-secrets/samples/hello_world.py
[hello_world_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-secrets/samples/hello_world_async.py
[backup_operations_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-secrets/samples/backup_restore_operations.py
[backup_operations_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-secrets/samples/backup_restore_operations_async.py
[list_operations_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-secrets/samples/list_operations.py
[list_operations_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-secrets/samples/list_operations_async.py
[recover_purge_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-secrets/samples/recover_purge_operations.py
[recover_purge_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-secrets/samples/recover_purge_operations_async.py
[keyvault_docs]: https://docs.microsoft.com/azure/key-vault/
[pip]: https://pypi.org/project/pip/
[pypi_package_secrets]: https://pypi.org/project/azure-keyvault-secrets/
[reference_docs]: https://aka.ms/azsdk/python/keyvault-secrets/docs
[secret_client_src]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-secrets/azure/keyvault/secrets
[secret_client_docs]: https://aka.ms/azsdk/python/keyvault-secrets/docs#azure.keyvault.secrets.SecretClient
[secret_samples]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-secrets/samples
[soft_delete]: https://docs.microsoft.com/azure/key-vault/key-vault-ovw-soft-delete

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Fkeyvault%2Fazure-keyvault-secrets%2FREADME.png)
