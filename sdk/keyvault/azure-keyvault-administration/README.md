# Azure Key Vault Administration client library for Python

>**Note:** The Administration library only works with [Managed HSM][managed_hsm] – functions targeting a Key Vault will fail.

Azure Key Vault helps solve the following problems:
- Vault administration (this library) - role-based access control (RBAC), and vault-level backup and restore options
- Cryptographic key management ([azure-keyvault-keys](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys)) - create, store, and control
access to the keys used to encrypt your data
- Secrets management
([azure-keyvault-secrets](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-secrets)) -
securely store and control access to tokens, passwords, certificates, API keys,
and other secrets
- Certificate management
([azure-keyvault-certificates](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-certificates)) -
create, manage, and deploy public and private SSL/TLS certificates

[Package (PyPI)][pypi_package_administration] | [API reference documentation][reference_docs] | [Product documentation][keyvault_docs]

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_
_Python 3.7 or later is required to use this package. For more details, please refer to [Azure SDK for Python version support policy](https://github.com/Azure/azure-sdk-for-python/wiki/Azure-SDKs-Python-version-support-policy)._

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
* Python 3.7 or later
* A [managed HSM][managed_hsm]. If you need to create one, see the final two steps in the next section for details on creating the managed HSM with the Azure CLI.

### Authenticate the client
This document demonstrates using [DefaultAzureCredential][default_cred_ref]
to authenticate as a service principal. However, this package's clients
accept any [azure-identity][azure_identity] credential. See the
[azure-identity][azure_identity] documentation for more information about other
credentials.

#### Create and Get credentials
This [Azure Cloud Shell][azure_cloud_shell] snippet shows how to create a
new service principal. Before using it, replace "your-application-name" with
a more appropriate name for your service principal.

* Create a service principal:
    ```Bash
    az ad sp create-for-rbac --name http://your-application-name --skip-assignment
    ```

    > Output:
    > ```json
    > {
    >     "appId": "generated app id",
    >     "displayName": "your-application-name",
    >     "name": "http://your-application-name",
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

* Create the managed HSM and grant the above mentioned service principal authorization to perform administrative operations on the managed HSM (replace `<your-resource-group-name>` and `<your-managed-hsm-name>` with your own, unique names and `<your-service-principal-object-id>` with the value from above):
    ```Bash
    az keyvault create --hsm-name "<your-managed-hsm-name>" --resource-group "<your-resource-group-name>" --administrators <your-service-principal-object-id> --location "<your-azure-location>"
    ```
  This service principal is automatically added to the "Managed HSM Administrators" [built-in role][built_in_roles].

* Activate your managed HSM to enable key and role management. Detailed instructions can be found in [this quickstart guide](https://docs.microsoft.com/azure/key-vault/managed-hsm/quick-create-cli#activate-your-managed-hsm). Create three self signed certificates and download the [Security Domain](https://docs.microsoft.com/azure/key-vault/managed-hsm/security-domain) for your managed HSM:
    > **Important:** Create and store the RSA key pairs and security domain file generated in this step securely.
    ```Bash
    openssl req -newkey rsa:2048 -nodes -keyout cert_0.key -x509 -days 365 -out cert_0.cer
    openssl req -newkey rsa:2048 -nodes -keyout cert_1.key -x509 -days 365 -out cert_1.cer
    openssl req -newkey rsa:2048 -nodes -keyout cert_2.key -x509 -days 365 -out cert_2.cer
    az keyvault security-domain download --hsm-name "<your-managed-hsm-name>" --sd-wrapping-keys ./certs/cert_0.cer ./certs/cert_1.cer ./certs/cert_2.cer --sd-quorum 2 --security-domain-file <your-managed-hsm-name>-SD.json
    ```

* Use the above mentioned managed HSM name to retrieve details of your managed HSM instance which also contains your manged HSM URL (`hsmUri`):
    ```Bash
    az keyvault show --hsm-name "<your-managed-hsm-name>"
    ```

#### Controlling access to your managed HSM
The designated administrators assigned during creation are automatically added to the "Managed HSM Administrators" [built-in role][built_in_roles],
who are able to download a security domain and [manage roles for data plane access][access_control], among other limited permissions.

To perform other actions on keys, you need to assign principals to other roles such as "Managed HSM Crypto User", which can perform non-destructive key operations:

```Bash
az keyvault role assignment create --hsm-name <your-managed-hsm-name> --role "Managed HSM Crypto User" --scope / --assignee-object-id <principal-or-user-object-ID> --assignee-principal-type <principal-type>
```

Please read [best practices][best_practices] for properly securing your managed HSM.

#### Create a client
Once the **AZURE_CLIENT_ID**, **AZURE_CLIENT_SECRET** and
**AZURE_TENANT_ID** environment variables are set,
[DefaultAzureCredential][default_cred_ref] will be able to authenticate the
clients.

There are two clients available in this package – below are snippets demonstrating how to construct
each one of these clients. Constructing a client also requires your managed HSM's URL, which you can
get from the Azure CLI (shown above).

##### Create a KeyVaultAccessControlClient
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultAccessControlClient

credential = DefaultAzureCredential()

client = KeyVaultAccessControlClient(vault_url="https://my-managed-hsm-name.managedhsm.azure.net/", credential=credential)
```

##### Create a KeyVaultBackupClient
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultBackupClient

credential = DefaultAzureCredential()

client = KeyVaultBackupClient(vault_url="https://my-managed-hsm-name.managedhsm.azure.net/", credential=credential)
```

## Key concepts

### Role Definition
A role definition defines the operations that can be performed, such as read, write, and delete. It can also define the operations that are excluded from allowed operations.

A role definition is specified as part of a role assignment.

### Role Assignment.
A role assignment is the association of a role definition to a service principal. They can be created, listed, fetched individually, and deleted.

### KeyVaultAccessControlClient
A `KeyVaultAccessControlClient` manages role definitions and role assignments.

### KeyVaultBackupClient
A `KeyVaultBackupClient` performs full key backups, full key restores, and selective key restores.

## Examples
This section contains code snippets covering common tasks:
* Access Control
    * [List all role definitions](#list-all-role-definitions "List all role definitions")
    * [Set, Get, and Delete a role definition](#set-get-and-delete-a-role-defintion "Set, Get, and Delete a role definition")
    * [List all role assignments](#list-all-role-assignments "List all role assignments")
    * [Create, Get, and Delete a role assignment](#create-get-and-delete-a-role-assignment "Create, Get, and Delete a role assignment")
* Backup and Restore
    * [Perform a full key backup](#perform-a-full-key-backup "Perform a full key backup")
    * [Perform a full key restore](#perform-a-full-key-restore "Perform a full key restore")

### List all role definitions
List the role definitions available for assignment.

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultAccessControlClient, KeyVaultRoleScope

credential = DefaultAzureCredential()

client = KeyVaultAccessControlClient(vault_url="https://my-managed-hsm-name.managedhsm.azure.net/", credential=credential)

# this will list all role definitions available for assignment
role_definitions = client.list_role_definitions(KeyVaultRoleScope.GLOBAL)

for definition in role_definitions:
    print(definition.id)
    print(definition.role_name)
    print(definition.description)
```

### Set, Get, and Delete a role definition

`set_role_definition` can be used to either create a custom role definition or update an existing definition with the specified name.

```python
import uuid
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import (
    KeyVaultAccessControlClient,
    KeyVaultDataAction,
    KeyVaultPermission,
    KeyVaultRoleScope
)

credential = DefaultAzureCredential()

client = KeyVaultAccessControlClient(vault_url="https://my-managed-hsm-name.managedhsm.azure.net/", credential=credential)

# create a custom role definition
permissions = [KeyVaultPermission(allowed_data_actions=[KeyVaultDataAction.READ_HSM_KEY])]
created_definition = client.set_role_definition(KeyVaultRoleScope.GLOBAL, permissions=permissions)

# update the custom role definition
permissions = [
    KeyVaultPermission(allowed_data_actions=[], denied_data_actions=[KeyVaultDataAction.READ_HSM_KEY])
]
updated_definition = client.set_role_definition(
    KeyVaultRoleScope.GLOBAL, permissions=permissions, role_name=created_definition.name
)

# get the custom role definition
definition = client.get_role_definition(KeyVaultRoleScope.GLOBAL, role_name=definition_name)

# delete the custom role definition
deleted_definition = client.delete_role_definition(KeyVaultRoleScope.GLOBAL, role_name=definition_name)
```

### List all role assignments
Before creating a new role assignment in the [next snippet](#create-get-and-delete-a-role-assignment), list all of the current role assignments:

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultAccessControlClient, KeyVaultRoleScope

credential = DefaultAzureCredential()

client = KeyVaultAccessControlClient(vault_url="https://my-managed-hsm-name.managedhsm.azure.net/", credential=credential)

# this will list all role assignments
role_assignments = client.list_role_assignments(KeyVaultRoleScope.GLOBAL)

for assignment in role_assignments:
    print(assignment.name)
    print(assignment.principal_id)
    print(assignment.role_definition_id)
```

### Create, Get, and Delete a role assignment
Assign a role to a service principal. This will require a role definition id from the list retrieved in the [above snippet](#list-all-role-definitions) and the principal object id retrieved in the [Create and Get credentials](#create-and-get-credentials) section.

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultAccessControlClient, KeyVaultRoleScope

credential = DefaultAzureCredential()

client = KeyVaultAccessControlClient(vault_url="https://my-managed-hsm-name.managedhsm.azure.net/", credential=credential)

role_definition_id = "<role-definition-id>"  # Replace <role-definition-id> with the id of a definition returned from the previous example
principal_id = "<your-service-principal-object-id>"

# first, let's create the role assignment
role_assignment = client.create_role_assignment(KeyVaultRoleScope.GLOBAL, role_definition_id, principal_id)
print(role_assignment.name)
print(role_assignment.principal_id)
print(role_assignment.role_definition_id)

# now, we get it
role_assignment = client.get_role_assignment(KeyVaultRoleScope.GLOBAL, role_assignment.name)
print(role_assignment.name)
print(role_assignment.principal_id)
print(role_assignment.role_definition_id)

# finally, we delete this role assignment
role_assignment = client.delete_role_assignment(KeyVaultRoleScope.GLOBAL, role_assignment.name)
print(role_assignment.name)
print(role_assignment.principal_id)
print(role_assignment.role_definition_id)
```

### Perform a full key backup
Back up your entire collection of keys. The backing store for full key backups is a blob storage container using Shared Access Signature authentication.

For more details on creating a SAS token using the `BlobServiceClient`, see the sample [here](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/storage/azure-storage-blob/samples/blob_samples_authentication.py#L105).
Alternatively, it is possible to [generate a SAS token in Storage Explorer](https://docs.microsoft.com/azure/vs-azure-tools-storage-manage-with-storage-explorer?tabs=windows#generate-a-shared-access-signature-in-storage-explorer)

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultBackupClient

credential = DefaultAzureCredential()
client = KeyVaultBackupClient(vault_url="https://my-managed-hsm-name.managedhsm.azure.net/", credential=credential)

# blob storage container URL, for example https://<account name>.blob.core.windows.net/backup
blob_storage_url = "<your-blob-storage-url>"
sas_token = "<your-sas-token>"  # replace with a sas token to your storage account

# Backup is a long-running operation. The client returns a poller object whose result() method
# blocks until the backup is complete, then returns an object representing the backup operation.
backup_poller = client.begin_backup(blob_storage_url, sas_token)
backup_operation = backup_poller.result()

# this is the Azure Storage Blob URL of the backup
print(backup_operation.folder_url)
```


### Perform a full key restore
Restore your entire collection of keys from a backup. The data source for a full key restore is a storage blob accessed using Shared Access Signature authentication.
You will also need the `azure_storage_blob_container_uri` from the [above snippet](#perform-a-full-key-backup).

For more details on creating a SAS token using the `BlobServiceClient`, see the sample [here](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/storage/azure-storage-blob/samples/blob_samples_authentication.py#L105).
Alternatively, it is possible to [generate a SAS token in Storage Explorer](https://docs.microsoft.com/azure/vs-azure-tools-storage-manage-with-storage-explorer?tabs=windows#generate-a-shared-access-signature-in-storage-explorer)

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultBackupClient

credential = DefaultAzureCredential()
client = KeyVaultBackupClient(vault_url="https://my-managed-hsm-name.managedhsm.azure.net/", credential=credential)

sas_token = "<your-sas-token>"  # replace with a sas token to your storage account

# URL to a storage blob, for example https://<account name>.blob.core.windows.net/backup/mhsm-account-2020090117323313
blob_url = "<your-blob-url>"

# Restore is a long-running operation. The client returns a poller object whose wait() method
# blocks until the restore is complete.
restore_poller = client.begin_restore(blob_url, sas_token)
restore_poller.wait()
```

## Troubleshooting

See the `azure-keyvault-administration`
[troubleshooting guide](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-administration/TROUBLESHOOTING.md)
for details on how to diagnose various failure scenarios.

### General
Key Vault clients raise exceptions defined in [azure-core][azure_core_exceptions].
For example, if you try to get a role assignment that doesn't exist, KeyVaultAccessControlClient
raises [ResourceNotFoundError](https://aka.ms/azsdk-python-core-exceptions-resource-not-found-error):

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultAccessControlClient
from azure.core.exceptions import ResourceNotFoundError

credential = DefaultAzureCredential()
client = KeyVaultAccessControlClient(vault_url="https://my-managed-hsm-name.managedhsm.azure.net/", credential=credential)

try:
    client.get_role_assignment("/", "which-does-not-exist")
except ResourceNotFoundError as e:
    print(e.message)
```

Clients from the Administration library can only be used to perform operations on a managed HSM, so attempting to do so on a Key Vault will raise an error.

## Next steps

Content forthcoming

###  Additional Documentation
For more extensive documentation on Azure Key Vault, see the
[API reference documentation][reference_docs].

For more extensive documentation on Managed HSM, see the [service documentation][managed_hsm].

## Contributing
This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct].
For more information, see the
[Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact opencode@microsoft.com with any additional questions or comments.

<!-- LINKS -->
[access_control]: https://docs.microsoft.com/azure/key-vault/managed-hsm/access-control
[azure_cloud_shell]: https://shell.azure.com/bash
[azure_core_exceptions]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core#azure-core-library-exceptions
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
[azure_identity_pypi]: https://pypi.org/project/azure-identity/
[azure_sub]: https://azure.microsoft.com/free/
[best_practices]: https://docs.microsoft.com/azure/key-vault/managed-hsm/best-practices
[built_in_roles]: https://docs.microsoft.com/azure/key-vault/managed-hsm/built-in-roles
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[default_cred_ref]: https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
[keyvault_docs]: https://docs.microsoft.com/azure/key-vault/
[managed_hsm]: https://docs.microsoft.com/azure/key-vault/managed-hsm/
[pip]: https://pypi.org/project/pip/
[pypi_package_administration]: https://pypi.org/project/azure-keyvault-administration
[reference_docs]: https://aka.ms/azsdk/python/keyvault-administration/docs


![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Fkeyvault%2Fazure-keyvault-administration%2FREADME.png)
