---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-app-configuration
---

# Azure App Configuration Data Library Python Samples

## Prerequisites

You must have an [Azure subscription][azure_sub], and a [Configuration Store][configuration_store] to use this package.

To create a Configuration Store, you can either use [Azure Portal](https://ms.portal.azure.com/#create/Microsoft.Azconfig) or if you are using [Azure CLI][azure_cli] you can simply run the following snippet in your console:

```Powershell
az appconfig create --name <config-store-name> --resource-group <resource-group-name> --location eastus
```

## Setup

Install the Azure App Configuration client library for Python with pip:

```commandline
pip install azure-appconfiguration
```

## Contents

| File | Description |
|-------------|-------------|
| hello_world_sample.py / hello_world_async_sample.py       | demos set/get/delete operations |
| hello_world_advanced_sample.py / hello_world_advanced_async_sample.py | demos add/set with label/list operations |
| conditional_operation_sample.py / conditional_operation_async_sample.py | demos conditional set/get/delete operations |
| read_only_sample.py / read_only_async_sample.py | demos set_read_only/clear_read_only operations |
| list_revision_sample.py / list_revision_async_sample.py | demos list revision operations |

<!-- LINKS -->
[azure_sub]: https://azure.microsoft.com/free/
[azure_cli]: https://docs.microsoft.com/cli/azure
[configuration_store]: https://azure.microsoft.com/en-us/services/app-configuration/
