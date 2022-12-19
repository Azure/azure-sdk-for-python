---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-key-vault
urlFragment: keyvault-certificates-samples
---

# Azure Key Vault Certificates Client Library Python Samples

## Prerequisites

You must have an [Azure subscription](https://azure.microsoft.com/free) and an
[Azure Key Vault](https://docs.microsoft.com/azure/key-vault/general/overview) to run
these samples. You can create a key vault with the
[Azure CLI](https://docs.microsoft.com/azure/key-vault/general/quick-create-cli).

## Setup

To run these samples, first install the Key Vault Certificates and Azure Identity libraries:

```commandline
pip install azure-keyvault-certificates azure-identity
```

[Azure Identity](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md) is used for authenticating Key Vault clients. These samples use the
[DefaultAzureCredential](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md#defaultazurecredential), but any credential from the library can be used with Key Vault clients.

## Contents

| File | Description |
|-------------|-------------|
| [hello_world.py][hello_world_sample] ([async version][hello_world_async_sample]) | create/get/update/delete certificates |
| [backup_restore_operations.py][backup_operations_sample] ([async version][backup_operations_async_sample]) | back up and recover certificates |
| [import_certificate.py][import_certificate_sample] ([async version][import_certificate_async_sample]) | import PKCS#12 (PFX) and PEM-formatted certificates into Key Vault |
| [list_operations.py][list_operations_sample] ([async version][list_operations_async_sample]) | list certificates |
| [recover_purge_operations.py][recover_purge_operations_sample] ([async version][recover_purge_operations_async_sample]) | recover and purge certificates |
| [issuers.py][issuers_sample] ([async version][issuers_async_sample]) | manage certificate issuers |
| [contacts.py][contacts_sample] ([async version][contacts_async_sample]) | manage certificate contacts |
| [parse_certificate.py][parse_sample] ([async version][parse_async_sample]) | extract a certificate's private key |

[backup_operations_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-certificates/samples/backup_restore_operations.py
[backup_operations_async_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-certificates/samples/backup_restore_operations_async.py
[hello_world_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/samples/hello_world.py
[hello_world_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/samples/hello_world_async.py
[import_certificate_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-certificates/samples/import_certificate.py
[import_certificate_async_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-certificates/samples/import_certificate_async.py
[keyvault_docs]: https://docs.microsoft.com/azure/key-vault/
[list_operations_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/samples/list_operations.py
[list_operations_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/samples/list_operations_async.py
[recover_purge_operations_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/samples/recover_purge_operations.py
[recover_purge_operations_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/samples/recover_purge_operations_async.py
[contacts_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/samples/contacts.py
[contacts_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/samples/contacts_async.py
[issuers_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/samples/issuers.py
[issuers_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/samples/issuers_async.py
[parse_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/samples/parse_certificate.py
[parse_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/samples/parse_certificate_async.py
