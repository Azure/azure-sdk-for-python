---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-key-vault
urlFragment: keyvault-securitydomain-samples
---

# Azure Key Vault Security Domain Client Library Python Samples

## Prerequisites

You must have an [Azure subscription](https://azure.microsoft.com/free) and a [Key Vault Managed HSM][managed_hsm] to run these samples. You can create a managed HSM with the [Azure CLI][managed_hsm_cli].

## Setup

To run these samples, first install the Key Vault Security Domain and Azure Identity libraries:

```commandline
python -m pip install azure-keyvault-securitydomain azure-identity
```

[Azure Identity](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md) is used for authenticating Key Vault clients. These samples use the
[DefaultAzureCredential](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md#defaultazurecredential), but any credential from the library can be used with Key Vault clients.

## Contents

| File | Description |
|-------------|-------------|
| [hello_world.py][hello_world_sample] ([async version][hello_world_async_sample]) | download a security domain |

<!-- LINKS -->

[hello_world_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-securitydomain/samples/hello_world.py
[hello_world_async_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-securitydomain/samples/hello_world_async.py

[managed_hsm]: https://learn.microsoft.com/azure/key-vault/managed-hsm/overview
[managed_hsm_cli]: https://learn.microsoft.com/azure/key-vault/managed-hsm/quick-create-cli
