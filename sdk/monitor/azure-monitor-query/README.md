# Azure Monitor Query client library for Python

Azure Monitor helps you maximize the availability and performance of your applications and services. It delivers a comprehensive solution for collecting, analyzing, and acting on telemetry from your cloud and on-premises environments.

All data collected by Azure Monitor fits into one of two fundamental types, metrics and logs. Metrics are numerical values that describe some aspect of a system at a particular point in time. They are lightweight and capable of supporting near real-time scenarios. Logs contain different kinds of data organized into records with different sets of properties for each type. Telemetry such as events and traces are stored as logs in addition to performance data so that it can all be combined for analysis.

[Source code][python-query-src] | [Package (PyPI)][python-query-pypi] | [API reference documentation][python-query-ref-docs] | [Product documentation][python-query-product-docs] | [Samples][python-query-samples] | [Changelog][python-query-changelog]

## Getting started

### Prerequisites
* Python 2.7, or 3.6 or later is required to use this package.
* You must have an [Azure subscription][azure_subscription].


### Install the package
Install the Azure Monitor Query client library for Python with [pip][pip]:

```bash
pip install azure-monitor-query --pre
```

### Authenticate the client
A **token credential** is necessary to instantiate both the LogsQueryClient and the MetricsQueryClient object.

```Python
from azure.monitor.query import LogsQueryClient
from azure.identity import ClientSecretCredential


credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )

client = LogsQueryClient(credential)
```

```Python
from azure.monitor.query import MetricsQueryClient
from azure.identity import ClientSecretCredential


credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )

client = MetricsQueryClient(credential)
```

## Key concepts

### Logs

Azure Monitor Logs is a feature of Azure Monitor that collects and organizes log and performance data from monitored
resources. Data from different sources such as platform logs from Azure services, log and performance data from virtual
machines agents, and usage and performance data from applications can be consolidated into a single workspace so they
can be analyzed together using a sophisticated query language that's capable of quickly analyzing millions of records.
You may perform a simple query that just retrieves a specific set of records or perform sophisticated data analysis to
identify critical patterns in your monitoring data.

#### Log Analytics workspaces

Data collected by Azure Monitor Logs is stored in one or more Log Analytics workspaces. The workspace defines the
geographic location of the data, access rights defining which users can access data, and configuration settings such as
the pricing tier and data retention.

You must create at least one workspace to use Azure Monitor Logs. A single workspace may be sufficient for all of your
monitoring data, or may choose to create multiple workspaces depending on your requirements. For example, you might have
one workspace for your production data and another for testing.

#### Log queries

Data is retrieved from a Log Analytics workspace using a log query which is a read-only request to process data and
return results. Log queries are written
in [Kusto Query Language (KQL)](https://docs.microsoft.com/azure/data-explorer/kusto/query/), which is the same query
language used by Azure Data Explorer. You can write log queries in Log Analytics to interactively analyze their results,
use them in alert rules to be proactively notified of issues, or include their results in workbooks or dashboards.
Insights include prebuilt queries to support their views and workbooks.

### Metrics

Azure Monitor Metrics is a feature of Azure Monitor that collects numeric data from monitored resources into a time
series database. Metrics are numerical values that are collected at regular intervals and describe some aspect of a
system at a particular time. Metrics in Azure Monitor are lightweight and capable of supporting near real-time scenarios
making them particularly useful for alerting and fast detection of issues. You can analyze them interactively with
metrics explorer, be proactively notified with an alert when a value crosses a threshold, or visualize them in a
workbook or dashboard.

#### Metrics data structure

Data collected by Azure Monitor Metrics is stored in a time-series database which is optimized for analyzing
time-stamped data. Each set of metric values is a time series with the following properties:

- The time the value was collected
- The resource the value is associated with
- A namespace that acts like a category for the metric
- A metric name
- The value itself
- Some metrics may have multiple dimensions as described in Multi-dimensional metrics. Custom metrics can have up to 10
  dimensions.


## Examples

### Get logs for a query

```Python
import os
import pandas as pd
from azure.monitor.query import LogsQueryClient
from azure.identity import ClientSecretCredential


credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )

client = LogsQueryClient(credential)

# Response time trend 
# request duration over the last 12 hours. 
query = """AppRequests | 
where TimeGenerated > ago(12h) | 
summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId"""

# returns LogsQueryResults 
response = client.query(os.environ['LOG_WORKSPACE_ID'], query)

if not response.tables:
    print("No results for the query")

for table in response.tables:
    df = pd.DataFrame(table.rows, columns=[col.name for col in table.columns])
    print(df)
```

### Get Logs for multiple queries

```Python
import os
import pandas as pd
from azure.monitor.query import LogsQueryClient, LogsQueryRequest
from azure.identity import ClientSecretCredential


credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )

client = LogsQueryClient(credential)

requests = [
    LogsQueryRequest(
        query="AzureActivity | summarize count()",
        timespan="PT1H",
        workspace= os.environ['LOG_WORKSPACE_ID']
    ),
    LogsQueryRequest(
        query= """AppRequests | take 10  |
            summarize avgRequestDuration=avg(DurationMs) by bin(TimeGenerated, 10m), _ResourceId""",
        timespan="PT1H",
        workspace= os.environ['LOG_WORKSPACE_ID']
    ),
    LogsQueryRequest(
        query= "AppRequests | take 2",
        workspace= os.environ['LOG_WORKSPACE_ID']
    ),
]
response = client.batch_query(requests)

for response in response.responses:
    body = response.body
    if not body.tables:
        print("Something is wrong")
    else:
        for table in body.tables:
            df = pd.DataFrame(table.rows, columns=[col.name for col in table.columns])
            print(df)
```

### Get logs with server timeout

```Python
import os
import pandas as pd
from azure.monitor.query import LogsQueryClient
from azure.identity import ClientSecretCredential


credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )

client = LogsQueryClient(credential)

response = client.query(
    os.environ['LOG_WORKSPACE_ID'],
    "Perf | summarize count() by bin(TimeGenerated, 4h) | render barchart title='24H Perf events'",
    server_timeout=10,
    )

for table in response.tables:
    df = pd.DataFrame(table.rows, columns=[col.name for col in table.columns])
    print(df)
```

### Get Metrics

```Python
import os
from azure.monitor.query import MetricsQueryClient
from azure.identity import ClientSecretCredential


credential  = ClientSecretCredential(
        client_id = os.environ['AZURE_CLIENT_ID'],
        client_secret = os.environ['AZURE_CLIENT_SECRET'],
        tenant_id = os.environ['AZURE_TENANT_ID']
    )

client = MetricsQueryClient(credential)
response = client.query(os.environ['METRICS_RESOURCE_URI'], metric_names=["Microsoft.CognitiveServices/accounts"])
```

## Troubleshooting

- Enable `azure.monitor.query` logger to collect traces from the library.

### General
Monitor Query client library will raise exceptions defined in [Azure Core][azure_core_exceptions].

### Logging
This library uses the standard
[logging][python_logging] library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

### Optional Configuration

Optional keyword arguments can be passed in at the client and per-operation level.
The azure-core [reference documentation][azure_core_ref_docs]
describes available configurations for retries, logging, transport protocols, and more.

## Next steps

### Additional documentation

For more extensive documentation on Azure Monitor Query, see the [Monitor Query documentation][python-query-product-docs] on docs.microsoft.com.

## Contributing
This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[azure_cli_link]: https://pypi.org/project/azure-cli/
[python-query-src]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/azure-monitor-query/
[python-query-pypi]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/azure-monitor-query/
[python-query-product-docs]: https://docs.microsoft.com/rest/api/monitor/metrics
[python-query-ref-docs]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/monitor/azure-monitor-query/
[python-query-samples]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/monitor/azure-monitor-query/samples
[python-query-changelog]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/monitor/azure-monitor-query/CHANGELOG.md
[pip]: https://pypi.org/project/pip/

[azure_core_exceptions]: https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions
[python_logging]: https://docs.python.org/3/library/logging.html
[azure_core_ref_docs]: https://aka.ms/azsdk/python/core/docs
[azure_subscription]: https://azure.microsoft.com/free/

[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
