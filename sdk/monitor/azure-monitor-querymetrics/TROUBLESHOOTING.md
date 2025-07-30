# Troubleshooting Azure Monitor Query Metrics client library issues

This troubleshooting guide contains instructions to diagnose frequently encountered issues while using the Azure Monitor Query Metrics client library for Python.

## Table of contents

* [General Troubleshooting](#general-troubleshooting)
    * [Enable client logging](#enable-client-logging)
    * [Troubleshooting authentication issues with metrics query requests](#authentication-errors)
    * [Troubleshooting running async APIs](#errors-with-running-async-apis)
* [Troubleshooting Metrics Query](#troubleshooting-metrics-query)
    * [Troubleshooting insufficient access error](#troubleshooting-insufficient-access-error-for-metrics-query)
    * [Troubleshooting unsupported granularity for metrics query](#troubleshooting-unsupported-granularity-for-metrics-query)
* [Additional azure-core configurations](#additional-azure-core-configurations)


## General Troubleshooting

Monitor query raises exceptions described in [`azure-core`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md)

### Enable client logging

To troubleshoot issues with Azure Monitor Query Metrics library, it is important to first enable logging to monitor the behavior of the application. The errors and warnings in the logs generally provide useful insights into what went wrong and sometimes include corrective actions to fix issues.

This library uses the standard [logging](https://docs.python.org/3/library/logging.html) library for logging. Basic information about HTTP sessions, such as URLs and headers, is logged at the INFO level.
Detailed DEBUG level logging, including request/response bodies and unredacted headers, can be enabled on a client with the logging_enable argument:

```python
import logging
from azure.monitor.querymetrics import MetricsClient

# Create a logger for the 'azure.monitor.querymetrics' SDK
logger = logging.getLogger('azure.monitor.querymetrics')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

client = MetricsClient(credential, logging_enable=True)
```

Similarly, logging_enable can enable detailed logging for a single operation, even when it isn't enabled for the client:

```python
client.query_workspace(logging_enable=True)
```

### Authentication errors

Azure Monitor Query Metrics supports Microsoft Entra ID authentication. The MetricsClient has methods to set the `credential`. To provide a valid credential, you can use
`azure-identity` dependency. For more details on getting started, refer to
the [README](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-querymetrics#create-the-client)
of Azure Monitor Query Metrics library. You can also refer to
the [Azure Identity documentation](https://learn.microsoft.com/python/api/overview/azure/identity-readme)
for more details on the various types of credential supported in `azure-identity`.

For more help on troubleshooting authentication errors please see the Azure Identity client library [troubleshooting guide](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/TROUBLESHOOTING.md).

### Errors with running async APIs

The async transport is designed to be opt-in. [AioHttp](https://pypi.org/project/aiohttp/) is one of the supported implementations of async transport. It is not installed by default. You need to install it separately as follows:

```
pip install aiohttp
```

## Troubleshooting Metrics Query

### Troubleshooting insufficient access error for metrics query

If you encounter 401 authorization errors while querying metrics using `MetricsClient`, please ensure you are authorized to read monitoring data at the Azure subscription level. For example, the [Monitoring Reader role](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles/monitor#monitoring-reader) on the subscription to be queried.

### Troubleshooting unsupported granularity for metrics query

If you notice the following exception, this is due to an invalid time granularity in the metrics query request. Your
query might have set the `granularity` keyword argument to an unsupported duration.

```text
"{"code":"BadRequest","message":"Invalid time grain duration: PT10M, supported ones are: 00:01:00,00:05:00,00:15:00,00:30:00,01:00:00,06:00:00,12:00:00,1.00:00:00"}"
```

As documented in the error message, the supported granularity for metrics queries are 1 minute, 5 minutes, 15 minutes,
30 minutes, 1 hour, 6 hours, 12 hours and 1 day.

## Additional azure-core configurations

When calling the methods, some properties including `retry_mode`, `timeout`, `connection_verify` can be configured by passing in as keyword arguments. See
[configurations](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md#configurations) for list of all such properties.
