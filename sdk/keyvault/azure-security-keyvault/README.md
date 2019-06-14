# Azure Key Vault client library for Python
Azure Key Vault is a tool used for securely storing and accessing keys, secrets and certificates.

Cloud applications and services use cryptographic keys and secrets to help keep information secure. Azure Key Vault safeguards these keys, secrets and certificates. When you use Key Vault, you can encrypt authentication keys, storage account keys, data encryption keys, .pfx files, and passwords by using keys that are protected by hardware security modules (HSMs).

Use the Key Vault client library fro Python to:

* Securely store and control access to tokens, passwords, certificates, API keys, and other secrets.
* Create and control encryption keys that encrypt your data.
* Provision, manage, and deploy public and private Secure Sockets Layer/Transport Layer Security (SSL/TLS) certificates for use with Azure and your internal connected resources.
* Use either software or FIPS 140-2 Level 2 validated HSMs to help protect secrets and keys.

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault) | [Package (Pypi)](TODO) | [API reference documentation](TODO) | [Product documentation](TODO)
# Getting started
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
In order to interact with the Key Vault service, you'll need to create an instance of the [KeyVaultClient](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault/azure/security/keyvault) class. You need a **vault url**, **client secret credentials (client id, client secret, tenant id)** and a [resource url](https://vault.azure.net) to instantiate a client object.

  #### Create/Get credentials
Use the [Azure Cloud Shell](https://shell.azure.com/bash) snippet below to create/get client secret credentials.

  * Create a service principal and configure its access to Azure resources:
    ```Bash
    az ad sp create-for-rbac -n <your-application-name> --skip-assignment
    ```
    Output:
    ```json
    {
        "appId": "fa7c8686-c4f5-4639-ab88-497ee122bad3",
        "displayName": "myspn",
        "name": "http://myspn",
        "password": "30e5c628-a322-3497-8429-52f2f98788c7",
        "tenant": "72f988bf-86f1-41fg-91ab-2d7cd011db47"
    }
    ```
* Use the above returned credentials information to set **AZURE_CLIENT_ID**(appId), **AZURE_CLIENT_SECRET**(password) and **AZURE_TENANT_ID**(tenant) environment variables.
  ```Bash
    export AZURE_CLIENT_ID="fa7c8686-c4f5-4639-ab88-497ee122bad3"
    export AZURE_CLIENT_SECRET="30e5c628-a322-3497-8429-52f2f98788c7"
    export AZURE_TENANT_ID="72f988bf-86f1-41fg-91ab-2d7cd011db47"
  ```

 * Grant the above mentioned application authorization to perform secret operations on the keyvault:
    ```Bash
    az keyvault set-policy --name <your-key-vault-name> --spn $AZURE_CLIENT_ID --secret-permissions backup delete get list set --key-permissions backup delete get list set 
    ```
    > --secret-permissions/key-permissiona:
    > Accepted values: backup, delete, get, list, purge, recover, restore, set

### Create client
Once you've populated the **AZURE_CLIENT_ID**, **AZURE_CLIENT_SECRET** and **AZURE_TENANT_ID** environment variables, you can create the [VaultClient](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-security-keyvault/azure/security/keyvault/vault_client.py):
```python
    from azure.identity import DefaultAzureCredential
    from azure.security.keyvault import VaultClient

    credential = DefaultAzureCredential()

    # Create a new Vault client using a client secret credential
    vault_client = VaultClient(vault_url=<your-vault-url>, credential=credential)
```
## Key concepts
### Vault
A user can create a Key Vault to safeguard and manage cryptographic keys and secrets used by cloud applications and services. When using a Key Vault, application developers no longer need to store security information in their application. Azure key vaults may be created and managed through the Azure portal.

### Vault Client:
A vault client performs interactions with the Keys and Secrets client for creating and getting an instance of the Keys/Secrets client. An asynchronous and synchronous, VaultClient, client exists in the SDK allowing for selection of a client based on an application's use case. The Key Vault client library performs cryptographic key operations and vault operations against the Key Vault service. Once you've initialized a VaultClient, you can interact with the primary resource types in Key Vault.

For more information about these resources, see [What is Azure Key Vault](https://docs.microsoft.com/en-us/azure/key-vault/key-vault-whatis).

## Examples
The following section provides several code snippets using the above created `vault_client`, covering some of the most common Azure Key Vault service related tasks, including:
* [Create a Secret Client](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault#create-a-secret-client)
  * Refer to Secret Client documentation [here](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault/azure/security/keyvault/secrets) to use the secret client library to create and manage secrets.
* [Create a Key Client](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault#create-a-key-client)
  * Refer to Key Client documentation [here](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-security-keyvault/azure/security/keyvault/keys) to use the key client library to create and manage keys.

### Create a Secret Client
```python
    # retrieves an instance of Secret Client
    secret_client = vault_client.secrets
```

### Create a Key Client
```python
    # retrieves an instance of Key Client
    key_client = vault_client.keys
```

## Troubleshooting
### General
he Key Vault APIs generate exceptions that can fall into one of the azure-core defined exceptions. For more detailed infromation about exceptions and how to deal with them, see [Azure Core exceptions](TODO).

### Logging[TODO]
This SDK uses Python standard logging library. You can configure logging print out debugging information to the stdout or anywhere you want.

```python 
import logging
logging.basicConfig(level=logging.DEBUG)
```
Http request and response details are printed to stdout with this logging config.

## Next steps
Several KeyVault Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Key Vault:
* [test_examples_keyvault.py](TODO) - Contains the code snippets working with Key Vault client.
* [hello_world.py](TODO) and [hello_world_async.py](TODO) - Python code for working with Azure Key Vault Secrets, including:
  * Create a secret
  * Get an existing secret
  * Update an existing secret
  * Delete secret
* [hello_world.py](TODO) and [hello_world_async.py](TODO) - Python code for working with Azure Key Vault Keys, including:
  * Create a key
  * Get an existing key
  * Update an existing key
  * Delete key

  ###  Additional Documentation
For more extensive documentation on Azure Key Vault, see the [API reference documentation](TODO).

## Contributing
This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

 When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

 This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the Code of Conduct FAQ or contact opencode@microsoft.com with any additional questions or comments.
