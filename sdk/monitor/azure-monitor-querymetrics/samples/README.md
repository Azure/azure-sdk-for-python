---
page_type: sample
languages:
  - python
products:
    - azure
    - azure-monitor
urlFragment: querymetrics-azuremonitor-samples
---

# Azure Monitor Query Metrics client library Python samples

## Samples

The following code samples show common scenarios with the Azure Monitor Query Metrics client library.

For examples on authenticating with the Azure Monitor service, see [sample_authentication.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-querymetrics/samples/sample_authentication.py) and [sample_authentication_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-querymetrics/samples/sample_authentication_async.py).

### Metrics query samples

- [Send a query to resources using MetricsClient](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-querymetrics/samples/sample_metrics_query.py) ([async sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-querymetrics/samples/sample_metrics_query_async.py))

## Prerequisites

- Python 3.9 or later
- An [Azure subscription][azure_subscription]
- Authorization to read metrics data at the Azure subscription level. For example, the [Monitoring Reader role](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles/monitor#monitoring-reader) on the subscription containing the resources to be queried.
- Azure resource of any kind (Storage Account, Key Vault, Cosmos DB, etc.).

## Setup

1. Install the latest version of the Azure Monitor Query Metrics library:

  ```bash
  pip install azure-monitor-querymetrics
  ```

2. Clone or download this sample repository.
3. Open the *samples* folder in Visual Studio Code or your IDE of choice.
4. To run the samples, you need `azure-identity`.

  ```bash
  pip install azure-identity
  ```

5. To run the async samples, you need an asynchronous HTTP framework like `aiohttp`:

  ```bash
  pip install aiohttp
  ```

## Run the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file. For example, `python sample_metrics_query.py`.

## Next steps

To learn more about Azure Monitor, see the [Azure Monitor service documentation](https://learn.microsoft.com/azure/azure-monitor/).

<!-- LINKS -->

[azure_subscription]: https://azure.microsoft.com/free/python/
