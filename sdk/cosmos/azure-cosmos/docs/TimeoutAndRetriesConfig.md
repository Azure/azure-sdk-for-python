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
- `Retry Fixed Interval`: On legacy Python, `retry_fixed_interval` selects a fixed throttle retry delay in milliseconds instead of the service response's requested delay. Rust-backed clients reject this keyword with `TypeError`, including `None` and zero; omit it.
- `Throttle Retry Wait Threshold Seconds`: Configures the ordinary throttle retry waiting threshold through `throttle_retry_wait_threshold_seconds`. The value is in seconds; the legacy default is 30 seconds.

This replaces `retry_throttle_backoff_max` without changing the value's units
or retry behavior. The old name raises `TypeError` with migration guidance,
including when supplied as `None`. The threshold is not a fixed delay before
each retry or an overall operation timeout.

On the Rust-backed path, this allowance governs ordinary throttle retries;
it is not a strict cap on all waiting. The driver can use remaining operation
time for a final retry after the ordinary allowance is exhausted. Configure
`timeout` to bound the overall operation, including retry waiting.

Rust-backed clients also reject a non-`None`
`connection_policy.RetryOptions.FixedRetryIntervalInMilliseconds`.
Leave that grouped setting at its default `None`. This applies to sync/async
clients and connection-string factories; legacy Python retains fixed-delay
support.

Previously, `retry_total` and `retry_backoff_max` were used to set both the throttle and connection retry policy configurations. 
This option is backwards compatible though, the option remains to set both throttle and connection retry configurations with the same `retry_total` and `retry_backoff_max` value.

Alpha Bank allows up to five throttle retries and sets the ordinary waiting
threshold to 15 seconds. It does not request a fixed delay before each retry.
These throttle-specific options leave the connection retry settings unchanged.

```python
from azure.cosmos import CosmosClient

import os
URL = os.environ['ACCOUNT_URI']
KEY = os.environ['ACCOUNT_KEY']

client = CosmosClient(URL, credential=KEY, retry_throttle_total=5, throttle_retry_wait_threshold_seconds=15)
```

### Connection Retry config

Alpha Bank wants to control retries after a connection failure or an interrupted
response. On legacy Python, the settings below configure the connection-retry
policy. Rust-backed clients currently reject `retry_connect` and `retry_read`
with `TypeError` during construction, even for `None` or zero. This includes
sync/async clients and connection-string factories.

Omit these keywords on Rust; omission keeps the driver's retry behavior,
not a zero-retry guarantee. Rejection is an interim safeguard pending the
retry-control review, rather than a permanent exclusion. The remaining
settings below must not be assumed to configure equivalent Rust connection
retries merely because they are accepted.

Legacy Python settings:
- `Retry Total`: Represents the total amount of retries. Can be changed by passing the `retry_total` option. Default value is 9.
- `Retry Connect`: Maximum number of connection error retry attempts. Can be changed by passing the `retry_connect` option. Default value is 3.
- `Retry Read`: Maximum number of socket read retry attempts. Can be changed by passing the `retry_read` option. Default value is 3.
- `Retry Backoff Factor`: Factor to calculate wait time between retry attempts. Can be changed by passing the `retry_backoff_factor` option. Default value is 1.
- `Retry Backoff Max`: Represents the maximum retry wait time. Can be changed by passing the `retry_backoff_max` option. Default value is 30s.


The following example is for legacy Python; Rust rejects it during construction.
The maximum total retries is 7 attempts, the connection error retry is 5 attempts, and the socket read retry is 4 attempts.
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
                        throttle_retry_wait_threshold_seconds=25,
                        retry_throttle_total=5,
                        retry_total=10)
```

More information on the SDK's default retry behaviors can be found in our error codes and retries [document](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos/docs/ErrorCodesAndRetries.md).