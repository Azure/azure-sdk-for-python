# Guide for migrating from azure-loganalytics v0.1.0 to azure-monitor-query v1.0.x

This guide assists you in the migration from [azure-loganalytics](https://pypi.org/project/azure-loganalytics/) v0.1.0 to [azure-monitor-query](https://pypi.org/project/azure-monitor-query/) v1.0.x. Side-by-side comparisons are provided for similar operations between the two packages.

Familiarity with the `azure-loganalytics` v0.1.0 package is assumed. If you're new to the Azure Monitor Query client library for Python, see the [README for `azure-monitor-query`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/README.md) instead of this guide.

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

- Using the new [`azure-identity`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md) library to share a single authentication approach between clients.
- A unified logging and diagnostics pipeline offering a common view of the activities across each of the client libraries.

### New features

There are a variety of new features in version 1.0 of the Monitor Query library. Some include:

- The ability to execute a batch of queries with the `LogsQueryClient.query_batch()` API.
- The ability to configure the retry policy used by the operations on the client.
- Authentication with Azure Active Directory (Azure AD) credentials using [`azure-identity`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md).

For more new features, changes, and bug fixes, see the [change log](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/CHANGELOG.md).

## Important changes

### The client

To provide a more intuitive experience, the top-level client to query logs was renamed to `LogsQueryClient` from `LogAnalyticsDataClient`. `LogsQueryClient` can be authenticated using Azure AD. This client is the single entry point to execute a single query or a batch of queries.

#### Consistency

There are now methods with similar names, signatures, and locations to create senders and receivers. The result is consistency and predictability on the various features of the library.

### Client constructors and authentication

In `azure-loganalytics` v0.1.0:

```python
from azure.loganalytics import LogAnalyticsDataClient
from msrestazure.azure_active_directory import ServicePrincipalCredentials

credential = ServicePrincipalCredentials(...)
client = LogAnalyticsDataClient(credentials=credential)
```

In `azure-monitor-query` v1.0.x:

```python
from azure.monitor.query import LogsQueryClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = LogsQueryClient(credential=credential)
```

### Send a single query request

In version 1.0 of the Monitor Query library:

- The `QueryBody` is flattened. Users are expected to pass the Kusto query directly to the API.
- The `timespan` attribute is now required, which helped to avoid querying over the entire data set.

In `azure-loganalytics` v0.1.0:

```python
from azure.loganalytics.models import QueryBody

query = 'AppRequests | take 5'
response = client.query(workspace_id, QueryBody(**{'query': query}))
```

In `azure-monitor-query` v1.0.x:

```python
query = 'AppRequests | take 5'
client.query(workspace_id, query, timespan=timedelta(days=1))
```

## Additional samples

For more examples, see [Samples for azure-monitor-query](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-query/samples).
