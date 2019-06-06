# Azure Key Vault Secret client library for Python
Azure Key Vault is a cloud service that provides a secure storage of secrets, such as passwords and database connection strings. Secret client library allows you to securely store and tightly control the access to tokens, passwords, API keys, and other secrets. This library offers operations to create, retrieve, update, delete, purge, backup, restore and and list the secrets and its versions.

Use the secret client library to create and manage secrets.

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault/azure/security/keyvault/secrets) | [Package (Pypi)](TODO) | [API reference documentation](TODO) | [Product documentation](TODO)
## Getting started
### Install the package
Install the Azure Key Vault client library for Python with pip:


`$ pip install azure-security-keyvault
`

### Prerequisites
* An [Azure subscription](https://azure.microsoft.com/free/).
* Python 2.7, 3.4 or later.
* An existing Key Vault. You can create this by following the instructions on [this article](https://docs.microsoft.com/en-gb/azure/key-vault/quick-create-portal).

### Authenticate the client
In order to interact with the Key Vault service for managing secrets, you'll need to create an instance of the SecretClient class. For this you will need a vault url, client secret credentials (client id, client secret, tenant id) and a [resource url](https://vault.azure.net).

### Get credentials
You can find credential information in [Azure Portal](https://portal.azure.com/).

### Create Secret client
The following code snippet demonstrates a way you can instantiate the KeyVaultClient object:
```python
    from azure.identity import AsyncClientSecretCredential
    from azure.security.keyvault import SecretClient

    credential = AsyncClientSecretCredential(client_id=client_id, secret=client_secret, tenant_id=tenant_id)

    # Create a new secret client using a client secret credential
    secret_client = SecretClient(vault_url=vault_url, credential=credential)
```
## Key concepts
### Secret
  A secret is the fundamental resource within Azure KeyVault. From a developer's perspective, Key Vault APIs accept and return secret values as strings. In addition to the secret data, the following attributes may be specified:
* expires: Identifies the expiration time on or after which the secret data should not be retrieved.
* nbf: Identifies the time after which the secret will be active.
* enabled: Specifies whether the secret data can be retrieved.
* created: Indicates when this version of the secret was created.(read-only)
* updated: Indicates when this version of the secret was updated.(read-only)

### Secret Client:
The Secret client performs the interactions with the Azure Key Vault service for getting, setting, updating,deleting, and listing secrets and its versions. An asynchronous and synchronous, SecretClient, client exists in the SDK allowing for selection of a client based on an application's use case.

## Examples
The following sections provide several code snippets covering some of the most common Azure Key Vault Secret service related tasks, including:
* [Create a Secret](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault#create-a-secret)
* [Retrieve a Secret](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault#retrieve-a-secret)
* [Update an existing Secret](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault#update-an-existing-secret)
* [Delete a Secret](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault#delete-a-secret)
* * [Async create a Secret](https://github.com/samvaity/azure-sdk-for-python/tree/secrets-track2-readme/sdk/keyvault/azure-security-keyvault/azure/security/keyvault/secrets#async-create-a-secret)

### Create a Secret
`set_secret` creates a Secret to be stored in the Azure Key Vault. If a secret with the same name already exists then a new version of the secret is created.
```python
    from azure.identity import AsyncClientSecretCredential
    from azure.security.keyvault import SecretClient

    credential = AsyncClientSecretCredential(client_id=client_id, secret=client_secret, tenant_id=tenant_id)
    # Create a new secret client using a client secret credential
    secret_client = SecretClient(vault_url=vault_url, credential=credential)

    secret = secret_client.set_secret("secret-name", "secret-value", enabled=True)
    print(secret.version)
    print(secret.enabled)
```

### Retrieve a Secret
`get_secret` retrieves a secret previously stored in the Key Vault.
```python
    from azure.identity import AsyncClientSecretCredential
    from azure.security.keyvault import SecretClient

    credential = AsyncClientSecretCredential(client_id=client_id, secret=client_secret, tenant_id=tenant_id)
    # Create a new secret client using a client secret credential
    secret_client = SecretClient(vault_url=vault_url, credential=credential)

    secret = secret_client.get_secret("secret-name")
    print(secret.version)
```

### Update an existing Secret
`update_secret` updates a secret previously stored in the Key Vault.
```python
    from azure.identity import AsyncClientSecretCredential
    from azure.security.keyvault import SecretClient

    credential = AsyncClientSecretCredential(client_id=client_id, secret=client_secret, tenant_id=tenant_id)
    # Create a new secret client using a client secret credential
    secret_client = SecretClient(vault_url=vault_url, credential=credential)

    content_type = "text/plain"
    tags = {"foo": "updated tag"}

    updated_secret = secret_client.update_secret("secret-name", content_type=content_type, tags=tags)

    print(updated_secret.version)
    print(updated_secret.updated)
    print(updated_secret.content_type)
    print(updated_secret.tags)
```

### Delete a Secret
`delete_secret` deletes a secret previously stored in the Key Vault.
```python
    from azure.identity import AsyncClientSecretCredential
    from azure.security.keyvault import SecretClient

    credential = AsyncClientSecretCredential(client_id=client_id, secret=client_secret, tenant_id=tenant_id)
    # Create a new secret client using a client secret credential
    secret_client = SecretClient(vault_url=vault_url, credential=credential)

    secret = secret_client.delete_secret("secret-name")
    
    print(deleted_secret.name)
    print(deleted_secret.deleted_date)
```

### Async operations
Python’s asyncio package (introduced in Python 3.4) and its two keywords `async` and `await` serves to declare, build, execute, and manage asynchronous code.
The following example provides a code snippet demonstrating a way to perform async operations in the Secret Client library:

### Async create a secret
```python
    import asyncio

    from azure.identity import AsyncClientSecretCredential
    from azure.security.keyvault.aio import SecretClient

    credential = AsyncClientSecretCredential(client_id=client_id, secret=client_secret, tenant_id=tenant_id)
    # Create a new secret client using a client secret credential
    secret_client = SecretClient(vault_url=vault_url, credential=credential)

    # Sends secret data and asynchronously waits until acknowledgement is received
    secret = await secret_client.set_secret("secret-name", "secret-value", enabled=True)
    print(secret.version)
    print(secret.enabled)
```

## Troubleshooting
### General
The Key Vault APIs generate exceptions that can fall into one of the azure-core defined exceptions. For more detailed infromation about exceptions and how to deal with them, see [Azure Core exceptions](TODO).

### Logging
This SDK uses Python standard logging library. You can configure logging print out debugging information to the stdout or anywhere you want.

```python 
import logging
logging.basicConfig(level=logging.DEBUG)
```
Http request and response details are printed to stdout with this logging config.

###  Documentation
Reference documentation is available at docs.microsoft.com/python/api/azure-security-keyvault [TODO: update link]

## Provide Feedback
If you encounter any bugs or have suggestions, please file an issue in the Issues section of the project.

## Contributing
This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the Microsoft Open Source Code of Conduct. For more information see the Code of Conduct FAQ or contact opencode@microsoft.com with any additional questions or comments.