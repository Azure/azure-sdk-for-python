# Azure Key Vault client library for Python
Azure Key Vault is a tool for securely storing and accessing keys, secrets and certificates.

Cloud applications and services use cryptographic keys and secrets to help keep information secure. Azure Key Vault safeguards these keys, secrets and certificates. When you use Key Vault, you can encrypt authentication keys, storage account keys, data encryption keys, .pfx files, and passwords by using keys that are protected by hardware security modules (HSMs).

Use the Key Vault client library to:

* Securely store and control access to tokens, passwords, certificates, API keys, and other secrets.
* Create and control encryption keys that encrypt your data.
* Provision, manage, and deploy public and private Secure Sockets Layer/Transport Layer Security (SSL/TLS) certificates for use with Azure and your internal connected resources.
* Use either software or FIPS 140-2 Level 2 validated HSMs to help protect secrets and keys.

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault) | [Package (Pypi)](https://pypi.org/project/azure-security-keyvault/) | [API reference documentation](https://docs.microsoft.com/python/api/azure-security-keyvault) | [Product documentation](https://docs.microsoft.com/en-gb/azure/key-vault/)
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
Interaction with Key Vault starts with an instance of the KeyVaultClient class. vault_url, credentials, config=None You need the vault url, azure credentials, and the client configuration to instantiate the client object.

### Get credentials
You can find credential information in [Azure Portal](https://portal.azure.com/).

### Create client
The following code snippet demonstrates a way you can instantiate the KeyVaultClient object:
```python
    from azure.security.keyvault import VaultClient
    from azure.common.credentials import ServicePrincipalCredentials

    credentials = ServicePrincipalCredentials(
        client_id=client_id, secret=client_secret, tenant=tenant_id, resource="https://vault.azure.net"
    )

    # Create a new Vault client using Azure credentials
    vault_client = VaultClient(vault_url=vault_url, credentials=credentials)
```
## Key concepts
### Vault
  A user can create a key vault and gain full access and control over it. When using Key Vault, application developers no longer need to store security information in their application. Not having to store security information in applications eliminates the need to make this information part of the code.

### Vault Client:
A vault client performs interactions with the Keys and Secrets client for creating and getting an instance of the Keys/Secrets client. An asynchronous and synchronous, VaultClient, client exists in the SDK allowing for selection of a client based on an application's use case.

## Examples
The following sections provide several code snippets covering some of the most common Key Vault related tasks, including:
* [Create a Secret Client](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault#create-a-secret-client)
* [Create a Key Client](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault#create-a-key-client)

### Create a Secret Client
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
```

### Create a Key Client
```python
    from azure.common.credentials import ServicePrincipalCredentials
    from azure.security.keyvault import VaultClient

    credentials = ServicePrincipalCredentials(
        client_id=client_id, secret=client_secret, tenant=tenant_id, resource="https://vault.azure.net"
    )

    # Create a new Vault client using Azure credentials
    vault_client = VaultClient(vault_url=vault_url, credentials=credentials)
    # retrieves an instance of Key Client
    key_client = vault_client.keys
```

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

## Next steps
* Set and retrieve a secret [TODO: add link]
* Set and retrieve a key [TODO: add link]

###  Documentation
Reference documentation is available at docs.microsoft.com/python/api/azure-security-keyvault

## Provide Feedback
If you encounter any bugs or have suggestions, please file an issue in the Issues section of the project.

## Contributing
This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the Microsoft Open Source Code of Conduct. For more information see the Code of Conduct FAQ or contact opencode@microsoft.com with any additional questions or comments.