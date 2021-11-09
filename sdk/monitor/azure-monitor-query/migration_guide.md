# Guide for migrating from azure-loganalytics 0.1.0 to azure-monitor-query 1.0.x
This guide is intended to assist in the migration to `azure-monitor-query` 1.0.x from `azure-loganalytics` v0.1.0.
It will focus on side-by-side comparisons for similar operations between the two packages.

Familiarity with the `azure-loganalytics` v0.1.0 package is assumed.
For those new to the Monitor Query client library for Python, please refer to the [README for `azure-monitor-query`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/README.md) rather than this guide.

## Table of contents

* [Migration benefits](#migration-benefits)
    - [Cross Service SDK improvements](#cross-service-sdk-improvements)
    - [New Features](#new-features)
* [Important changes](#important-changes)
    - [The Client](#the-client)
    - [Client constructors and Authentication](#client-constructors-and-authentication)
    - [Sending a Single Query Request](#sending-a-single-query-request)
* [Additional samples](#additional-samples)

## Migration benefits

A natural question to ask when considering whether or not to adopt a new version or library is what
the benefits of doing so would be. As Azure has matured and been embraced by a more diverse group of developers,
we have been focused on learning the patterns and practices to best support developer productivity and
to understand the gaps that the Python client libraries have.

There were several areas of consistent feedback expressed across the Azure client library ecosystem.
One of the most important is that the client libraries for different Azure services have not had a
consistent approach to organization, naming, and API structure. Additionally, many developers have felt
that the learning curve was difficult, and the APIs did not offer a good, approachable,
and consistent onboarding story for those learning Azure or exploring a specific Azure service.

To try and improve the development experience across Azure services,
a set of uniform [design guidelines](https://azure.github.io/azure-sdk/general_introduction.html) was created
for all languages to drive a consistent experience with established API patterns for all services.
A set of [Python-specific guidelines](https://azure.github.io/azure-sdk/python/guidelines/index.html) was also introduced to ensure
that Python clients have a natural and idiomatic feel with respect to the Python ecosystem.
Further details are available in the guidelines for those interested.

### Cross Service SDK improvements

The modern Azure Monitor Query client library also provides the ability to share in some of the cross-service improvements made to the Azure development experience, such as
- using the new [`azure-identity`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md) library
to share a single authentication approach between clients
- a unified logging and diagnostics pipeline offering a common view of the activities across each of the client libraries

### New Features

We have a variety of new features in the version 1.0 of the Monitor Query library.

- Ability to query a batch of queries with the `LogsQueryClient.query_batch()` API.
- Ability to configure the retry policy used by the operations on the client.
- Authentication with AAD credentials using [`azure-identity`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md).
- Refer to the [CHANGELOG.md](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-query/CHANGELOG.md) for more new features, changes and bug fixes.

## Important changes

### The Client

In the interest of providing a more intuitive experience, we've renamed the top level client to query logs to `LogsQueryClient` from `LogAnalyticsDataClient` which can be authenticated using Azure Active Directory(AAD). This client is the single entry point to both query a single query or a batch query.

#### Consistency
We now have methods with similar names, signature and location to create senders and receivers.
This provides consistency and predictability on the various features of the library.

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

### Sending a Single Query Request

- In the latest version, `QueryBody` is flattenned. Users are expected to pass the query directly to the API.
- `timespan` is now a required attribute. This helped to avoid querying over the entire data.

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

More examples can be found at [Samples for azure-monitor-query](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-query/samples)
