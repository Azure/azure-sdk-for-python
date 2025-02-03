---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-app-configuration
---

# Azure App Configuration Provider Library Python Samples

## Prerequisites

You must have an [Azure subscription][azure_sub], and a [Configuration Store][configuration_store] to use this package.

To create a Configuration Store, you can either use [Azure Portal](https://ms.portal.azure.com/#create/Microsoft.Azconfig) or if you are using [Azure CLI][azure_cli] you can simply run the following snippet in your console:

```Powershell
az appconfig create --name <config-store-name> --resource-group <resource-group-name> --location eastus
```

### Create Keys

```Powershell
az appconfig kv set --name <config-store-name> --key message --value "hi"
az appconfig kv set --name <config-store-name> --key test.message --value "Hi with test Prefix"
```

### Create Key Vault Reference

Requires Key Vault with Secret already created.

```Powershell
az appconfig kv set-keyvault --name <config-store-name> --key secret --secret-identifier <key-vault-reference>
```

## Setup

Install the Azure App Configuration Provider client library for Python with pip:

```commandline
pip install azure.appconfiguration.provider
```

## Contents

| File | Description |
|-------------|-------------|
| aad_sample.py | demos connecting to app configuration with Azure Active Directory |
| connection_string_sample.py | demos connecting to app configuration with a Connection String |
| key_vault_reference_sample.py | demos resolving key vault references with App Configuration |

## Next steps

Check out our Django and Flask examples to see how to use the provider in a web application.

### [Django](https://github.com/Azure/AppConfiguration/tree/main/examples/Python/python-django-webapp-sample)

### [Flask](https://github.com/Azure/AppConfiguration/tree/main/examples/Python/python-flask-webapp-sample)

<!-- LINKS -->
[azure_sub]: https://azure.microsoft.com/free/
[azure_cli]: https://learn.microsoft.com/cli/azure
[configuration_store]: https://azure.microsoft.com/services/app-configuration/
