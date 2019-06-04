# Azure Key Vault Secret client library for Python
Azure Key Vault is a cloud service that provides a secure storage of secrets, such as passwords and database connection strings. Secret client library allows you to securely store and tightly control the access to tokens, passwords, API keys, and other secrets. This library offers operations to create, retrieve, update, delete, purge, backup, restore and and list the secrets.

Use the secret client library to create and manage secrets.

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault/azure/security/keyvault/secrets) | [Package (Pypi)](https://pypi.org/project/azure-security-keyvault/) | [API reference documentation](https://docs.microsoft.com/python/api/azure-security-keyvault) | [Product documentation](https://docs.microsoft.com/en-gb/azure/key-vault/)
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
In order to interact with the Key Vault service, you'll need to create an instance of the VaultClient class. You need the vault url, azure credentials, and the client configuration to instantiate the client object.

### Get credentials
You can find credential information in [Azure Portal](https://portal.azure.com/).

### Create Secret client
The following code snippet demonstrates a way you can instantiate the KeyVaultClient object:
```python
    from azure.security.keyvault import VaultClient
    from azure.common.credentials import ServicePrincipalCredentials

    credentials = ServicePrincipalCredentials(
        client_id=client_id, secret=client_secret, tenant=tenant_id, resource="https://vault.azure.net"
    )

    # Create a new Vault client using Azure credentials
    vault_client = VaultClient(vault_url=vault_url, credentials=credentials)
    # retrieves an instance of Secret Client
    secret_client = vault_client.secrets
```
## Key concepts
### Secret
  A secret is the fundamental resource within an Azure KeyVault. From a developer's perspective, Key Vault APIs accept and return secret values as strings. In addition to the secret data, the following attributes may be specified:
* expires: Identifies the expiration time on or after which the secret data should not be retrieved.
* nbf: Identifies the time after which the secret will be active.
* enabled: Specifies whether the secret data can be retrieved.
* created: Indicates when this version of the secret was created.(read-only)
* updated: Indicates when this version of the secret was updated.(read-only)

### Secret Client:
The Secret client performs the interactions with the Azure Key Vault service for getting, setting, updating, deleting, and listing secrets. An asynchronous and synchronous, SecretClient, client exists in the SDK allowing for selection of a client based on an application's use case.

## Examples
The following sections provide several code snippets covering some of the most common Azure Key Vault Secret service related tasks, including:
* [Create a Secret](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault#create-a-secret)
* [Retrieve a Secret](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault#retrieve-a-secret)
* [Update an existing Secret](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault#update-an-existing-secret)
* [Delete a Secret](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault#delete-a-secret)

### Create a Secret
`set_secret` creates a Secret to be stored in the Azure Key Vault. If a secret with the same name already exists then a new version of the secret is created.
```python
    from azure.common.credentials import ServicePrincipalCredentials
    from azure.security.keyvault import VaultClient

    credentials = ServicePrincipalCredentials(
        client_id=client_id, secret=client_secret, tenant=tenant_id, resource="https://vault.azure.net"
    )

    # Create a new Vault client using Azure credentials
    vault_client = VaultClient(vault_url=vault_url, credentials=credentials)
    # retrieves an instance of Secret Client
    secret_client = vault_client.secrets

    secret = secret_client.set_secret("secret-name", "secret-value", enabled=True)
    print(secret.version)
    print(secret.enabled)
```

### Retrieve a Secret
`get_secret` retrieves a secret previously stored in the Key Vault.
```python
    from azure.common.credentials import ServicePrincipalCredentials
    from azure.security.keyvault import VaultClient

    credentials = ServicePrincipalCredentials(
        client_id=client_id, secret=client_secret, tenant=tenant_id, resource="https://vault.azure.net"
    )

    # Create a new Vault client using Azure credentials
    vault_client = VaultClient(vault_url=vault_url, credentials=credentials)
    # retrieves an instance of Secret Client
    secret_client = vault_client.secrets

    secret = secret_client.get_secret("secret-name")
    print(secret.version)
```

### Update an existing Secret
`update_secret` updates a secret previously stored in the Key Vault.
```python
    from azure.common.credentials import ServicePrincipalCredentials
    from azure.security.keyvault import VaultClient

    credentials = ServicePrincipalCredentials(
        client_id=client_id, secret=client_secret, tenant=tenant_id, resource="https://vault.azure.net"
    )

    # Create a new Vault client using Azure credentials
    vault_client = VaultClient(vault_url=vault_url, credentials=credentials)
    # retrieves an instance of Secret Client
    secret_client = vault_client.secrets

    content_type = "text/plain"
    tags = {"foo": "updated tag"}
    secret_version = secret.version
    updated_secret = secret_client.update_secret_attributes(
        "secret-name", secret_version, content_type=content_type, tags=tags
    )

    print(updated_secret.version)
    print(updated_secret.updated)
    print(updated_secret.content_type)
    print(updated_secret.tags)
```

### Delete a Secret
`delete_secret` deletes a secret previously stored in the Key Vault.
```python
    from azure.common.credentials import ServicePrincipalCredentials
    from azure.security.keyvault import VaultClient

    credentials = ServicePrincipalCredentials(
        client_id=client_id, secret=client_secret, tenant=tenant_id, resource="https://vault.azure.net"
    )

    # Create a new Vault client using Azure credentials
    vault_client = VaultClient(vault_url=vault_url, credentials=credentials)
    # retrieves an instance of Secret Client
    secret_client = vault_client.secrets

    secret = secret_client.delete_secret("secret-name")
    print(deleted_secret.name)
    print(deleted_secret.deleted_date)
```

For async examples we just have to add await, can we just add one example and use that as the only example for async?

## Troubleshooting
### General
The Key Vault APIs generate exceptions that can fall into one of the azure-core defined [exceptions](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/azure/core/exceptions.py).

### Logging
This SDK uses Python standard logging library. You can configure logging print out debugging information to the stdout or anywhere you want.

```python 
import logging
logging.basicConfig(level=logging.DEBUG)
```
Http request and response details are printed to stdout with this logging config.

###  Documentation
Reference documentation is available at docs.microsoft.com/python/api/azure-security-keyvault

## Provide Feedback
If you encounter any bugs or have suggestions, please file an issue in the Issues section of the project.

## Contributing
This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the Microsoft Open Source Code of Conduct. For more information see the Code of Conduct FAQ or contact opencode@microsoft.com with any additional questions or comments.