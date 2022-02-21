---
page_type: sample
languages:
  - python
products:
    - azure
    - azure-monitor
urlFragment: query-azuremonitor-samples
---

# Azure Monitor Query client library Python samples

## Samples

The following code samples show common scenarios with the Azure Monitor Query client library.

### Logs query samples

- [Send a single query with LogsQueryClient and handle the response as a table](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_logs_single_query.py) ([async sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/async_samples/sample_log_query_async.py))
- [Send a single query with LogsQueryClient and handle the response in key-value form](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_logs_query_key_value_form.py)
- [Send a single query with LogsQueryClient without pandas](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_single_log_query_without_pandas.py)
- [Send a single query with LogsQueryClient across multiple workspaces](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_log_query_multiple_workspaces.py)
- [Send multiple queries with LogsQueryClient](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_batch_query.py)
- [Send a single query with LogsQueryClient using server timeout](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_server_timeout.py)

### Metrics query samples

- [Send a query using MetricsQueryClient](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_metrics_query.py) ([async sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/async_samples/sample_metrics_query_async.py))
- [Get a list of metric namespaces](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_metric_namespaces.py) ([async sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/async_samples/sample_metric_namespaces_async.py))
- [Get a list of metric definitions](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_metric_definitions.py) ([async sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/async_samples/sample_metric_definitions_async.py))

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended on 01 January 2022. For more information and questions, refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_.

## Prerequisites

- Python  3.6 or later
- An [Azure subscription][azure_subscription]
- To query Logs, you need an [Azure Log Analytics workspace][azure_monitor_create_using_portal].
- To query Metrics, you need an Azure resource of any kind (Storage Account, Key Vault, Cosmos DB, etc.).

## Setup

1. Install the latest version of the Azure Monitor Query library:

  ```bash
  pip install azure-monitor-query
  ```

2. Clone or download this sample repository.
3. Open the *samples* folder in Visual Studio Code or your IDE of choice.
4. To run most of this samples, you need `azure-identity` and `pandas`. Although, those dependencies are optional and can be replaced.

  ```bash
  pip install azure-identity pandas
  ```

5. To run the async samples, you need an asynchronous HTTP framework like `aiohttp`:

  ```bash
  pip install aiohttp
  ```

## Run the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file. For example, `python sample_logs_single_query.py`.

## Next steps

To learn more about Azure Monitor, see the [Azure Monitor service documentation](https://docs.microsoft.com/azure/azure-monitor/).

<!-- LINKS -->

[azure_monitor_create_using_portal]: https://docs.microsoft.com/azure/azure-monitor/logs/quick-create-workspace
[azure_subscription]: https://azure.microsoft.com/free/python/
