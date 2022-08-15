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

[Source code][library_src] | [Package (PyPI)][pypi_package_administration] | [API reference documentation][reference_docs] | [Product documentation][keyvault_docs] | [Samples][administration_samples]

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_.

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
* Python 3.6 or later
* An existing [Key Vault Managed HSM][managed_hsm]. If you need to create one, you can do so using the Azure CLI by following the steps in [this document][managed_hsm_cli].

### Authenticate the client
In order to interact with the Azure Key Vault service, you will need an instance of either a [KeyVaultAccessControlClient](#create-a-keyvaultaccesscontrolclient) or [KeyVaultBackupClient](#create-a-keyvaultbackupclient), as well as a **vault url** (which you may see as "DNS Name" in the Azure Portal) and a credential object. This document demonstrates using a [DefaultAzureCredential][default_cred_ref], which is appropriate for most scenarios, including local development and production environments. We recommend using a [managed identity][managed_identity] for authentication in production environments.

See [azure-identity][azure_identity] documentation for more information about other methods of authentication and their corresponding credential types.

#### Create a KeyVaultAccessControlClient
After configuring your environment for the [DefaultAzureCredential][default_cred_ref] to use a suitable method of authentication, you can do the following to create an access control client (replacing the value of `vault_url` with your Managed HSM's URL):
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultAccessControlClient

credential = DefaultAzureCredential()

client = KeyVaultAccessControlClient(
    vault_url="https://my-managed-hsm-name.managedhsm.azure.net/",
    credential=credential
)
```

> **NOTE:** For an asynchronous client, import `azure.keyvault.administration.aio`'s `KeyVaultAccessControlClient` instead.

#### Create a KeyVaultBackupClient
After configuring your environment for the [DefaultAzureCredential][default_cred_ref] to use a suitable method of authentication, you can do the following to create a backup client (replacing the value of `vault_url` with your Managed HSM's URL):
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultBackupClient

credential = DefaultAzureCredential()

client = KeyVaultBackupClient(
    vault_url="https://my-managed-hsm-name.managedhsm.azure.net/",
    credential=credential
)
```

> **NOTE:** For an asynchronous client, import `azure.keyvault.administration.aio`'s `KeyVaultBackupClient` instead.

## Key concepts

### Role definition
A role definition defines the operations that can be performed, such as read, write, and delete. It can also define the operations that are excluded from allowed operations.

A role definition is specified as part of a role assignment.

### Role assignment
A role assignment is the association of a role definition to a service principal. They can be created, listed, fetched individually, and deleted.

### KeyVaultAccessControlClient
A `KeyVaultAccessControlClient` manages role definitions and role assignments.

### KeyVaultBackupClient
A `KeyVaultBackupClient` performs full key backups, full key restores, and selective key restores.

## Examples
This section contains code snippets covering common tasks:
* Access control
    * [List all role definitions](#list-all-role-definitions)
    * [Set, get, and delete a role definition](#set-get-and-delete-a-role-defintion)
    * [List all role assignments](#list-all-role-assignments)
    * [Create, get, and delete a role assignment](#create-get-and-delete-a-role-assignment)
* Backup and restore
    * [Perform a full key backup](#perform-a-full-key-backup)
    * [Perform a full key restore](#perform-a-full-key-restore)

### List all role definitions
List the role definitions available for assignment.

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultAccessControlClient, KeyVaultRoleScope

credential = DefaultAzureCredential()

client = KeyVaultAccessControlClient(
    vault_url="https://my-managed-hsm-name.managedhsm.azure.net/",
    credential=credential
)

# this will list all role definitions available for assignment
role_definitions = client.list_role_definitions(KeyVaultRoleScope.GLOBAL)

for definition in role_definitions:
    print(definition.id)
    print(definition.role_name)
    print(definition.description)
```

### Set, get, and delete a role definition

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

client = KeyVaultAccessControlClient(
    vault_url="https://my-managed-hsm-name.managedhsm.azure.net/",
    credential=credential
)

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

client = KeyVaultAccessControlClient(
    vault_url="https://my-managed-hsm-name.managedhsm.azure.net/",
    credential=credential
)

# this will list all role assignments
role_assignments = client.list_role_assignments(KeyVaultRoleScope.GLOBAL)

for assignment in role_assignments:
    print(assignment.name)
    print(assignment.principal_id)
    print(assignment.role_definition_id)
```

### Create, get, and delete a role assignment
Assign a role to a service principal. This will require a role definition ID and service principal object ID. You can use an ID from the retrieved [list of role definitions](#list-all-role-definitions) for the former, and an assignment's `principal_id` from the list retrieved in the [above snippet](#list-all-role-assignments) for the latter.

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultAccessControlClient, KeyVaultRoleScope

credential = DefaultAzureCredential()

client = KeyVaultAccessControlClient(
    vault_url="https://my-managed-hsm-name.managedhsm.azure.net/",
    credential=credential
)

# Replace <role-definition-id> with the id of a definition from the fetched list from an earlier example
role_definition_id = "<role-definition-id>"
# Replace <service-principal-object-id> with the principal_id of an assignment returned from the previous example
principal_id = "<service-principal-object-id>"

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
Several samples are available in the Azure SDK for Python GitHub repository. These samples provide example code for additional Key Vault scenarios:
| File | Description |
|-------------|-------------|
| [access_control_operations.py][access_control_operations_sample] | create/update/delete role definitions and role assignments |
| [access_control_operations_async.py][access_control_operations_async_sample] | create/update/delete role definitions and role assignments with an async client |
| [backup_restore_operations.py][backup_operations_sample] | full backup and restore |
| [backup_restore_operations_async.py][backup_operations_async_sample] | full backup and restore with an async client |

###  Additional documentation
For more extensive documentation on Azure Key Vault, see the [API reference documentation][reference_docs].

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
[access_control_operations_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-administration/samples/access_control_operations.py
[access_control_operations_async_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-administration/samples/access_control_operations_async.py
[administration_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-administration/samples
[azure_cloud_shell]: https://shell.azure.com/bash
[azure_core_exceptions]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core#azure-core-library-exceptions
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
[azure_identity_pypi]: https://pypi.org/project/azure-identity/
[azure_sub]: https://azure.microsoft.com/free/

[backup_operations_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-administration/samples/backup_restore_operations.py
[backup_operations_async_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-administration/samples/backup_restore_operations_async.py
[best_practices]: https://docs.microsoft.com/azure/key-vault/managed-hsm/best-practices
[built_in_roles]: https://docs.microsoft.com/azure/key-vault/managed-hsm/built-in-roles

[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/

[default_cred_ref]: https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential

[keyvault_docs]: https://docs.microsoft.com/azure/key-vault/

[library_src]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-administration/azure/keyvault/administration

[managed_hsm]: https://docs.microsoft.com/azure/key-vault/managed-hsm/overview
[managed_hsm_cli]: https://docs.microsoft.com/azure/key-vault/managed-hsm/quick-create-cli
[managed_identity]: https://docs.microsoft.com/azure/active-directory/managed-identities-azure-resources/overview

[pip]: https://pypi.org/project/pip/
[pypi_package_administration]: https://pypi.org/project/azure-keyvault-administration

[reference_docs]: https://aka.ms/azsdk/python/keyvault-administration/docs


![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Fkeyvault%2Fazure-keyvault-administration%2FREADME.png)
