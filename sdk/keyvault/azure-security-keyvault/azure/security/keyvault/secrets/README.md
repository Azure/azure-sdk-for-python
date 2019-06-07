# Azure Key Vault Secret client library for Python
Azure Key Vault is a cloud service that provides a secure storage of secrets, such as passwords and database connection strings. Secret client library allows you to securely store and tightly control the access to tokens, passwords, API keys, and other secrets. This library offers operations to create, retrieve, update, delete, purge,backup, restore and and list the secrets and its versions.

Use the secret client library to create and manage secrets.

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault/azure/security/keyvault/secrets) | [Package (Pypi)](TODO) | [API reference documentation](TODO) | [Product documentation](TODO)
## Getting started
### Install the package
Install the Azure Key Vault client library for Python with pip:

`$ pip install azure-security-keyvault
`

#### Prerequisites
* An [Azure subscription](https://azure.microsoft.com/free/).
* Python 2.7, 3.4 or later to use this package.
* An existing Key Vault. If you need to create a Key Vault, you can use the [Azure Cloud Shell](https://shell.azure.com/bash) to create one with this Azure CLI command:

`az keyvault create --resource-group <resource-group-name> --name <key-vault-name>`

### Authenticate the client
In order to interact with the Key Vault service, you'll need to create an instance of the [KeyVaultClient](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault/azure/security/keyvault) class. You need a vault url, client secret credentials (client id, client secret, tenant id) and a [resource url](https://vault.azure.net) to instantiate a client object.

 #### Create/Get credentials
Use the [Azure CLI](https://docs.microsoft.com/cli/azure) snippet below to create/get client secret credentials.

 * Create a service principal and configure its access to Azure resources:

     `az ad sp create-for-rbac -n <your-application-name> --skip-assignment`
    > If you don't specify a password, one will be created for you.
* Grant the above mentioned application authorization to perform secret and key operations on the keyvault:
     `az keyvault set-policy --name <key-vault-name> --spn <your-service-principal-id> --secret-permissions <secret-permissions> --key-permissions <key-permissions>`

#### Create Secret client
Once you have the `client_id`, `client_secret` and `tenant_id` from above, you can create the [SecretClient](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-security-keyvault/azure/security/keyvault/secrets/_client.py):
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
* [List Secrets](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault#list-secrets)
* [Async create a Secret](https://github.com/samvaity/azure-sdk-for-python/tree/secrets-track2-readme/sdk/keyvault/azure-security-keyvault/azure/security/keyvault/secrets#async-create-a-secret)
* [Async list Secrets](https://github.com/samvaity/azure-sdk-for-python/tree/secrets-track2-readme/sdk/keyvault/azure-security-keyvault/azure/security/keyvault/secrets#async-list-secrets)

### Create a Secret
`set_secret` creates a Secret to be stored in the Azure Key Vault. If a secret with the same name already exists then a new version of the secret is created.
```python
    from azure.identity import AsyncClientSecretCredential
    from azure.security.keyvault import SecretClient

    credential = AsyncClientSecretCredential(client_id=client_id, secret=client_secret, tenant_id=tenant_id)
    # Create a new secret client using a client secret credential
    secret_client = SecretClient(vault_url=vault_url, credential=credential)

    secret = secret_client.set_secret("secret-name", "secret-value", enabled=True)
    
    print(secret.id)
    print(secret.value)
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
    
    print(secret.id)
    print(secret.value)
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
   
    print(secret.id)
    print(secret.value)
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
    
    print(deleted_secret.id)
    print(deleted_secret.name)
    print(deleted_secret.deleted_date)
```
### List secrets
This example lists all the secrets in the specified Key Vault.
```python
    from azure.identity import AsyncClientSecretCredential
    from azure.security.keyvault.aio import SecretClient

    credential = AsyncClientSecretCredential(client_id=client_id, secret=client_secret, tenant_id=tenant_id)
    # Create a new secret client using a client secret credential
    secret_client = SecretClient(vault_url=vault_url, credential=credential)

    secrets = secret_client.list_secrets()

    for secret in secrets:
        # the list doesn't include values or versions of the secrets
        print(secret.id)
        print(secret.name)
```

### Async operations
Python’s asyncio package (introduced in Python 3.4) and its two keywords `async` and `await` serves to declare, build, execute, and manage asynchronous code.
The following examples provides a code snippets for performing async operations in the Secret Client library:

### Async create a secret
This example creates a secret in the specified Key Vault with the specified optional arguments.
```python
    import asyncio

    from azure.identity import AsyncClientSecretCredential
    from azure.security.keyvault.aio import SecretClient

    credential = AsyncClientSecretCredential(client_id=client_id, secret=client_secret, tenant_id=tenant_id)
    # Create a new secret client using a client secret credential
    secret_client = SecretClient(vault_url=vault_url, credential=credential)

    # Sends secret data and asynchronously waits until acknowledgement is received
    secret = await secret_client.set_secret("secret-name", "secret-value", enabled=True)
    
    print(secret.id)
    print(secret.value)
    print(secret.version)
    print(secret.enabled)
```
### Async list secrets
This example lists all the secrets in the specified Key Vault.
```python
    import asyncio

    from azure.identity import AsyncClientSecretCredential
    from azure.security.keyvault.aio import SecretClient

    credential = AsyncClientSecretCredential(client_id=client_id, secret=client_secret, tenant_id=tenant_id)
    # Create a new secret client using a client secret credential
    secret_client = SecretClient(vault_url=vault_url, credential=credential)

    secrets = secret_client.list_secrets()

    # Recieve secrets data asynchronously from Key Vault service
    async for secret in secrets:
        # the list doesn't include values or versions of the secrets
        print(secret.id)
        print(secret.name)
```

## Troubleshooting
### General
The Key Vault APIs generate exceptions that can fall into one of the azure-core defined exceptions. For more detailed infromation about exceptions and how to deal with them, see [Azure Core exceptions](TODO).

For example, if you try to retrieve a secret after it is deleted a `404` error is returned, indicating resource not found. In the following snippet, the error is handled gracefully by catching the exception and displaying additional information about the error.
```python
try:
    client.get_secret("deleted_secret")
except HttpResponseError as e:
    if e.code == 404:
        print(e.message)
    else:
        raise
    
Output: "Secret not found:deleted_secret"
```
### Logging
This SDK uses Python standard logging library. You can configure logging print out debugging information to the stdout or anywhere you want.

```python 
import logging
logging.basicConfig(level=logging.DEBUG)
```
Http request and response details are printed to stdout with this logging config.

## Next steps
Several KeyVault Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Key Vault:
* [test_examples_keyvault.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-security-keyvault/tests/test_examples_keyvault.py) - Contains code snippets found in this article.
* [test_examples_secrets_sync.py](TODO) -  Python code for working with Key Vault secrets, including:
    * Create a secret
    * Get an existing secret
    * Update an existing secret
    * List secret versions
    * Delete secret
* [test_examples_keys_sync.py](TODO) -  Python code for working with Key Vault keys, including:
    * Create a key
    * Get an existing key
    * Update an existing key
    * List key versions
    * Delete key
* [Sample 1](TODO)
* [Sample 2](TODO)

 ###  Additional Documentation
For more extensive documentation on Azure Key Vault, see the reference documentation available at docs.microsoft.com/python/api/azure-security-keyvault--TODO

## Contributing
This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the Microsoft Open Source Code of Conduct. For more information see the Code of Conduct FAQ or contact opencode@microsoft.com with any additional questions or comments.