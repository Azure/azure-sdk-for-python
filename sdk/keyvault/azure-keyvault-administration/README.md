# Azure KeyVault Administration client library for .NET
Azure Key Vault helps solve the following problems:
- Vault administration (this library) - full backup / restore, and key-level role-based access control (RBAC) of vaults.
- Cryptographic key management ([azure-keyvault-keys](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys)) - create, store, and control
access to the keys used to encrypt your data
- Secrets management
([azure-keyvault-secrets](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-secrets)) -
securely store and control access to tokens, passwords, certificates, API keys,
and other secrets
- Certificate management
([azure-keyvault-certificates](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-certificates)) -
create, manage, and deploy public and private SSL/TLS certificates

## Getting started
### Install packages
Install [azure-keyvault-administration][pypi_package_administration] and
[azure-identity][azure_identity_pypi] with [pip][pip]:
```Bash
pip install azure-keyvault-administration azure-identity
```
[azure-identity][azure_identity] is used for Azure Active Directory
authentication as demonstrated below.

### Prerequisites
* An [Azure subscription][azure_sub]
* Python 2.7, 3.5.3, or later
* A Key Vault. If you need to create one, See the final two steps in the next section for details on creating the Key Vault with the Azure CLI.

### Authenticate the client
This document demonstrates using [DefaultAzureCredential][default_cred_ref]
to authenticate as a service principal. However, [KeyVaultAccessControlClient][rbac_client_docs]
accepts any [azure-identity][azure_identity] credential. See the
[azure-identity][azure_identity] documentation for more information about other
credentials.

#### Create/Get credentials
This [Azure Cloud Shell][azure_cloud_shell] snippet shows how to create a
new service principal. Before using it, replace "your-application-name" with
a more appropriate name for your service principal.

* Create a service principal:
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

* Take note of the service principal objectId
    ```Bash
    az ad sp show --id <appId> --query objectId
    ```


    > Output:
    > ```
    > "<your-service-principal-object-id>"
    > ```

* Use the output to set **AZURE_CLIENT_ID** ("appId" above), **AZURE_CLIENT_SECRET**
    ("password" above) and **AZURE_TENANT_ID** ("tenant" above) environment variables.
    The following example shows a way to do this in Bash:
    ```Bash
    export AZURE_CLIENT_ID="generated app id"
    export AZURE_CLIENT_SECRET="random password"
    export AZURE_TENANT_ID="tenant id"
    ```

* Create the Key Vault and grant the above mentioned application authorization to perform administrative operations on the Azure Key Vault (replace `<your-resource-group-name>` and `<your-key-vault-name>` with your own, unique names and `<your-service-principal-object-id>` with the value from above):
    ```Bash
    az keyvault create --hsm-name <your-key-vault-name> --resource-group <your-resource-group-name> --administrators <your-service-principal-object-id> --location <your-azure-location>
    ```

* Use the above mentioned Azure Key Vault name to retrieve details of your Vault which also contains your Azure Key Vault URL:
    ```Bash
    az keyvault show --hsm-name <your-key-vault-name>
    ```

#### Create a client
Once the **AZURE_CLIENT_ID**, **AZURE_CLIENT_SECRET** and
**AZURE_TENANT_ID** environment variables are set,
[DefaultAzureCredential][default_cred_ref] will be able to authenticate the
[KeyVaultAccessControlClient][rbac_client_docs].

Constructing the client also requires your vault's URL, which you can
get from the Azure CLI or the Azure Portal. In the Azure Portal, this URL is
the vault's "DNS Name".

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultAccessControlClient

credential = DefaultAzureCredential()

client = KeyVaultAccessControlClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
```
## Key concepts

### Role Definition
A role definition defines the operations that can be performed, such as read, write, and delete. It can also define the operations that are excluded from allowed operations.

A role definition is specified as part of a role assignment.

### Role Assignment.
A role assignment is the association of a role definition to a service principal. They can be created, listed, fetched individually, and deleted.

### KeyVaultAccessControlClient
A `KeyVaultAccessControlClient` provides both synchronous and asynchronous operations allowing for management of role definitions and role assignments.

## Examples
This section conntains code snippets covering common tasks:
* [List the role definitions](#list-the-role-definitions "List the role definitions")
* [Create, Get, and Delete a role assignment](#create-get-and-delete-a-role-assignment "Create, Get, and Delete a role assignment")

### List the role definitions
List the role definitions available for assignment.

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultAccessControlClient

credential = DefaultAzureCredential()

client = KeyVaultAccessControlClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)

role_definitions = client.list_role_definitions(role_scope="/")  # this is the global scope

for role_definition in role_definitions:
    print(role_definition.id)
    print(role_definition.role_name)
    print(role_definition.description)
```

### Create, Get, and Delete a role assignment
Assign a role to a service principal. This will require a role definition id from the list retrieved in the [above snippet](#list-the-role-definitions) and the principal object id retrieved in the [Create/Get credentials](#create/get-credentials)

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultAccessControlClient

credential = DefaultAzureCredential()

client = KeyVaultAccessControlClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)

role_scope = "/"  # setting the scope to the global scope
role_assignment_name = "<role-assignment-name>"  # must be a UUID
role_definition = "<role-definition>"  # Replace <role-definition-id> with a role definition from the definitions returned from the previous example
principal_id = "<your-service-principal-object-id>"

# first, let's create the role assignment
role_assignment = client.create_role_assignment(role_scope, role_assignment_name, role_definition.id, principal_id)
print(role_assignment.name)
print(role_assignment.principal_id)
print(role_assignment.role_definition_id)

# now, we get it
role_assignment = client.get_role_assignment(role_scope, role_assignment.name)
print(role_assignment.name)
print(role_assignment.principal_id)
print(role_assignment.role_definition_id)

# finally, we delete this role assignment
role_assignment = client.delete_role_assignment(role_scope, role_assignment.name)
print(role_assignment.name)
print(role_assignment.principal_id)
print(role_assignment.role_definition_id)

```


## Troubleshooting
### General
Key Vault clients raise exceptions defined in [azure-core][azure_core_exceptions].
For example, if you try to get a role assignment that doesn't exist, [KeyVaultAccessControlClient][rbac_client_docs]
raises [ResourceNotFoundError](https://aka.ms/azsdk-python-core-exceptions-resource-not-found-error):

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultAccessControlClient
from azure.core.exceptions import ResourceNotFoundError

credential = DefaultAzureCredential()
client = KeyVaultAccessControlClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)

try:
    client.get_role_assignment("/", "which-does-not-exist")
except ResourceNotFoundError as e:
    print(e.message)
```

## Next steps

Content forthcoming

## Contributing

This project welcomes contributions and suggestions.  Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution. For
details, visit [cla.microsoft.com][cla].

This project has adopted the [Microsoft Open Source Code of Conduct][coc].
For more information see the [Code of Conduct FAQ][coc_faq]
or contact [opencode@microsoft.com][coc_contact] with any
additional questions or comments.

<!-- LINKS -->
[azure_cloud_shell]: https://shell.azure.com/bash
[azure_core_exceptions]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/core/azure-core#azure-core-library-exceptions
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity
[azure_identity_pypi]: https://pypi.org/project/azure-identity/
[azure_sub]: https://azure.microsoft.com/free/
[default_cred_ref]: https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[keyvault_docs]: https://docs.microsoft.com/azure/key-vault/
[pip]: https://pypi.org/project/pip/
[pypi_package_administration]: https://pypi.org/project/azure-keyvault-administration/
[reference_docs]: https://aka.ms/azsdk/python/keyvault-keys/docs
[rbac_client_docs]: https://aka.ms/azsdk/python/keyvault-administration/docs#azure.keyvault.administration.KeyVaultAccessControlClient


![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-net%2Fsdk%2Ftables%2FAzure.Data.Tables%2FREADME.png)