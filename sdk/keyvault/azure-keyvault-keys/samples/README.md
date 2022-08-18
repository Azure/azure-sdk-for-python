---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-key-vault
urlFragment: keyvault-keys-samples
---

# Azure Key Vault Keys Client Library Python Samples

## Prerequisites

You must have an [Azure subscription](https://azure.microsoft.com/free) and an [Azure Key Vault](https://docs.microsoft.com/azure/key-vault/general/overview) to run these samples. You can create a key vault with the [Azure CLI](https://docs.microsoft.com/azure/key-vault/general/quick-create-cli).

You can also run these samples with a [Key Vault Managed HSM][managed_hsm]. If you need to create a Managed HSM, you can do so using the Azure CLI by following the steps in [this document][managed_hsm_cli].

## Setup

To run these samples, first install the Key Vault Keys and Azure Identity libraries:

```commandline
pip install azure-keyvault-keys azure-identity
```

[Azure Identity](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md) is used for authenticating Key Vault clients. These samples use the
[DefaultAzureCredential](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md#defaultazurecredential), but any credential from the library can be used with Key Vault clients.

## Contents

| File | Description |
|-------------|-------------|
| [hello_world.py][hello_world_sample] ([async version][hello_world_async_sample]) | create/get/update/delete keys |
| [list_operations.py][list_operations_sample] ([async version][list_operations_async_sample]) | basic list operations for keys |
| [backup_restore_operations.py][backup_operations_sample] ([async version][backup_operations_async_sample]) | back up and recover keys |
| [recover_purge_operations.py][recover_purge_sample] ([async version][recover_purge_async_sample]) | recover and purge keys |

[hello_world_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys/samples/hello_world.py
[hello_world_async_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys/samples/hello_world_async.py
[backup_operations_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys/samples/backup_restore_operations.py
[backup_operations_async_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys/samples/backup_restore_operations_async.py
[list_operations_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys/samples/list_operations.py
[list_operations_async_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys/samples/list_operations_async.py
[recover_purge_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys/samples/recover_purge_operations.py
[recover_purge_async_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys/samples/recover_purge_operations_async.py
[key_rotation_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys/samples/key_rotation.py
[key_rotation_async_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys/samples/key_rotation_async.py
[managed_hsm]: https://docs.microsoft.com/azure/key-vault/managed-hsm/overview
[managed_hsm_cli]: https://docs.microsoft.com/azure/key-vault/managed-hsm/quick-create-cli