# Guide for migrating from azure-applicationinsights v0.1.0 to azure-monitor-query v1.0.x

This guide assists you in the migration from [azure-applicationinsights](https://pypi.org/project/azure-applicationinsights/) v0.1.0 to [azure-monitor-query](https://pypi.org/project/azure-monitor-query/) v1.0.x. Side-by-side comparisons are provided for similar operations between the two packages.

Familiarity with the `azure-applicationinsights` v0.1.0 package is assumed. If you're new to the Azure Monitor Query client library for Python, see the [README for `azure-monitor-query`](https://docs.microsoft.com/python/api/overview/azure/monitor-query-readme?view=azure-python) instead of this guide.

## Table of contents

- [Migration benefits](#migration-benefits)
  - [Cross-service SDK improvements](#cross-service-sdk-improvements)
  - [New features](#new-features)
- [Important changes](#important-changes)
  - [The client](#the-client)
  - [Client constructors and authentication](#client-constructors-and-authentication)
  - [Send a single query request](#sending-a-single-query-request)
- [Additional samples](#additional-samples)

## Migration benefits

A natural question to ask when considering whether to adopt a new version or library is what the benefits of doing so would be. As Azure has matured and been embraced by a more diverse group of developers, we've focused on learning the patterns and practices to best support developer productivity and to understand the gaps that the Python client libraries have.

Several areas of consistent feedback were expressed across the Azure client library ecosystem. One of the most important is that the client libraries for different Azure services haven't had a consistent approach to organization, naming, and API structure. Additionally, many developers have felt that the learning curve was too steep. The APIs didn't offer an approachable and consistent onboarding story for those learning Azure or exploring a specific Azure service.

To improve the development experience across Azure services, a set of uniform [design guidelines](https://azure.github.io/azure-sdk/general_introduction.html) was created for all languages to drive a consistent experience with established API patterns for all services. A set of [Python-specific guidelines](https://azure.github.io/azure-sdk/python/guidelines/index.html) was also introduced to ensure that Python clients have a natural and idiomatic feel with respect to the Python ecosystem. Further details are available in the guidelines.

### Cross-service SDK improvements

The Azure Monitor Query client library also takes advantage of the cross-service improvements made to the Azure development experience. Examples include:

- Using the new [Azure Identity](https://docs.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python) library to share a single authentication approach between clients.
- A unified logging and diagnostics pipeline offering a common view of the activities across each of the client libraries.

### New features

There are various new features in version 1.0 of the Monitor Query library. Some include:

- The ability to execute a batch of queries with the `LogsQueryClient.query_batch()` API.
- The ability to configure the retry policy used by the operations on the client.
- Authentication with Azure Active Directory (Azure AD) credentials using [azure-identity](https://docs.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python).

For more new features, changes, and bug fixes, see the [change log](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/CHANGELOG.md).

## Important changes

### The client

To provide a more intuitive experience, the top-level client to [ApplicationInsightsDataClient](https://docs.microsoft.com/python/api/azure-applicationinsights/azure.applicationinsights.applicationinsightsdataclient?view=azure-python) has been split into two different clients:

- [LogsQueryClient](https://docs.microsoft.com/python/api/azure-monitor-query/azure.monitor.query.logsqueryclient?view=azure-python) serves as a single point of entry to execute a single Kusto query or a batch of Kusto queries.
- [MetricsQueryClient](https://docs.microsoft.com/python/api/azure-monitor-query/azure.monitor.query.metricsqueryclient?view=azure-python) is used to query metrics, list metric namespaces, and to list metric definitions.

Both clients can be authenticated using Azure AD.

#### Consistency

There are now methods with similar names, signatures, and locations to create senders and receivers. The result is consistency and predictability on the various features of the library.

### Client constructors and authentication

In `azure-applicationinsights` v0.1.0:

```python
from azure.applicationinsights import ApplicationInsightsDataClient
from msrestazure.azure_active_directory import ServicePrincipalCredentials

credential = ServicePrincipalCredentials(...)
client = ApplicationInsightsDataClient(credentials=credential)
```

In `azure-monitor-query` v1.0.x:

```python
from azure.monitor.query import LogsQueryClient, MetricsQueryClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
logs_query_client = LogsQueryClient(credential=credential)
metrics_query_client = MetricsQueryClient(credential=credential)
```

### Send a single query request

In version 1.0 of the Monitor Query library:

- The `QueryBody` is flattened. Users are expected to pass the Kusto query directly to the API.
- The `timespan` attribute is now required, which helped to avoid querying over the entire data set.

In `azure-applicationinsights` v0.1.0:

```python
from azure.applicationinsights.models import QueryBody

query = 'requests | take 10'
application = 'DEMO_APP'
result = self.client.query.execute(application, QueryBody(query = query))
```

In `azure-monitor-query` v1.0.x:

```python
query = 'AppRequests | take 5'
logs_query_client.query(workspace_id, query, timespan=timedelta(days=1))
```

### A note about the Events API

The `azure-applicationinsights` package includes an Events API, which is just a different "API head" on the same logs data. It enables the querying of some logs in Application Insights without writing Kusto queries. The API translates to Kusto queries in the background. The same data can be accessed via regular Kusto queries, as shown in the preceding example.

### Query metrics from a resource

In `azure-applicationinsights` v0.1.0:

```python
metricId = 'availabilityResults/count'
application = 'DEMO_APP'
result = client.metrics.get(application, metricId)
```

In `azure-monitor-query` v1.0.x:

```python
metrics_resource_uri = os.environ.get('METRICS_RESOURCE_URI')
result = metrics_query_client.query_resource(
    metrics_resource_uri,
    metric_names=["Ingress"],
    timespan=timedelta(hours=2),
    granularity=timedelta(minutes=5),
    aggregations=[MetricAggregationType.AVERAGE],
    )
```

## Additional samples

For more examples, see [Samples for azure-monitor-query](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-query/samples).
