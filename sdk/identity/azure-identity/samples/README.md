---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-sdks
urlFragment: identity-samples
---

# Azure Identity Library Python Samples

## Prerequisites

You must have an [Azure subscription](https://azure.microsoft.com/free) and an
[Azure Key Vault](https://azure.microsoft.com/services/key-vault/) to run
these samples. You can create a Key Vault in the
[Azure Portal](https://portal.azure.com/#create/Microsoft.KeyVault) or with the
[Azure CLI](https://docs.microsoft.com/azure/key-vault/secrets/quick-create-cli).

Azure Key Vault is used only to demonstrate authentication. Azure Identity has
the same API for all compatible client libraries.

## Setup

To run these samples, first install the Azure Identity and Key Vault Certificates
and Secrets client libraries:

```commandline
pip install azure-identity azure-keyvault-certificates azure-keyvault-secrets
```

## Contents
| File | Description |
|-------------|-------------|
| control_interactive_prompts.py | demonstrates controlling when interactive credentials prompt for user interaction |
| custom_credentials.py | demonstrates custom credential implementations using existing access tokens and an MSAL client |
| key_vault_cert.py | demonstrates authenticating with a Key Vault certificate |
| user_authentication.py | demonstrates user authentication and token cache persistence API for applications |
| credential_creation_code_snippets.py | demonstrates how to instantiate various credentials |
