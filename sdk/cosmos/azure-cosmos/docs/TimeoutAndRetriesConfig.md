## Cosmos DB Python SDK – Timeout configurations and Retry configurations

### Timeout config

The timeout options for the client can be changed from the default configurations with the options below. 
These options can be passed in at the client constructor or on a per-request basis. These are:
- `Client Timeout`: can be changed by passing the `timeout` option. Changes the value of the per-request client timeout. If not present,
the 'Connection Timeout' connectivity timeouts below will be used. `connection_timeout` must be smaller than your `timeout` to be used.
- `Connection Timeout`: can be changed through `connection_timeout` option. Changes the value on the client's http transport timeout when
connecting to the socket. Default value is 5s. 
- `Read Timeout`: can be changed through `read_timeout` option. Changes the value on the client's http transport timeout when
reading the service buffer stream, or receiving responses from the server. Default value is 65s.

These options can also be combined, as seen in the example below.
This will set the client timeout to 10 seconds, connection timeout to 3 seconds, and read timeout to 60 seconds.
```python
from azure.cosmos import CosmosClient

import os
URL = os.environ['ACCOUNT_URI']
KEY = os.environ['ACCOUNT_KEY']

client = CosmosClient(URL, credential=KEY, timeout=10, connection_timeout=3, read_timeout=60)
```


### Resource Throttle Retry Policy config

The options for the resource throttle retry policy used for 429 error codes can be changed from the default client configurations with the options below. These are:
- `Retry Total`: Represents the total amount of retries. Can be changed by passing the `retry_total` option. Default value is 9.
- `Retry Fixed Interval`: Represents a fixed wait period between retry attempts in seconds. Can be changed by passing the
`retry_fixed_interval` option (`float`). The default behaviour is to use an exponential retry policy. Must be a value >= 1.
- `Retry Backoff Max`: Represents the maximum retry wait time. Can be changed by passing the `retry_backoff_max` option. Default value is 30s.

These options can also be combined, in the example below the total number of retries is 5, the fixed interval is set to 3 seconds, and the maximum retry wait time is 20 seconds.

```python
from azure.cosmos import CosmosClient

import os
URL = os.environ['ACCOUNT_URI']
KEY = os.environ['ACCOUNT_KEY']

client = CosmosClient(URL, credential=KEY, retry_total=5, retry_fixed_interval=3.0, retry_backoff_max=20)
```

### Connection Retry config

The retry options below can be changed from the default client configurations. These are:
- `Retry Connect`: Maximum number of connection error retry attempts. Can be changed by passing the `retry_connect` option. Default value is 3.
- `Retry Read`: Maximum number of socket read retry attempts. Can be changed by passing the `retry_read` option. Default value is 3.
- `Retry Backoff Factor`: Factor to calculate wait time between retry attempts. Can be changed by passing the `retry_backoff_factor` option. Default value is 1.

In the example below, the maximum connection error retry is set to 5 attempts, socket read retry to 4 attempts, and the retry backoff factor is set to 2.
When the retry backoff factor is set to 2 it means the wait time for retries will increase exponentially (1s, 2s, 4s, 8s, 16s...).
```python
from azure.cosmos import CosmosClient

import os
URL = os.environ['ACCOUNT_URI']
KEY = os.environ['ACCOUNT_KEY']

client = CosmosClient(URL, credential=KEY, retry_connect=5, retry_read=4, retry_backoff_factor=2)
```

More information on the SDK's default retry behaviors can be found in our error codes and retries [document](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos/docs/ErrorCodesAndRetries.md).