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

[Source code][library_src]
| [Package (PyPI)][pypi_package_administration]
| [Package (Conda)](https://anaconda.org/microsoft/azure-keyvault/)
| [API reference documentation][reference_docs]
| [Product documentation][keyvault_docs]
| [Samples][administration_samples]

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691._
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
* An existing [Key Vault Managed HSM][managed_hsm]. If you need to create one, you can do so using the Azure CLI by following the steps in [this document][managed_hsm_cli].

### Authenticate the client
In order to interact with the Azure Key Vault service, you will need an instance of either a [KeyVaultAccessControlClient](#create-a-keyvaultaccesscontrolclient) or [KeyVaultBackupClient](#create-a-keyvaultbackupclient), as well as a **vault url** (which you may see as "DNS Name" in the Azure Portal) and a credential object. This document demonstrates using a [DefaultAzureCredential][default_cred_ref], which is appropriate for most scenarios, including local development and production environments. We recommend using a [managed identity][managed_identity] for authentication in production environments.

See [azure-identity][azure_identity] documentation for more information about other methods of authentication and their corresponding credential types.

#### Create a KeyVaultAccessControlClient
After configuring your environment for the [DefaultAzureCredential][default_cred_ref] to use a suitable method of authentication, you can do the following to create an access control client (replacing the value of `vault_url` with your Managed HSM's URL):

<!-- SNIPPET:access_control_operations.create_an_access_control_client -->

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultAccessControlClient

MANAGED_HSM_URL = os.environ["MANAGED_HSM_URL"]
credential = DefaultAzureCredential()
client = KeyVaultAccessControlClient(vault_url=MANAGED_HSM_URL, credential=credential)
```

<!-- END SNIPPET -->

> **NOTE:** For an asynchronous client, import `azure.keyvault.administration.aio`'s `KeyVaultAccessControlClient` instead.

#### Create a KeyVaultBackupClient
After configuring your environment for the [DefaultAzureCredential][default_cred_ref] to use a suitable method of authentication, you can do the following to create a backup client (replacing the value of `vault_url` with your Managed HSM's URL):

<!-- SNIPPET:backup_restore_operations.create_a_backup_restore_client -->

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultBackupClient

MANAGED_HSM_URL = os.environ["MANAGED_HSM_URL"]
credential = DefaultAzureCredential()
client = KeyVaultBackupClient(vault_url=MANAGED_HSM_URL, credential=credential)
```

<!-- END SNIPPET -->

> **NOTE:** For an asynchronous client, import `azure.keyvault.administration.aio`'s `KeyVaultBackupClient` instead.

#### Create a KeyVaultSettingsClient
After configuring your environment for the [DefaultAzureCredential][default_cred_ref] to use a suitable method of authentication, you can do the following to create a settings client (replacing the value of `vault_url` with your Managed HSM's URL):

<!-- SNIPPET:settings_operations.create_a_settings_client -->

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultSettingsClient

MANAGED_HSM_URL = os.environ["MANAGED_HSM_URL"]
credential = DefaultAzureCredential()
client = KeyVaultSettingsClient(vault_url=MANAGED_HSM_URL, credential=credential)
```

<!-- END SNIPPET -->

> **NOTE:** For an asynchronous client, import `azure.keyvault.administration.aio`'s `KeyVaultSettingsClient` instead.

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

### KeyVaultSettingsClient

A `KeyVaultSettingsClient` manages Managed HSM account settings.

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
    * [Perform a selective key restore](#perform-a-selective-key-restore)

### List all role definitions
`list_role_definitions` can be used by a `KeyVaultAccessControlClient` to list the role definitions available for
assignment.

<!-- SNIPPET:access_control_operations.list_role_definitions -->

```python
from azure.keyvault.administration import KeyVaultRoleScope

role_definitions = client.list_role_definitions(scope=KeyVaultRoleScope.GLOBAL)
for definition in role_definitions:
    print(f"Role name: {definition.role_name}; Role definition name: {definition.name}")
```

<!-- END SNIPPET -->

### Set, get, and delete a role definition

`set_role_definition` can be used by a `KeyVaultAccessControlClient` to either create a custom role definition or update
an existing definition with the specified unique `name` (a UUID).

<!-- SNIPPET:access_control_operations.create_a_role_definition -->

```python
from azure.keyvault.administration import KeyVaultDataAction, KeyVaultPermission, KeyVaultRoleScope

role_name = "customRole"
scope = KeyVaultRoleScope.GLOBAL
permissions = [KeyVaultPermission(data_actions=[KeyVaultDataAction.CREATE_HSM_KEY])]
role_definition = client.set_role_definition(scope=scope, role_name=role_name, permissions=permissions)
```

<!-- END SNIPPET -->

<!-- SNIPPET:access_control_operations.update_a_role_definition -->

```python
new_permissions = [
    KeyVaultPermission(
        data_actions=[KeyVaultDataAction.READ_HSM_KEY],
        not_data_actions=[KeyVaultDataAction.CREATE_HSM_KEY]
    )
]
unique_definition_name = role_definition.name
updated_definition = client.set_role_definition(
    scope=scope, name=unique_definition_name, role_name=role_name, permissions=new_permissions
)
```

<!-- END SNIPPET -->

`get_role_definition` can be used by a `KeyVaultAccessControlClient` to fetch a role definition with the specified scope
and unique name.

<!-- SNIPPET:access_control_operations.get_a_role_definition -->

```python
fetched_definition = client.get_role_definition(scope=scope, name=unique_definition_name)
```

<!-- END SNIPPET -->

`delete_role_definition` can be used by a `KeyVaultAccessControlClient` to delete a role definition with the specified
scope and unique name.

<!-- SNIPPET:access_control_operations.delete_a_role_definition -->

```python
client.delete_role_definition(scope=scope, name=unique_definition_name)
```

<!-- END SNIPPET -->

### List all role assignments
`list_role_assignments` can be used by a `KeyVaultAccessControlClient` to list all of the current role assignments.

<!-- SNIPPET:access_control_operations.list_role_assignments -->

```python
from azure.keyvault.administration import KeyVaultRoleScope

role_assignments = client.list_role_assignments(KeyVaultRoleScope.GLOBAL)
for assignment in role_assignments:
    print(f"Role assignment name: {assignment.name}")
    print(f"Principal ID associated with this assignment: {assignment.properties.principal_id}")
```

<!-- END SNIPPET -->

### Create, get, and delete a role assignment
Role assignments assign a role to a service principal. This will require a role definition ID and service principal
object ID. You can use an ID from the retrieved [list of role definitions](#list-all-role-definitions) for the former,
and an assignment's `principal_id` from the list retrieved in the [above snippet](#list-all-role-assignments) for the
latter. Provide these values, and a scope, to a `KeyVaultAccessControlClient`'s `create_role_assignment` method.

<!-- SNIPPET:access_control_operations.create_a_role_assignment -->

```python
from azure.keyvault.administration import KeyVaultRoleScope

scope = KeyVaultRoleScope.GLOBAL
role_assignment = client.create_role_assignment(scope=scope, definition_id=definition_id, principal_id=principal_id)
print(f"Role assignment {role_assignment.name} created successfully.")
```

<!-- END SNIPPET -->

`get_role_assignment` can be used by a `KeyVaultAccessControlClient` to fetch an existing role assignment with the
specified scope and unique name.

<!-- SNIPPET:access_control_operations.get_a_role_assignment -->

```python
fetched_assignment = client.get_role_assignment(scope=scope, name=role_assignment.name)
print(f"Role assignment for principal {fetched_assignment.properties.principal_id} fetched successfully.")
```

<!-- END SNIPPET -->

`delete_role_assignment` can be used by a `KeyVaultAccessControlClient` to delete a role assignment with the specified
scope and unique name.

<!-- SNIPPET:access_control_operations.delete_a_role_assignment -->

```python
client.delete_role_assignment(scope=scope, name=role_assignment.name)
```

<!-- END SNIPPET -->

### Perform a full key backup
The `KeyVaultBackupClient` can be used to back up your entire collection of keys. The backing store for full key
backups is a blob storage container using Shared Access Signature (SAS) authentication.

For more details on creating a SAS token using a `BlobServiceClient` from [`azure-storage-blob`][storage_blob], refer
to the library's [credential documentation][sas_docs]. Alternatively, it is possible to
[generate a SAS token in Storage Explorer][storage_explorer].

<!-- SNIPPET:backup_restore_operations.begin_backup -->

```python
CONTAINER_URL = os.environ["CONTAINER_URL"]
SAS_TOKEN = os.environ["SAS_TOKEN"]

backup_result = client.begin_backup(CONTAINER_URL, SAS_TOKEN).result()
print(f"Azure Storage Blob URL of the backup: {backup_result.folder_url}")
```

<!-- END SNIPPET -->

Note that the `begin_backup` method returns a poller. Calling `result()` on this poller returns a
`KeyVaultBackupResult` containing information about the backup. Calling `wait()` on the poller will instead block until
the operation is complete without returning an object.

### Perform a full key restore
The `KeyVaultBackupClient` can be used to restore your entire collection of keys from a backup. The data source for a
full key restore is a storage blob accessed using Shared Access Signature authentication. You will also need the URL of
the backup (`KeyVaultBackupResult.folder_url`) from the [above snippet](#perform-a-full-key-backup).

For more details on creating a SAS token using a `BlobServiceClient` from [`azure-storage-blob`][storage_blob], refer
to the library's [credential documentation][sas_docs]. Alternatively, it is possible to
[generate a SAS token in Storage Explorer][storage_explorer].

<!-- SNIPPET:backup_restore_operations.begin_backup -->

```python
client.begin_restore(backup_result.folder_url, SAS_TOKEN).wait()
```

<!-- END SNIPPET -->

Note that the `begin_restore` method returns a poller. Unlike the poller returned by `begin_backup`, this poller's
`result` method returns `None`; therefore, calling `wait()` is functionally the same.

### Perform a selective key restore

To restore a single key from a backed up vault instead of all keys, provide the key name as a `key_name` argument to the
`begin_restore` method [shown above](#perform-a-full-key-restore).

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
| [settings_operations.py][settings_operations_sample] | list and update Key Vault settings |
| [settings_operations_async.py][settings_operations_async_sample] | list and update Key Vault settings with an async client |

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

[sas_docs]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-blob/README.md#types-of-credentials
[settings_operations_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-administration/samples/settings_operations.py
[settings_operations_async_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-administration/samples/settings_operations_async.py
[storage_blob]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/storage/azure-storage-blob/README.md
[storage_explorer]: https://learn.microsoft.com/azure/vs-azure-tools-storage-manage-with-storage-explorer


![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Fkeyvault%2Fazure-keyvault-administration%2FREADME.png)
