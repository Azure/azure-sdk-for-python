# Azure Monitor Ingestion client library for Python

The Azure Monitor Ingestion client library is used to send custom logs to [Azure Monitor][azure_monitor_overview] using the [Logs Ingestion API][ingestion_overview].

This library allows you to send data from virtually any source to supported built-in tables or to custom tables that you create in Log Analytics workspace. You can even extend the schema of built-in tables with custom columns.

**Resources:**

- [Source code][source]
- [Package (PyPI)][package]
- [Package (Conda)](https://anaconda.org/microsoft/azure-monitor-ingestion/)
- [API reference documentation][python-ingestion-ref-docs]
- [Service documentation][azure_monitor_overview]
- [Samples][samples]
- [Change log][changelog]

## Getting started

### Prerequisites

- Python 3.7 or later
- An [Azure subscription][azure_subscription]
- An [Azure Log Analytics workspace][azure_monitor_create_using_portal]
- A [Data Collection Endpoint][data_collection_endpoint]
- A [Data Collection Rule][data_collection_rule]

### Install the package

Install the Azure Monitor Ingestion client library for Python with [pip][pip]:

```bash
pip install azure-monitor-ingestion
```

### Create the client

An authenticated client is required to upload Logs to Azure Monitor. The library includes both synchronous and asynchronous forms of the clients. To authenticate, create an instance of a token credential. Use that instance when creating a `LogsIngestionClient`. The following examples use `DefaultAzureCredential` from the [azure-identity](https://pypi.org/project/azure-identity/) package.

#### Synchronous clients

Consider the following example, which creates synchronous clients for uploading logs:

```python
import os
from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient

endpoint = os.environ['DATA_COLLECTION_ENDPOINT']
credential = DefaultAzureCredential()
logs_client = LogsIngestionClient(endpoint, credential)
```

#### Asynchronous clients

The asynchronous forms of the client APIs are found in the `.aio`-suffixed namespace. For example:

```python
import os
from azure.identity.aio import DefaultAzureCredential
from azure.monitor.ingestion.aio import LogsIngestionClient

endpoint = os.environ['DATA_COLLECTION_ENDPOINT']
credential = DefaultAzureCredential()
logs_client = LogsIngestionClient(endpoint, credential)
```

#### Configure clients for non-public Azure clouds

By default, `LogsIngestionClient` is configured to connect to the public Azure cloud. To connect to non-public Azure clouds, some additional configuration is required. The appropriate scope for authentication must be provided using the `credential_scopes` keyword argument. The following example shows how to configure the client to connect to Azure US Government:

```python
logs_client = LogsIngestionClient(endpoint, credential_scopes=["https://monitor.azure.us//.default"])
```

## Key concepts

### Data Collection Endpoint

Data Collection Endpoints (DCEs) allow you to uniquely configure ingestion settings for Azure Monitor. [This article][data_collection_endpoint] provides an overview of data collection endpoints including their contents and structure and how you can create and work with them.

### Data Collection Rule

Data collection rules (DCR) define data collected by Azure Monitor and specify how and where that data should be sent or stored. The REST API call must specify a DCR to use. A single DCE can support multiple DCRs, so you can specify a different DCR for different sources and target tables.

The DCR must understand the structure of the input data and the structure of the target table. If the two don't match, it can use a transformation to convert the source data to match the target table. You may also use the transform to filter source data and perform any other calculations or conversions.

For more information, see [Data collection rules in Azure Monitor][data_collection_rule], and see [this article][data_collection_rule_structure] for details about a DCR's structure. For information on how to retrieve a DCR ID, see [this tutorial][data_collection_rule_tutorial].

### Log Analytics workspace tables

Custom logs can send data to any custom table that you create and to certain built-in tables in your Log Analytics workspace. The target table must exist before you can send data to it. The following built-in tables are currently supported:

- [CommonSecurityLog](https://learn.microsoft.com/azure/azure-monitor/reference/tables/commonsecuritylog)
- [SecurityEvents](https://learn.microsoft.com/azure/azure-monitor/reference/tables/securityevent)
- [Syslog](https://learn.microsoft.com/azure/azure-monitor/reference/tables/syslog)
- [WindowsEvents](https://learn.microsoft.com/azure/azure-monitor/reference/tables/windowsevent)

### Logs retrieval

The logs that were uploaded using this library can be queried using the [Azure Monitor Query][azure_monitor_query] client library.

## Examples

- [Upload custom logs](#upload-custom-logs)
- [Upload with custom error handling](#upload-with-custom-error-handling)

### Upload custom logs

This example shows uploading logs to Azure Monitor.

```python
import os

from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient

endpoint = os.environ['DATA_COLLECTION_ENDPOINT']
credential = DefaultAzureCredential()

client = LogsIngestionClient(endpoint=endpoint, credential=credential, logging_enable=True)

rule_id = os.environ['LOGS_DCR_RULE_ID']
body = [
      {
        "Time": "2021-12-08T23:51:14.1104269Z",
        "Computer": "Computer1",
        "AdditionalContext": "context-2"
      },
      {
        "Time": "2021-12-08T23:51:14.1104269Z",
        "Computer": "Computer2",
        "AdditionalContext": "context"
      }
    ]

try:
    client.upload(rule_id=rule_id, stream_name=os.environ['LOGS_DCR_STREAM_NAME'], logs=body)
except HttpResponseError as e:
    print(f"Upload failed: {e}")
```

### Upload with custom error handling

To upload logs with custom error handling, you can pass a callback function to the `on_error` parameter of the `upload` method. The callback function is called for each error that occurs during the upload and should expect one argument that corresponds to an `LogsUploadError` object. This object contains the error encountered and the list of logs that failed to upload.

```python
# Example 1: Collect all logs that failed to upload.
failed_logs = []
def on_error(error):
    print("Log chunk failed to upload with error: ", error.error)
    failed_logs.extend(error.failed_logs)

# Example 2: Ignore all errors.
def on_error_pass(error):
    pass

client.upload(rule_id=rule_id, stream_name=os.environ['LOGS_DCR_STREAM_NAME'], logs=body, on_error=on_error)
```

## Troubleshooting

For details on diagnosing various failure scenarios, see our [troubleshooting guide](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-ingestion/TROUBLESHOOTING.md).

## Next steps

To learn more about Azure Monitor, see the [Azure Monitor service documentation][azure_monitor_overview].

### Samples

The following code samples show common scenarios with the Azure Monitor Ingestion client library.

#### Logs Ingestion samples

- [Upload a list of logs][sample_send_small_logs] ([async sample][sample_send_small_logs_async])
- [Upload a list of logs with custom error handling][sample_custom_error_callback] ([async sample][sample_custom_error_callback_async])
- [Upload the contents of a file][sample_upload_file_contents] ([async sample][sample_upload_file_contents_async])
- [Upload data in a pandas DataFrame][sample_upload_pandas_dataframe] ([async sample][sample_upload_pandas_dataframe_async])

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repositories using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information, see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[azure_core_exceptions]: https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions
[azure_core_ref_docs]: https://aka.ms/azsdk/python/core/docs
[azure_monitor_create_using_portal]: https://learn.microsoft.com/azure/azure-monitor/logs/quick-create-workspace
[azure_monitor_overview]: https://learn.microsoft.com/azure/azure-monitor/
[azure_monitor_query]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-query#readme
[azure_subscription]: https://azure.microsoft.com/free/python/
[changelog]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-ingestion/CHANGELOG.md
[data_collection_endpoint]: https://learn.microsoft.com/azure/azure-monitor/essentials/data-collection-endpoint-overview
[data_collection_rule]: https://learn.microsoft.com/azure/azure-monitor/essentials/data-collection-rule-overview
[data_collection_rule_structure]: https://learn.microsoft.com/azure/azure-monitor/essentials/data-collection-rule-structure
[data_collection_rule_tutorial]: https://learn.microsoft.com/azure/azure-monitor/logs/tutorial-logs-ingestion-portal#collect-information-from-the-dcr
[ingestion_overview]: https://learn.microsoft.com/azure/azure-monitor/logs/logs-ingestion-api-overview
[package]: https://aka.ms/azsdk-python-monitor-ingestion-pypi
[pip]: https://pypi.org/project/pip/
[python_logging]: https://docs.python.org/3/library/logging.html
[python-ingestion-ref-docs]: https://aka.ms/azsdk/python/monitor-ingestion/docs
[samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-ingestion/samples
[source]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-ingestion/

[sample_send_small_logs]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-ingestion/samples/sample_send_small_logs.py
[sample_send_small_logs_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-ingestion/samples/async_samples/sample_send_small_logs_async.py
[sample_custom_error_callback]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-ingestion/samples/sample_custom_error_callback.py
[sample_custom_error_callback_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-ingestion/samples/async_samples/sample_custom_error_callback_async.py
[sample_upload_file_contents]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-ingestion/samples/sample_upload_file_contents.py
[sample_upload_file_contents_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-ingestion/samples/async_samples/sample_upload_file_contents_async.py
[sample_upload_pandas_dataframe]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-ingestion/samples/sample_upload_pandas_dataframe.py
[sample_upload_pandas_dataframe_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-ingestion/samples/async_samples/sample_upload_pandas_dataframe_async.py

[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
