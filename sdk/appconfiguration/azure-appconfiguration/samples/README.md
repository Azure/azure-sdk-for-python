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

* Python 3.8 or later is required to use this package.
* You must have an [Azure subscription][azure_sub], and a [Configuration Store][configuration_store] to use this package.

To create a Configuration Store, you can either use [Azure Portal](https://ms.portal.azure.com/#create/Microsoft.Azconfig) or if you are using [Azure CLI][azure_cli] you can simply run the following snippet in your console:

```Powershell
az appconfig create --name <config-store-name> --resource-group <resource-group-name> --location eastus
```

## Setup

Install the Azure App Configuration client library for Python with pip:

```
pip install azure-appconfiguration
```

## Contents

| File | Description |
|-------------|-------------|
| [hello_world_sample.py][hello_world_sample] / [hello_world_sample_async.py][hello_world_sample_async] | demos how to add/update/retrieve/delete configuration settings |
| [conditional_operation_sample.py][conditional_operation_sample] / [conditional_operation_sample_async.py][conditional_operation_sample_async] | demos how to conditional set/get/delete configuration settings |
| [read_only_sample.py][read_only_sample] / [read_only_sample_async.py][read_only_sample_async] | demos how to set and clear read-only for configuration settings |
| [list_configuration_settings_sample.py][list_configuration_settings_sample] / [list_configuration_settings_sample_async.py][list_configuration_settings_sample_async] | demos how to list configuration settings with optional filters |
| [list_labels_sample.py][list_labels_sample] / [list_labels_sample_async.py][list_labels_sample_async] | demos how to list labels |
| [list_revision_sample.py][list_revision_sample] / [list_revision_sample_async.py][list_revision_sample_async] | demos how to get configuration setting revision history |
| [sync_token_sample.py][sync_token_sample] / [sync_token_sample_async.py][sync_token_sample_async] | demos how to update sync_token for an AzureAppConfigurationClient |
| [snapshot_sample.py][snapshot_sample] / [snapshot_sample_async.py][snapshot_sample_async] | demos how to create/retrieve/archive/recover/list configuration settings snapshot and list configuration settings of a snapshot |
| [send_request_sample.py][send_request_sample] / [send_request_sample_async.py][send_request_sample_async] | demos how to make custom HTTP requests through a client pipeline |


<!-- LINKS -->
[azure_sub]: https://azure.microsoft.com/free/
[azure_cli]: https://learn.microsoft.com/cli/azure
[configuration_store]: https://azure.microsoft.com/services/app-configuration/
[hello_world_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/hello_world_sample.py
[hello_world_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/hello_world_sample_async.py
[conditional_operation_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/conditional_operation_sample.py
[conditional_operation_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/conditional_operation_sample_async.py
[read_only_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/read_only_sample.py
[read_only_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/read_only_sample_async.py
[list_configuration_settings_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/list_configuration_settings_sample.py
[list_configuration_settings_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/list_configuration_settings_sample_async.py
[list_labels_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/list_labels_sample.py
[list_labels_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/list_labels_sample_async.py
[list_revision_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/list_revision_sample.py
[list_revision_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/list_revision_sample_async.py
[sync_token_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/sync_token_sample.py
[sync_token_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/sync_token_sample_async.py
[snapshot_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/snapshot_sample.py
[snapshot_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/snapshot_sample_async.py
[send_request_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/send_request_sample.py
[send_request_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/send_request_sample_async.py
