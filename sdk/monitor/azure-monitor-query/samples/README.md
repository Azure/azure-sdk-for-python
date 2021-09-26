---
page_type: sample
languages:
  - python
products:
    - azure
    - azure-monitor
urlFragment: query-azuremonitor-samples
---

# Azure Monitor Query Client Library Python Samples

## Samples
These code samples show common champion scenario operations with the Azure Monitor Query client library.

* Send a single query with LogsQueryClient and handle the response as a table: [sample_logs_single_query.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_logs_single_query.py) ([async_sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/async_samples/sample_log_query_client_async.py))

* Send a single query with LogsQueryClient and handle the response in key value form: [sample_logs_query_key_value_form.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_logs_query_key_value_form.py)

* Send a single query with LogsQueryClient without pandas: [sample_single_log_query_without_pandas.py.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_single_log_query_without_pandas.py)

* Send a single query with LogsQueryClient across multiple workspaces: [sample_logs_query_multiple_workspaces.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_logs_query_multiple_workspaces.py)

* Send multiple queries with LogsQueryClient: [sample_batch_query.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_batch_query.py)

* Send a single query with LogsQueryClient using server timeout: [sample_server_timeout.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_server_timeout.py)

* Send a query using MetricsQueryClient: [sample_metrics_query.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_metrics_query.py) ([async_sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/async_samples/sample_metrics_query_client_async.py))

* Get a list of metric namespaces: [sample_metric_namespaces.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_metric_namespaces.py) ([async_sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/async_samples/sample_metric_namespaces_async.py))

* Get a list of metric definitions: [sample_metric_definitions.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/sample_metric_definitions.py) ([async_sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/samples/async_samples/sample_metric_definitions_async.py))

## Prerequisites

- Python 2.7, or 3.6 or later
- An [Azure subscription][azure_subscription]
- To query Logs, you need an [Azure Log Analytics workspace][azure_monitor_create_using_portal].
- To query Metrics, you need an Azure resource of any kind (Storage Account, Key Vault, Cosmos DB, etc.).

## Setup

1. Install the latest beta version of Azure monitor query that the samples use:

```bash
pip install azure-monitor-query
```

2. Clone or download this sample repository.
3. Open the sample folder in Visual Studio Code or your IDE of choice.
4. To run most of this samples, you need azure-identity and pandas although they are optional can be replaced.

```bash
pip install azure-identity pandas
```

5. Finally, to run the async samples, you would need an async http framework like aiohttp

```bash
pip install aiohttp
```

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python sample_logs_single_query.py`

## Next steps

To learn more about Azure Monitor, see the [Azure Monitor service documentation](https://docs.microsoft.com/azure/azure-monitor/).