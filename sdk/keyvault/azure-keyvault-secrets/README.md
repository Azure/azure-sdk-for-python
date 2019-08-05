# Azure Key Vault Secret client library for Python
This client library helps you to set, get, update, and delete Azure Key Vault
Secrets. Secrets are a resource for storing secret values, such as passwords,
API keys, and connection strings, and controlling access to them.

Use this library to:
- Set, get, and delete secrets.
- Update secrets and their attributes.
- Backup and restore secrets.
- List the secrets in a vault, or the versions of a particular secret.

[Source code][secret_client_src] | [Package (PyPI)][pypi_package_secrets] | [API reference documentation][reference_docs] | [Product documentation][keyvault_docs] | [Samples][secret_samples]
## Getting started
### Install the package
Install the Azure Key Vault client library for Python with [pip][pip]:

```Bash
pip install azure-keyvault-secrets
```

### Prerequisites
* An [Azure subscription][azure_sub].
* Python 2.7, 3.4 or later to use this package.
* An existing Key Vault. If you need to create a Key Vault, you can use the [Azure Cloud Shell][azure_cloud_shell] to create one with this Azure CLI command. Replace `<your-resource-group-name>` and `<your-key-vault-name>` with your own, unique names:

    ```Bash
    az keyvault create --resource-group <your-resource-group-name> --name <your-key-vault-name>
    ```

### Authenticate the client
In order to interact with secrets in a vault, you'll need to create an instance
of [`SecretClient`][secret_client_docs]. That requires a **vault url**, and a
**credential** that can authenticate the client to the vault. This document
shows authentication with a client secret credential configured via environment
variables, but other credential types can be used. See
[azure-identity][azure_identity] documentation for more information.

 #### Create/Get credentials
Use the [Azure Cloud Shell][azure_cloud_shell] snippet below to create/get client secret credentials.

 * Create a service principal and configure its access to Azure resources:
    ```Bash
    az ad sp create-for-rbac -n <your-application-name> --skip-assignment
    ```
    Output:
    ```json
    {
        "appId": "generated-app-ID",
        "displayName": "dummy-app-name",
        "name": "http://dummy-app-name",
        "password": "random-password",
        "tenant": "tenant-ID"
    }
    ```
* Use the credentials returned above to set **AZURE_CLIENT_ID**(appId), **AZURE_CLIENT_SECRET**(password) and (password) and **AZURE_TENANT_ID**(tenant) environment variables. The following example shows a way to do this in Bash:
  ```Bash
    export AZURE_CLIENT_ID="generated-app-ID"
    export AZURE_CLIENT_SECRET="random-password"
    export AZURE_TENANT_ID="tenant-ID"
  ```

* Grant the above mentioned application authorization to perform secret operations on the keyvault:
    ```Bash
    az keyvault set-policy --name <your-key-vault-name> --spn $AZURE_CLIENT_ID --secret-permissions backup delete get list set
    ```
    > --secret-permissions:
    > Accepted values: backup, delete, get, list, purge, recover, restore, set

* Use the above mentioned Key Vault name to retrieve details of your Vault which also contains your Key Vault URL:
    ```Bash
    az keyvault show --name <your-key-vault-name>
    ```

#### Create Secret client
Once you've populated the **AZURE_CLIENT_ID**, **AZURE_CLIENT_SECRET** and
**AZURE_TENANT_ID** environment variables and replaced **your-vault-url**
with the above returned URI, you can create the [`SecretClient`][secret_client_docs]:

```python
    from azure.identity import DefaultAzureCredential
    from azure.keyvault.secrets import SecretClient

    credential = DefaultAzureCredential()

    # Create a new secret client using the default credential
    secret_client = SecretClient(vault_url=<your-vault-url>, credential=credential)
```
## Key concepts
### Secret
  In Azure Key Vault, a Secret consists of a secret value and its associated
  metadata and management information. From the perspective of a developer, the
  secret values themselves are strings.

### Secret Client:
The Secret client performs the interactions with the Azure Key Vault service for getting, setting, updating,deleting, and listing secrets and its versions. An asynchronous and synchronous, SecretClient, client exists in the SDK allowing for selection of a client based on an application's use case. Once you've initialized a SecretClient, you can interact with the primary resource types in Key Vault.

## Examples
The following section provides several code snippets using the above created `secret_client`, covering some of the most common Azure Key Vault Secret service related tasks, including:
* [Create a Secret](#create-a-secret)
* [Retrieve a Secret](#retrieve-a-secret)
* [Update an existing Secret](#update-an-existing-secret)
* [Delete a Secret](#delete-a-secret)
* [List Secrets](#list-secrets)
* [Async create a Secret](#async-create-a-secret)
* [Async list Secrets](#async-list-secrets)

### Create a Secret
`set_secret` creates a Secret to be stored in the Azure Key Vault. If a secret with the same name already exists, then a new version of the secret is created.
```python
    secret = secret_client.set_secret("secret-name", "secret-value")

    print(secret.name)
    print(secret.value)
    print(secret.version)
```

### Retrieve a Secret
`get_secret` retrieves a secret previously stored in the Key Vault.
```python
    secret = secret_client.get_secret("secret-name")

    print(secret.name)
    print(secret.value)
```

### Update an existing Secret
`update_secret` updates a secret previously stored in the Key Vault.
```python
    # Clients may specify the content type of a secret to assist in interpreting the secret data when it's retrieved
    content_type = "text/plain"
    # You can specify additional application-specific metadata in the form of tags.
    tags = {"foo": "updated tag"}

    updated_secret = secret_client.update_secret("secret-name", content_type=content_type, tags=tags)

    print(updated_secret.name)
    print(updated_secret.version)
    print(updated_secret.updated)
    print(updated_secret.content_type)
    print(updated_secret.tags)

```

### Delete a Secret
`delete_secret` deletes a secret previously stored in the Key Vault. When [soft-delete][soft_delete] is not enabled for the Key Vault, this operation permanently deletes the secret.
```python
    deleted_secret = secret_client.delete_secret("secret-name")

    print(deleted_secret.name)
    print(deleted_secret.deleted_date)
```
### List secrets
This example lists all the secrets in the specified Key Vault.
```python
    secrets = secret_client.list_secrets()

    for secret in secrets:
        # the list doesn't include values or versions of the secrets
        print(secret.name)
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

    # for async operations use DefaultAzureCredential
    credential = DefaultAzureCredential()
    # Create a new secret client using the default credential
    secret_client = SecretClient(vault_url=vault_url, credential=credential)

    secret = await secret_client.set_secret("secret-name", "secret-value")

    print(secret.name)
    print(secret.value)
    print(secret.version)
```
### Async list secrets
This example lists all the secrets in the specified Key Vault.
```python
    secrets = secret_client.list_secrets()

    async for secret in secrets:
        # the list doesn't include values or versions of the secrets
        print(secret.name)
```

## Troubleshooting
### General
Key Vault clients raise exceptions defined in azure-core. For more detailed infromation about exceptions and how to deal with them, see [Azure Core exceptions][azure_core_exceptions].

For example, if you try to retrieve a secret after it is deleted a `404` error is returned, indicating resource not found. In the following snippet, the error is handled gracefully by catching the exception and displaying additional information about the error.
```python
try:
    secret_client.get_secret("deleted_secret")
except ResourceNotFoundError as e:
    print(e.message)

Output: "Secret not found:deleted_secret"
```
### Logging
Network trace logging is disabled by default for this library. When enabled, this will be logged at DEBUG level. The logging policy is used to output the HTTP network trace to the configured logger. You can configure logging to print out debugging information to the stdout or write it to a file using the following example:

 ```python
import sys
import logging
 # Create a logger for the 'azure' SDK
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
 # Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)
 # Configure a file output
file_handler = logging.FileHandler(filename)
logger.addHandler(file_handler)

# Enable network trace logging. This will be logged at DEBUG level.
# By default, network trace logging is disabled.
config = SecretClient.create_config(credential, logging_enable=True)
client = SecretClient(url, credential, config=config)
```
The logger can also be enabled per operation.

 ```python
secret = secret_client.get_secret("secret-name", logging_enable=True)
```

## Next steps
Several KeyVault Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Key Vault:
* [test_samples_secrets.py][test_examples_secrets] and [test_samples_secrets_async.py][test_example_secrets_async] - Contains the code snippets working with Key Vault secrets.
* [hello_world.py][hello_world_sample] and [hello_world_async.py][hello_world_async_sample] - Python code for working with Azure Key Vault, including:
  * Create a secret
  * Get an existing secret
  * Update an existing secret
  * Delete secret
* [list_operations.py][list_operations_sample] and [list_operations_async.py][list_operations_async_sample] - Example code for working with Key Vault secrets backup and recovery, including:
  * Create secrets
  * List all secrets in the Key Vault
  * Update secrets in the Key Vault
  * List versions of a specified secret
  * Delete secrets from the Key Vault
  * List deleted secrets in the Key Vault

 ###  Additional Documentation
For more extensive documentation on Azure Key Vault, see the [API reference documentation][reference_docs].

## Contributing
This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the Code of Conduct FAQ or contact opencode@microsoft.com with any additional questions or comments.

<!-- LINKS -->
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
