# Azure Key Vault Secret client library for Python
Azure Key Vault helps solve the following problems:
- Secrets management (this library) -
securely store and control access to tokens, passwords, certificates, API keys,
and other secrets
- Cryptographic key management
([`azure-keyvault-keys`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-secrets)) -
create, store, and control access to the keys used to encrypt your data
- Certificate management
([`azure-keyvault-certificates`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-certificates)) -
create, manage, and deploy public and private SSL/TLS certificates

[Source code][secret_client_src] | [Package (PyPI)][pypi_package_secrets] | [API reference documentation][reference_docs] | [Product documentation][keyvault_docs] | [Samples][secret_samples]

## Getting started
### Install the package
Install the Azure Key Vault Secrets client library for Python with [pip][pip]:

```Bash
pip install azure-keyvault-secrets
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

    > The `"vaultUri"` property is the `vault_url` used by `SecretClient`

### Authenticate the client
In order to interact with a Key Vault's secrets, you'll need an instance of the
[`SecretClient`][secret_client_docs] class. Creating one requires a **vault url** and
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
[`SecretClient`][secret_client_docs]:

```python
    from azure.identity import DefaultAzureCredential
    from azure.keyvault.secrets import SecretClient

    credential = DefaultAzureCredential()

    secret_client = SecretClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
```

## Key concepts
With a `SecretClient`, you can get secrets from the vault, create new secrets
and update their values, and delete secrets, as shown in the
[examples](#examples) below.

### Secret
A secret consists of a secret value and its associated metadata and management
information. For this library secret values are strings, but Azure Key Vault
doesn't store them as such. For more information about secrets and how Key
Vault stores and manages them, see the
[Key Vault documentation](https://docs.microsoft.com/en-us/azure/key-vault/about-keys-secrets-and-certificates#key-vault-secrets)
.

## Examples
This section contains code snippets covering common tasks:
* [Retrieve a Secret](#retrieve-a-secret)
* [Update Secret metadata](#update-secret-metadata)
* [Delete a Secret](#delete-a-secret)
* [List Secrets](#list-secrets)
* [Async create a Secret](#async-create-a-secret)
* [Async list Secrets](#async-list-secrets)

### Create a Secret
`set_secret` creates a secret in the vault. If a secret with the same name
already exists, a new version of that secret is created.

```python
    secret = secret_client.set_secret("secret-name", "secret-value")

    print(secret.name)
    print(secret.value)
    print(secret.properties.version)
```

### Retrieve a Secret
`get_secret` retrieves a secret previously stored in the Key Vault.

```python
    secret = secret_client.get_secret("secret-name")

    print(secret.name)
    print(secret.value)
```

### Update Secret metadata
`update_secret` updates a secret's metadata. It cannot change the secret's
value; use [`set_secret`](#create-a-secret) to set a secret's value.

```python
    # Clients may specify the content type of a secret to assist in interpreting the secret data when it's retrieved
    content_type = "text/plain"
    # You can specify additional application-specific metadata in the form of tags.
    tags = {"foo": "updated tag"}

    updated_secret_properties = secret_client.update_secret_properties("secret-name", content_type=content_type, tags=tags)

    print(updated_secret_properties.updated_on)
    print(updated_secret_properties.content_type)
    print(updated_secret_properties.tags)
```

### Delete a Secret
`begin_delete_secret` requests Key Vault delete a secret, returning a poller which allows you to
wait for the deletion to finish. Waiting is helpful when the vault has [soft-delete][soft_delete]
enabled, and you want to purge (permanently delete) the secret as soon as possible.
When [soft-delete][soft_delete] is disabled, deletion is always permanent.

```python
    deleted_secret = secret_client.begin_delete_secret("secret-name").result()

    print(deleted_secret.name)
    print(deleted_secret.properties.deleted_date)
```

### List secrets
This example lists all the secrets in the vault. The list doesn't include
secret values; use [`get_secret`](#retrieve-a-secret) to get a secret's value.

```python
    secret_properties = secret_client.list_properties_of_secrets()

    for secret_property in secret_properties:
        # the list doesn't include values or versions of the secrets
        print(secret_property.name)
```

### Async operations
This library includes a complete async API supported on Python 3.5+. To use it, you must
first install an async transport, such as [`aiohttp`](https://pypi.org/project/aiohttp/).
See
[azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md#transport)
for more information.

### Async create a secret
This example creates a secret in the Key Vault with the specified optional arguments.
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

### Async list secrets
This example lists properties of all the secrets in the specified Key Vault.
Note that secret values are not included.

```python
    secret_properties = secret_client.list_properties_of_secrets()

    async for secret_property in secret_properties:
        # the list doesn't include values or versions of the secrets
        print(secret_property.name)
```

## Troubleshooting
### General
Key Vault clients raise exceptions defined in [`azure-core`][azure_core_exceptions].
For example, if you try to get a key that doesn't exist in the vault,
`SecretClient` raises `ResourceNotFoundError`:

```python
from azure.core.exceptions import ResourceNotFoundError

secret_client.begin_delete_secret("my-secret").wait()

try:
    secret_client.get_secret("my-secret")
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

# Enable network trace logging. Each HTTP request will be logged at DEBUG level.
client = SecretClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential, logging_enable=True)
```

Network trace logging can also be enabled for any single operation:
 ```python
secret = secret_client.get_secret("secret-name", logging_enable=True)
```

## Next steps
Several samples are available in the Azure SDK for Python GitHub repository.
These provide example code for additional Key Vault scenarios:
* [test_samples_secrets.py][test_examples_secrets] and
[test_samples_secrets_async.py][test_example_secrets_async] - code snippets
from the library's documentation
* [hello_world.py][hello_world_sample] and
[hello_world_async.py][hello_world_async_sample] - create/get/update/delete
secrets
* [list_operations.py][list_operations_sample] and
[list_operations_async.py][list_operations_async_sample] - list secrets

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
[hello_world_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-secrets/samples/hello_world.py
[hello_world_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-secrets/samples/hello_world_async.py
[keyvault_docs]: https://docs.microsoft.com/en-us/azure/key-vault/
[list_operations_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-secrets/samples/list_operations.py
[list_operations_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-secrets/samples/list_operations_async.py
[pip]: https://pypi.org/project/pip/
[pypi_package_secrets]: https://pypi.org/project/azure-keyvault-secrets/
[reference_docs]: https://azure.github.io/azure-sdk-for-python/ref/azure.keyvault.secrets.html
[secret_client_src]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-secrets/azure/keyvault/secrets
[secret_client_docs]: https://azure.github.io/azure-sdk-for-python/ref/azure.keyvault.secrets.html#azure.keyvault.secrets.SecretClient
[secret_samples]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-secrets/samples
[soft_delete]: https://docs.microsoft.com/en-us/azure/key-vault/key-vault-ovw-soft-delete
[test_examples_secrets]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-secrets/tests/test_samples_secrets.py
[test_example_secrets_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-secrets/tests/test_samples_secrets_async.py

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Fkeyvault%2Fazure-keyvault-secrets%2FFREADME.png)
