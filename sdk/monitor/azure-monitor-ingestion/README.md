# Azure Monitor Ingestion client library for Python

The Azure Monitor Ingestion client library is used to send custom logs to [Azure Monitor][azure_monitor_overview].

This library allows you to send data from virtually any source to supported built-in tables or to custom tables 
that you create in Log Analytics workspace. You can even extend the schema of built-in tables with custom columns.

**Resources:**

- [Source code][source]
- [Package (PyPI)][package]
- [API reference documentation][python-ingestion-ref-docs]
- [Service documentation][azure_monitor_overview]
- [Samples][samples]
- [Change log][changelog]

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended on 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

## Getting started

### Prerequisites

- Python 3.6 or later
- An [Azure subscription][azure_subscription]
- An [Azure Log Analytics workspace][azure_monitor_create_using_portal].
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

## Key concepts

### Data Collection Endpoint

Data Collection Endpoints (DCEs) allow you to uniquely configure ingestion settings for Azure Monitor. [This 
article][data_collection_endpoint] provides an overview of data collection endpoints including their contents and 
structure and how you can create and work with them.

### Data Collection Rule

Data collection rules (DCR) define data collected by Azure Monitor and specify how and where that data should be sent or
stored. The REST API call must specify a DCR to use. A single DCE can support multiple DCRs, so you can specify a
different DCR for different sources and target tables.

The DCR must understand the structure of the input data and the structure of the target table. If the two don't match,
it can use a transformation to convert the source data to match the target table. You may also use the transform to
filter source data and perform any other calculations or conversions.

For more details, refer to [Data collection rules in Azure Monitor](https://docs.microsoft.com/azure/azure-monitor/essentials/data-collection-rule-overview).

### Log Analytics Workspace Tables

Custom logs can send data to any custom table that you create and to certain built-in tables in your Log Analytics 
workspace. The target table must exist before you can send data to it. The following built-in tables are currently supported:

- [CommonSecurityLog](https://docs.microsoft.com/azure/azure-monitor/reference/tables/commonsecuritylog)
- [SecurityEvents](https://docs.microsoft.com/azure/azure-monitor/reference/tables/securityevent)
- [Syslog](https://docs.microsoft.com/azure/azure-monitor/reference/tables/syslog)
- [WindowsEvents](https://docs.microsoft.com/azure/azure-monitor/reference/tables/windowsevent)

## Examples

- [Upload custom logs](#upload-custom-logs)

### Upload custom logs

This example shows uploading logs to Azure monitor.

```python
import os
from azure.monitor.ingestion import LogsIngestionClient, UploadLogsStatus
from azure.identity import DefaultAzureCredential

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

response = client.upload(rule_id=rule_id, stream_name=os.environ['LOGS_DCR_STREAM_NAME'], logs=body)
if response.status != UploadLogsStatus.SUCCESS:
    failed_logs = response.failed_logs_index
    print(failed_logs)
```

## Troubleshooting

Enable the `azure.monitor.ingestion` logger to collect traces from the library.

### General

Monitor Ingestion client library will raise exceptions defined in [Azure Core][azure_core_exceptions].

### Logging

This library uses the standard [logging][python_logging] library for logging. Basic information about HTTP sessions, such as URLs and headers, is logged at the `INFO` level.

### Optional configuration

Optional keyword arguments can be passed in at the client and per-operation level. The `azure-core` [reference documentation][azure_core_ref_docs] describes available configurations for retries, logging, transport protocols, and more.

## Next steps

To learn more about Azure Monitor, see the [Azure Monitor service documentation][azure_monitor_overview].

### Samples

The following code samples show common scenarios with the Azure Monitor Ingestion client library.

#### Logs Ingestion samples

- [Upload a list of logs](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-ingestion/samples/sample_send_small_logs.py) ([async sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-ingestion/samples/async_samples/sample_send_small_logs_async.py))

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repositories using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[azure_core_exceptions]: https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions
[azure_core_ref_docs]: https://aka.ms/azsdk/python/core/docs
[azure_monitor_overview]: https://docs.microsoft.com/azure/azure-monitor/
[azure_subscription]: https://azure.microsoft.com/free/python/
[changelog]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-ingestion/CHANGELOG.md
[package]: https://aka.ms/azsdk-python-monitor-ingestion-pypi
[pip]: https://pypi.org/project/pip/
[python_logging]: https://docs.python.org/3/library/logging.html
[python-ingestion-ref-docs]: https://aka.ms/azsdk/python/monitor-ingestion/docs
[samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-ingestion/samples
[source]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-ingestion/
[data_collection_endpoint]: https://docs.microsoft.com//azure/azure-monitor/essentials/data-collection-endpoint-overview
[data_collection_rule]: https://docs.microsoft.com/azure/azure-monitor/essentials/data-collection-rule-overview

[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
