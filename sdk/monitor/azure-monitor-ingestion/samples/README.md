---
page_type: sample
languages:
  - python
products:
    - azure
    - azure-monitor
urlFragment: ingestion-azuremonitor-samples
---

# Azure Monitor Ingestion client library Python samples

This library allows you to send data from virtually any source to supported built-in tables or to custom tables that you create in Log Analytics workspaces. The following code samples show common scenarios with the Azure Monitor Ingestion client library.

|**File Name**|**Description**|
|-------------|---------------|
|[sample_authentication.py][sample_authentication] and [sample_authentication_async.py][sample_authentication_async]|Authenticate a client with the public cloud and a sovereign cloud.|
|[sample_send_small_logs.py][sample_send_small_logs] and [sample_send_small_logs_async.py][sample_send_small_logs_async]|Send a small number of logs to a Log Analytics workspace.|
|[sample_custom_error_callback.py][sample_custom_error_callback] and [sample_custom_error_callback_async.py][sample_custom_error_callback_async]|Use error callbacks to customize how errors are handled during upload. |
|[sample_upload_file_contents.py][sample_upload_file_contents] and [sample_upload_file_contents_async.py][sample_upload_file_contents_async]|Upload the contents of a file to a Log Analytics workspace.|
|[sample_upload_pandas_dataframe.py][sample_upload_pandas_dataframe] and [sample_upload_pandas_dataframe_async.py][sample_upload_pandas_dataframe_async]|Upload data in a pandas DataFrame to a Log Analytics workspace.|

## Prerequisites

- Python 3.7 or later
- An [Azure subscription][azure_subscription]
- An [Azure Log Analytics workspace][azure_monitor_create_using_portal]
- A [Data Collection Endpoint (DCE)][data_collection_endpoint]
- A [Data Collection Rule (DCR)][data_collection_rule]

## How to run the samples

### Install the dependencies

To run the samples, you need to install the following dependencies:
```bash
pip install azure-monitor-ingestion azure-identity pandas
```

To run the async samples, you need an asynchronous HTTP framework like `aiohttp`:

```bash
pip install aiohttp
```

### Set up authentication

We use [azure-identity][azure_identity]'s [DefaultAzureCredential][azure_identity_default_azure_credential] to authenticate. Ensure that your service principal or managed identity has the `Monitoring Metrics Publisher` role assigned on the Data Collection Rule resource. If you are using a service principal, set the following environment variables:

```bash
AZURE_TENANT_ID="your Azure AD tenant (directory) ID"
AZURE_CLIENT_ID="your Azure AD client (application) ID"
AZURE_CLIENT_SECRET="your Azure AD client secret"
```

### Set up additional environment variables

Change and set the following environment variables to match your configuration:

```bash
DATA_COLLECTION_ENDPOINT="your data collection endpoint"
LOGS_DCR_RULE_ID="your data collection rule immutable ID"
LOGS_DCR_STREAM_NAME="your data collection rule stream name"
```

### Run the samples

Navigate to the directory that the samples are saved in, and follow the usage described in the file. For example, `python sample_send_small_logs.py`.

## Next steps

To learn more about Azure Monitor, see the [Azure Monitor service documentation][azure_monitor_docs] and the [Logs Ingestion API overview][azure_monitor_logs_ingestion_overview].


<!-- Sample links -->
[sample_authentication]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-ingestion/samples/sample_authentication.py
[sample_authentication_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-ingestion/samples/async_samples/sample_authentication_async.py
[sample_send_small_logs]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-ingestion/samples/sample_send_small_logs.py
[sample_send_small_logs_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-ingestion/samples/async_samples/sample_send_small_logs_async.py
[sample_custom_error_callback]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-ingestion/samples/sample_custom_error_callback.py
[sample_custom_error_callback_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-ingestion/samples/async_samples/sample_custom_error_callback_async.py
[sample_upload_file_contents]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-ingestion/samples/sample_upload_file_contents.py
[sample_upload_file_contents_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-ingestion/samples/async_samples/sample_upload_file_contents_async.py
[sample_upload_pandas_dataframe]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-ingestion/samples/sample_upload_pandas_dataframe.py
[sample_upload_pandas_dataframe_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-ingestion/samples/async_samples/sample_upload_pandas_dataframe_async.py

<!-- External links -->
[azure_identity]: https://pypi.org/project/azure-identity/
[azure_identity_default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[azure_monitor_create_using_portal]: https://learn.microsoft.com/azure/azure-monitor/logs/quick-create-workspace
[azure_monitor_docs]: https://learn.microsoft.com/azure/azure-monitor/
[azure_monitor_logs_ingestion_overview]: https://learn.microsoft.com/azure/azure-monitor/logs/logs-ingestion-api-overview
[azure_subscription]: https://azure.microsoft.com/free/
[data_collection_endpoint]: https://learn.microsoft.com/azure/azure-monitor/essentials/data-collection-endpoint-overview
[data_collection_rule]: https://learn.microsoft.com/azure/azure-monitor/essentials/data-collection-rule-overview
