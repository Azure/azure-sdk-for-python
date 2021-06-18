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

## Sync samples
These code samples show common champion scenario operations with the Azure Monitor Query client library.

* Send a single query with LogsQueryClient: [sample_log_query_client.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/azure-monitor-query/samples/sample_log_query_client.py)

* Send multiple queries with LogsQueryClient: [sample_batch_query.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/azure-monitor-query/samples/sample_batch_query.py)

* Send multiple queries with LogsQueryClient as a dictionary: [sample_batch_query_serialized.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/azure-monitor-query/samples/sample_batch_query_serialized.py)

* Send a single query with LogsQueryClient using server timeout: [sample_server_timeout.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/azure-monitor-query/samples/sample_server_timeout.py)

* Send a query using MetricsQueryClient: [sample_metrics_query_client.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/azure-monitor-query/samples/sample_metrics_query_client.py) 

* Get a list of metric namespaces: [sample_metric_namespaces.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/azure-monitor-query/samples/sample_metric_namespaces.py)

* Get a list of metric definitions: [sample_metric_definitions.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/azure-monitor-query/samples/sample_metric_definitions.py)

## Async samples
These code samples show common champion scenario operations with the Azure Monitor Query client library using the async client.

* Send a single query with LogsQueryClient: [sample_log_query_client_async.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/azure-monitor-query/samples/async_samples/sample_log_query_client_async.py)

* Send a query using MetricsQueryClient: [sample_metrics_query_client_async.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/azure-monitor-query/samples/async_samples/sample_metrics_query_client_async.py) 

* Get a list of metric namespaces: [sample_metric_namespaces_async.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/azure-monitor-query/samples/async_samples/sample_metric_namespaces_async.py)

* Get a list of metric definitions: [sample_metric_definitions_async.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/azure-monitor-query/samples/async_samples/sample_metric_definitions_async.py)