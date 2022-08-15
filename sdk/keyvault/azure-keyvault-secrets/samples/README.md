---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-key-vault
urlFragment: keyvault-secrets-samples
---

# Azure Key Vault Secrets Client Library Python Samples

## Prerequisites

You must have an [Azure subscription](https://azure.microsoft.com/free) and an
[Azure Key Vault](https://docs.microsoft.com/azure/key-vault/general/overview) to run
these samples. You can create a key vault with the
[Azure CLI](https://docs.microsoft.com/azure/key-vault/general/quick-create-cli).

## Setup

To run these samples, first install the Key Vault Secrets and Azure Identity libraries:

```commandline
pip install azure-keyvault-secrets azure-identity
```

[Azure Identity](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md) is used for authenticating Key Vault clients. These samples use the
[DefaultAzureCredential](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md#defaultazurecredential), but any credential from the library can be used with Key Vault clients.

## Contents

| File | Description |
|-------------|-------------|
| [hello_world.py][hello_world_sample] ([async version][hello_world_async_sample]) | create/get/update/delete secrets |
| [list_operations.py][list_operations_sample] ([async version][list_operations_async_sample]) | basic list operations for secrets |
| [backup_restore_operations.py][backup_operations_sample] ([async version][backup_operations_async_sample]) | back up and restore secrets |
| [recover_purge_operations.py][recover_purge_sample] ([async version][recover_purge_async_sample]) | recover and purge secrets |

[hello_world_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-secrets/samples/hello_world.py
[hello_world_async_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-secrets/samples/hello_world_async.py
[backup_operations_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-secrets/samples/backup_restore_operations.py
[backup_operations_async_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-secrets/samples/backup_restore_operations_async.py
[list_operations_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-secrets/samples/list_operations.py
[list_operations_async_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-secrets/samples/list_operations_async.py
[recover_purge_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-secrets/samples/recover_purge_operations.py
[recover_purge_async_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-secrets/samples/recover_purge_operations_async.py
