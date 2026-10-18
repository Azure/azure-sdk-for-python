## Cosmos DB Python SDK – Timeout configurations and Retry configurations

### Timeout config

`timeout` sets an overall operation budget, including preparation and retries.
Set a client default or a non-`None` override on supported operations; `None`
inherits the client default. A paged operation gets a fresh budget for each
public page fetch, not for each internal service request or the whole enumeration.

For Rust clients, configure transport limits on `ConnectionPoolOptions` and
pass an explicitly created `CosmosRuntime` to the client:
- `connection_timeout`: connection establishment, 0.1–6 seconds.
- `data_http_request_timeout`: one complete data HTTP attempt, at least 0.1 seconds.
- `metadata_http_request_timeout`: one complete metadata HTTP attempt, 0.1–65 seconds.

Without overrides, these limits are 5, 6, and 65 seconds respectively.
All durations are finite seconds; overall budgets must be at least one second
and less than `2**64`. The HTTP-attempt limits do not measure read inactivity.
`read_timeout` and its connection-policy fields are removed on both execution
paths; explicitly supplying them, even as `None`, raises `TypeError`.

This example sets a ten-second overall default, a three-second connection limit,
and separate data/metadata HTTP-attempt limits.
```python
from azure.cosmos import ConnectionPoolOptions, CosmosClient, CosmosRuntime

import os
URL = os.environ['ACCOUNT_URI']
KEY = os.environ['ACCOUNT_KEY']

runtime = CosmosRuntime.create(connection_pool=ConnectionPoolOptions(
    connection_timeout=3,
    data_http_request_timeout=6,
    metadata_http_request_timeout=60,
))
client = CosmosClient(URL, credential=KEY, runtime=runtime, timeout=10)
```


### Resource Throttle Retry Policy config

The options for the resource throttle retry policy used for 429 error codes can be changed from the default client configurations with the options below. These are:
- `Retry Throttle Total`: Represents the total amount of retries. Can be changed by passing the `retry_throttle_total` option. Default value is 9.
- `Retry Fixed Interval`: Represents a fixed wait period between retry attempts in seconds. Can be changed by passing the
`retry_fixed_interval` option (`float`). The default behaviour is to use an exponential retry policy. Must be a value >= 1.
- `Retry Throttle Backoff Max`: Configures the throttle retry waiting allowance through `retry_throttle_backoff_max`. Default value is 30s.

On the Rust-backed path, this allowance governs ordinary throttle retries;
it is not a strict cap on all waiting. The driver can use remaining operation
time for a final retry after the ordinary allowance is exhausted. Configure
`timeout` to bound the overall operation, including retry waiting.

Previously, `retry_total` and `retry_backoff_max` were used to set both the throttle and connection retry policy configurations. 
This option is backwards compatible though, the option remains to set both throttle and connection retry configurations with the same `retry_total` and `retry_backoff_max` value.

In the example below the total number of throttle retries is 5, the fixed interval is set to 3 seconds, and the maximum throttle retry backoff wait time is 15 seconds.
This leaves the connection retry policies set to their default values. 

```python
from azure.cosmos import CosmosClient

import os
URL = os.environ['ACCOUNT_URI']
KEY = os.environ['ACCOUNT_KEY']

client = CosmosClient(URL, credential=KEY, retry_throttle_total=5, retry_fixed_interval=3.0, retry_throttle_backoff_max=15)
```

### Connection Retry config

The retry options below can be changed from the default client configurations. These are:
- `Retry Total`: Represents the total amount of retries. Can be changed by passing the `retry_total` option. Default value is 9.
- `Retry Connect`: Maximum number of connection error retry attempts. Can be changed by passing the `retry_connect` option. Default value is 3.
- `Retry Read`: Maximum number of socket read retry attempts. Can be changed by passing the `retry_read` option. Default value is 3.
- `Retry Backoff Factor`: Factor to calculate wait time between retry attempts. Can be changed by passing the `retry_backoff_factor` option. Default value is 1.
- `Retry Backoff Max`: Represents the maximum retry wait time. Can be changed by passing the `retry_backoff_max` option. Default value is 30s.


In the example below, the maximum total retries is 7 attempts, the connection error retry is 5 attempts, and the socket read retry is 4 attempts.
The retry backoff factor is set to 2. When the retry backoff factor is 2, it means the wait time for retries will increase exponentially (1s, 2s, 4s, 8s, 16s...).
Lastly, the retry backoff max is 20, meaning that the maximum wait time between retries will be 20 seconds. 
```python
from azure.cosmos import CosmosClient

import os
URL = os.environ['ACCOUNT_URI']
KEY = os.environ['ACCOUNT_KEY']

client = CosmosClient(URL, credential=KEY, retry_total = 7, retry_connect=5, retry_read=4, retry_backoff_factor=2, retry_backoff_max=20)
```
Additionally, in the above example the throttle retry total will be 7, and throttle max backoff will be 20 seconds.


To configure throttle and connection retries separately, both sets of parameters would need to be passed in as shown in the example below.
In this example, the connection retry backoff max time is 35 seconds, while setting the throttle backoff max to 25 seconds.
Additionally, the total throttle retry attempts is 5, while the total connection retry attempts is 10.

```python
from azure.cosmos import CosmosClient

import os
URL = os.environ['ACCOUNT_URI']
KEY = os.environ['ACCOUNT_KEY']

client = CosmosClient(URL, credential=KEY,
                        retry_backoff_max=35,
                        retry_throttle_backoff_max=25,
                        retry_throttle_total=5,
                        retry_total=10)
```

More information on the SDK's default retry behaviors can be found in our error codes and retries [document](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos/docs/ErrorCodesAndRetries.md).