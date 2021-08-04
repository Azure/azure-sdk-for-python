---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-key-vault
urlFragment: keyvault-administration-samples
---

# Azure Key Vault Administration Client Library Python Samples

## Prerequisites

You must have an [Azure subscription](https://azure.microsoft.com/free) and an
[Azure Managed HSM](https://docs.microsoft.com/azure/key-vault/managed-hsm/) to run
these samples. You can create a managed HSM with the
[Azure CLI](https://docs.microsoft.com/azure/key-vault/managed-hsm/quick-create-cli).

## Setup

To run these samples, first install the Key Vault Administration and Azure Identity libraries:

```commandline
pip install azure-keyvault-administration azure-identity
```

[Azure Identity](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md) is used for authenticating Key Vault clients. These samples use the
[DefaultAzureCredential](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md#defaultazurecredential), but any credential from the library can be used with Key Vault clients.

## Contents
| File | Description |
|-------------|-------------|
| [access_control_operations.py][access_control_operations_sample] | create/update/delete role definitions and role assignments |
| [access_control_operations_async.py][access_control_operations_async_sample] | create/update/delete role definitions and role assignments with an async client |
| [backup_restore_operations.py][backup_operations_sample] | full backup and restore |
| [backup_restore_operations_async.py][backup_operations_async_sample] | full backup and restore with an async client |

[access_control_operations_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-administration/samples/access_control_operations.py
[access_control_operations_async_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-administration/samples/access_control_operations_async.py
[backup_operations_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-administration/samples/backup_restore_operations.py
[backup_operations_async_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-administration/samples/backup_restore_operations_async.py
