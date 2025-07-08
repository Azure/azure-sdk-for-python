---
page_type: sample
languages:
  - python
products:
    - azure
    - azure-monitor
urlFragment: query-logs-azuremonitor-samples
---

# Azure Monitor Query Logs client library Python samples

## Samples

The following code samples show common scenarios with the Azure Monitor Query Logs client library.

For examples on authenticating with the Azure Monitor service, see [sample_authentication.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-querylogs/samples/sample_authentication.py) and [sample_authentication_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-querylogs/samples/async_samples/sample_authentication_async.py).

### Logs query samples

- [Send a single workspace query with LogsQueryClient and handle the response as a table](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-querylogs/samples/sample_logs_single_query.py) ([async sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-querylogs/samples/async_samples/sample_logs_single_query_async.py))
- [Send a single workspace query with LogsQueryClient and handle the response in key-value form](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-querylogs/samples/sample_logs_query_key_value_form.py)
- [Send a single workspace query with LogsQueryClient without pandas](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-querylogs/samples/sample_single_log_query_without_pandas.py)
- [Send a single workspace query with LogsQueryClient across multiple workspaces](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-querylogs/samples/sample_logs_query_multiple_workspaces.py)
- [Send multiple workspace queries with LogsQueryClient](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-querylogs/samples/sample_batch_query.py)
- [Send a single workspace query with LogsQueryClient using server timeout](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-querylogs/samples/sample_server_timeout.py)
- [Send a single resource query with LogsQueryClient](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-querylogs/samples/sample_resource_logs_query.py)
- [Handle partial query results](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-querylogs/samples/sample_logs_single_query_partial_result.py)

#### Notebook samples

- [Split a large query into multiple smaller queries to avoid hitting service limits](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-querylogs/samples/notebooks/sample_large_query.ipynb)
- [Detect anomalies in Azure Monitor log data using machine learning techniques](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-querylogs/samples/notebooks/sample_machine_learning_sklearn.ipynb)

## Prerequisites

- Python 3.9 or later
- An [Azure subscription][azure_subscription]
- To query Logs, you need an [Azure Log Analytics workspace][azure_monitor_create_using_portal].

## Setup

1. Install the Azure Monitor Query Logs client library for Python with [pip][pip]:

```bash
pip install azure-monitor-querylogs
```

2. **Optional**: To use the samples, you may also need to install [pandas][pandas] for easier data manipulation:

```bash
pip install pandas
```

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python sample_logs_single_query.py`

## Next steps

Check out the [API reference documentation][query_ref_docs] to learn more about what you can do with the Azure Monitor Query Logs client library.

[azure_subscription]: https://azure.microsoft.com/free/
[azure_monitor_create_using_portal]: https://learn.microsoft.com/azure/azure-monitor/logs/quick-create-workspace
[pandas]: https://pandas.pydata.org/
[pip]: https://pypi.org/project/pip/
[query_ref_docs]: https://learn.microsoft.com/python/api/azure-monitor-querylogs/azure.monitor.querylogs
