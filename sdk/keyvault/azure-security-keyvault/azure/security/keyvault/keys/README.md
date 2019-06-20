# Azure Key Vault Key client library for Python
Azure Key Vault allows you to create and store keys in the Key Vault. Azure Key Vault client supports RSA keys and elliptic curve keys, each with corresponding support in hardware security modules (HSM).

 Multiple keys, and multiple versions of the same key, can be kept in the Key Vault. Cryptographic keys in Key Vault are represented as [JSON Web Key [JWK]](https://tools.ietf.org/html/rfc7517) objects. This library offers operations to create, retrieve, update, delete, purge, backup, restore and list the keys and its versions.

[Source code](/azure/security/keyvault/keys) | [Package (PyPI)](TODO) | [API reference documentation](TODO) | [Product documentation](https://docs.microsoft.com/en-us/azure/key-vault/) | [Samples](/azure/security/keyvault/keys/samples)
## Getting started
### Install the package
Install the Azure Key Vault client library for Python with [pip](https://pypi.org/project/pip/):

```Bash
pip install azure-security-keyvault
```

### Prerequisites
* An [Azure subscription](https://azure.microsoft.com/free/).
* Python 2.7, 3.5 or later to use this package.
* An existing Key Vault. If you need to create a Key Vault, you can use the [Azure Cloud Shell](https://shell.azure.com/bash) to create one with this Azure CLI command. Replace `<your-resource-group-name>` and `<your-key-vault-name>` with your own, unique names:

    ```Bash
    az keyvault create --resource-group <your-resource-group-name> --name <your-key-vault-name>
    ```

### Authenticate the client
In order to interact with the Key Vault service, you'll need to create an instance of the [KeyClient](TODO-rst-docs) class. You would need a **vault url** and **client secret credentials (client id, client secret, tenant id)** to instantiate a client object for using the `DefaultAzureCredential` examples in the README. `DefaultAzureCredential` way of authentication by providing client secret credentials is being used in this getting started section but you can find more ways to authenticate with [azure-identity](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity).

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

* Grant the above mentioned application authorization to perform key operations on the keyvault:
    ```Bash
    az keyvault set-policy --name <your-key-vault-name> --spn $AZURE_CLIENT_ID --key-permissions backup delete get list set
    ```
    > --key-permissions:
    > Accepted values: backup, delete, get, list, purge, recover, restore, set

* Use the above mentioned Key Vault name to retreive details of your Vault which also contains your Key Vault URL:
    ```Bash
    az keyvault show --name <your-key-vault-name> 
    ```

#### Create Key client
Once you've populated the **AZURE_CLIENT_ID**, **AZURE_CLIENT_SECRET** and **AZURE_TENANT_ID** environment variables and replaced **your-vault-url** with the above returned URI for example "<https://myvault.vault.azure.net>", you can create the [KeyClient](TODO-rst-docs):

```python
from azure.identity import DefaultAzureCredential
from azure.security.keyvault import KeyClient

credential = DefaultAzureCredential()

# Create a new Key client using the default credential
key_client = KeyClient(vault_url=<your-vault-url>, credential=credential)
```
## Key concepts
### Key
  Azure Key Vault supports multiple key types and algorithms, and enables the use of Hardware Security Modules (HSM) for high value keys. In addition to the key value, the following attributes may be specified:
* enabled: Specifies whether the key is enabled and useable for cryptographic operations.
* not_before: Identifies the time before which the key must not be used for cryptographic operations.
* expires: Identifies the expiration time on or after which the key MUST NOT be used for cryptographic operation.
* created: Indicates when this version of the key was created.
* updated: Indicates when this version of the key was updated.

### Key Client:
The Key client performs the interactions with the Azure Key Vault service for getting, setting, updating, deleting, and listing keys and its versions. An asynchronous and synchronous, KeyClient, client exists in the SDK allowing for selection of a client based on an application's use case. Once you've initialized a Key, you can interact with the primary resource types in Key Vault.

## Examples
The following section provides several code snippets using the above created `key_client`, covering some of the most common Azure Key Vault Key service related tasks, including:
* [Create a Key](#create-a-key)
* [Retrieve a Key](#retrieve-a-key)
* [Update an existing Key](#update-an-existing-key)
* [Delete a Key](#delete-a-key)
* [List Keys](#list-keys)
* [Async create a Key](#async-create-a-key)
* [Async list Keys](#async-list-keys)

### Create a Key
`create_key` creates a Key to be stored in the Azure Key Vault. If a key with the same name already exists, then a new version of the key is created.
```python

# Create a key of any type
key = key_client.create_key("key-name", "RSA-HSM")

# Create an RSA key with size specification (optional)
rsa_key = key_client.create_rsa_key("rsa-key-name", hsm=False, size=2048)

# Create an EC key with curve specification and using HSM
ec_key = key_client.create_key("ec-key-name", hsm=True)

print(key.name)
print(key.key_material.kty)

print(rsa_key.name)
print(rsa_key.key_material.kty)

print(ec_key.name)
print(ec_key.key_material.kty)
```

### Retrieve a Key
`get_key` retrieves a key previously stored in the Key Vault.
```python
key = key_client.get_key("key-name")

print(key.name)
print(key.value)
```

### Update an existing Key
`update_key` updates a key previously stored in the Key Vault.
```python
# Clients may specify additional application-specific metadata in the form of tags.
tags = {"foo": "updated tag"}

updated_key = key_client.update_key("key-name", tags=tags)

print(updated_key.name)
print(updated_key.version)
print(updated_key.updated)
print(updated_key.tags)

```

### Delete a Key
`delete_key` deletes a key previously stored in the Key Vault. When [soft-delete](https://docs.microsoft.com/en-us/azure/key-vault/key-vault-ovw-soft-delete) is not enabled for the Key Vault, this operation permanently deletes the key.
```python
deleted_key = key_client.delete_key("key-name")

print(deleted_key.name)
print(deleted_key.deleted_date)
```
### List keys
This example lists all the keys in the specified Key Vault.
```python
keys = key_client.list_keys()

for key in keys:
    # the list doesn't include values or versions of the keys
    print(key.name)
```

### Async operations
Python’s [asyncio package](https://pypi.org/project/asyncio/)and its two keywords `async` and `await` serves to declare, build, execute, and manage asynchronous code.
The package supports async API on Python 3.5+ and is identical to synchronous API.

The following examples provide code snippets for performing async operations in the Key Client library:

### Async create a Key
This example creates a key in the Key Vault with the specified optional arguments.
```python
from azure.identity import AsyncDefaultAzureCredential
from azure.security.keyvault.aio import KeyClient

# for async operations use AsyncDefaultAzureCredential
credential = AsyncDefaultAzureCredential()
# Create a new Key client using the default credential
key_client = KeyClient(vault_url=vault_url, credential=credential)

key = await key_client.set_key("key-name", "key-value", enabled=True)

print(key.name)
print(key.version)
print(key.enabled)
```
### Async list keys
This example lists all the keys in the specified Key Vault.
```python
keys = key_client.list_keys()

async for key in keys:
    # the list doesn't include versions of the keys
    print(key.name)
```

## Troubleshooting
### General
Key Vault clients raise exceptions defined in azure-core. For more detailed infromation about exceptions and how to deal with them, see [Azure Core exceptions](TODO).

For example, if you try to retrieve a key after it is deleted a `404` error is returned, indicating resource not found. In the following snippet, the error is handled gracefully by catching the exception and displaying additional information about the error.
```python
try:
    key_client.get_key("deleted_key")
except ResourceNotFoundError as e:
    print(e.message)

Output: "Key not found:deleted_key"
```
### Logging
This library by default has network trace logging enabled. This will be logged at DEBUG level. The logging policy in the pipeline is used to output HTTP network trace to the configured logger. You can configure logging to print out debugging information to the stdout or write it to a file using the following example:

```python
import sys
import logging

# Create a logger for the 'azure' SDK
logger = logging.getLogger("azure")
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

# Configure a file output
file_handler = logging.FileHandler(filename)
logger.addHandler(file_handler)

# Enable network trace logging. This will be logged at DEBUG level.
# By default, network tracing logging is disabled.
config = KeyClient.create_config()
config.logging_policy = NetworkTraceLoggingPolicy(logging_enable=True, **kwargs)
```
The logger can also be enabled per operation.

```python
key = key_client.get_key("key-name", logging_enable=True)
```

## Next steps
Several KeyVault Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Key Vault:
* [test_examples_keys.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-security-keyvault/tests/test_examples_keys.py) and [test_examples_keys_async.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-security-keyvault/tests/test_examples_keys_async.py) - Contains the code snippets working with Key Vault keys.
* [hello_world.py](TODO) and [hello_world_async.py](TODO) - Python code for working with Azure Key Vault, including:
  * Create a key
  * Get an existing key
  * Update an existing key
  * Delete key
* [backup_restore_operations.py](TODO) and [backup_restore_operations_async.py](TODO) - Example code for working with Key Vault keys backup and recovery, including:
  * Create key
  * Backup a key
  * Delete the key
  * Use backed up key bytes to restore the deleted key

 ###  Additional Documentation
For more extensive documentation on Azure Key Vault, see the [API reference documentation](TODO).

## Contributing
This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the Code of Conduct FAQ or contact opencode@microsoft.com with any additional questions or comments.