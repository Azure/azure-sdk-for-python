# Azure Key Vault Secret client library for Python
Azure Key Vault is a cloud service that provides a secure storage of secrets, such as passwords and database connection strings. Secret client library allows you to securely store and tightly control the access to tokens, passwords, API keys, and other secrets. This library offers operations to create, retrieve, update, delete, purge, backup, restore and list the secrets and its versions.

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault/azure/security/keyvault/secrets) | [Package (PyPI)](TODO) | [API reference documentation](TODO) | [Product documentation](https://docs.microsoft.com/en-us/azure/key-vault/) | [Samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault/azure/security/keyvault/secrets/samples)
## Getting started
### Install the package
Install the Azure Key Vault client library for Python with [pip](https://pypi.org/project/pip/):

```Bash
pip install azure-security-keyvault
```

### Prerequisites
* An [Azure subscription](https://azure.microsoft.com/free/).
* Python 2.7, 3.4 or later to use this package.
* An existing Key Vault. If you need to create a Key Vault, you can use the [Azure Cloud Shell](https://shell.azure.com/bash) to create one with this Azure CLI command. Replace `<your-resource-group-name>` and `<your-key-vault-name>` with your own, unique names:

    ```Bash
    az keyvault create --resource-group <your-resource-group-name> --name <your-key-vault-name>
    ```

### Authenticate the client
In order to interact with the Key Vault service, you'll need to create an instance of the [SecretClient](TODO-rst-docs) class. You would need a **vault url** and **client secret credentials (client id, client secret, tenant id)** to instantiate a client object. Client secret credential way of authentication is being used in this getting started section but you can find more ways to authenticate with [azure-identity](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity).

 #### Create/Get credentials
Use the [Azure Cloud Shell](https://shell.azure.com/bash) snippet below to create/get client secret credentials.

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
* Use the above returned credentials information to set **AZURE_CLIENT_ID**(appId), **AZURE_CLIENT_SECRET**(password) and **AZURE_TENANT_ID**(tenant) environment variables. The following example shows a way to do this in Bash:
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

* Use the above mentioned Key Vault name to retreive details of your Vault which also contains your Key Vault URL:
    ```Bash
    az keyvault show --name <your-key-vault-name> 
    ```

#### Create Secret client
Once you've populated the **AZURE_CLIENT_ID**, **AZURE_CLIENT_SECRET** and **AZURE_TENANT_ID** environment variables and replaced **your-vault-url** with the above returned URI, you can create the [SecretClient](TODO-rst-docs):

```python
    from azure.identity import DefaultAzureCredential
    from azure.security.keyvault import SecretClient

    credential = DefaultAzureCredential()

    # Create a new secret client using the default credential
    secret_client = SecretClient(vault_url=<your-vault-url>, credential=credential)
```
## Key concepts
### Secret
  A secret is the fundamental resource within Azure KeyVault. From a developer's perspective, Key Vault APIs accept and return secret values as strings. In addition to the secret data, the following attributes may be specified:
* expires: Identifies the expiration time on or after which the secret data should not be retrieved.
* not_before: Identifies the time after which the secret will be active.
* enabled: Specifies whether the secret data can be retrieved.
* created: Indicates when this version of the secret was created.
* updated: Indicates when this version of the secret was updated.

### Secret Client:
The Secret client performs the interactions with the Azure Key Vault service for getting, setting, updating,deleting, and listing secrets and its versions. An asynchronous and synchronous, SecretClient, client exists in the SDK allowing for selection of a client based on an application's use case. Once you've initialized a SecretClient, you can interact with the primary resource types in Key Vault.

## Examples
The following section provides several code snippets using the above created `secret_client`, covering some of the most common Azure Key Vault Secret service related tasks, including:
* [Create a Secret](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault#create-a-secret)
* [Retrieve a Secret](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault#retrieve-a-secret)
* [Update an existing Secret](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault#update-an-existing-secret)
* [Delete a Secret](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault#delete-a-secret)
* [List Secrets](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault#list-secrets)
* [Async create a Secret](https://github.com/samvaity/azure-sdk-for-python/tree/secrets-track2-readme/sdk/keyvault/azure-security-keyvault/azure/security/keyvault/secrets#async-create-a-secret)
* [Async list Secrets](https://github.com/samvaity/azure-sdk-for-python/tree/secrets-track2-readme/sdk/keyvault/azure-security-keyvault/azure/security/keyvault/secrets#async-list-secrets)

### Create a Secret
`set_secret` creates a Secret to be stored in the Azure Key Vault. If a secret with the same name already exists, then a new version of the secret is created.
```python
    secret = secret_client.set_secret("secret-name", "secret-value", enabled=True)

    print(secret.name)
    print(secret.value)
    print(secret.version)
    print(secret.enabled)
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
    print(updated_secret.value)
    print(updated_secret.version)
    print(updated_secret.updated)
    print(updated_secret.content_type)
    print(updated_secret.tags)

```

### Delete a Secret
`delete_secret` deletes a secret previously stored in the Key Vault. When [soft-delete](https://docs.microsoft.com/en-us/azure/key-vault/key-vault-ovw-soft-delete) is not enabled for the Key Vault, this operation permanently deletes the secret.
```python
    secret = secret_client.delete_secret("secret-name")

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
Python’s [asyncio package](https://pypi.org/project/asyncio/) (introduced in Python 3.4) and its two keywords `async` and `await` serves to declare, build, execute, and manage asynchronous code.
The package supports async API on Python 3.5+ and is identical to synchronous API. 

The following examples provide code snippets for performing async operations in the Secret Client library:

### Async create a secret
This example creates a secret in the Key Vault with the specified optional arguments.
```python
    from azure.identity import AsyncDefaultAzureCredential
    from azure.security.keyvault.aio import SecretClient

    # for async operations use AsyncDefaultAzureCredential
    credential = AsyncDefaultAzureCredential()
    # Create a new secret client using the default credential
    secret_client = SecretClient(vault_url=vault_url, credential=credential)

    secret = await secret_client.set_secret("secret-name", "secret-value", enabled=True)

    print(secret.name)
    print(secret.value)
    print(secret.version)
    print(secret.enabled)
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
Key Vault clients raise exceptions defined in azure-core. For more detailed infromation about exceptions and how to deal with them, see [Azure Core exceptions](TODO).

For example, if you try to retrieve a secret after it is deleted a `404` error is returned, indicating resource not found. In the following snippet, the error is handled gracefully by catching the exception and displaying additional information about the error.
```python
try:
    secret_client.get_secret("deleted_secret")
except ResourceNotFoundError as e:
    print(e.message)

Output: "Secret not found:deleted_secret"
```
### Logging [TODO]
This SDK uses Python standard logging library. You can configure logging print out debugging information to the stdout or anywhere you want.

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```
Http request and response details are printed to stdout with this logging config.

## Next steps
Several KeyVault Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Key Vault:
* [test_examples_secrets_sync.py](TODO) and [test_examples_secrets_async.py](TODO) - Contains the code snippets working with Key Vault secrets.
* [hello_world.py](TODO) and [hello_world_async.py](TODO) - Python code for working with Azure Key Vault, including:
  * Create a secret
  * Get an existing secret
  * Update an existing secret
  * Delete secret
* [list_secrets.py](TODO) and [list_secrets_async.py](TODO) - Example code for working with Key Vault secrets backup and recovery, including:
  * Create secrets
  * List all secrets in the Key Vault
  * Update secrets in the Key Vault
  * List versions of a specified secret
  * Delete secrets from the Key Vault
  * List deleted secrets in the Key Vault

 ###  Additional Documentation
For more extensive documentation on Azure Key Vault, see the [API reference documentation](TODO).

## Contributing
This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the Code of Conduct FAQ or contact opencode@microsoft.com with any additional questions or comments.