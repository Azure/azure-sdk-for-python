## Cosmos DB Python SDK – Timeout configurations and Retry configurations

### Timeout config

The timeout options for the client can be changed from the default configurations with the options below. 
These options can be passed in at the client constructor or on a per-request basis. These are:
- `Client Timeout`: can be changed by passing the `timeout` option. Changes the value of the per-request client timeout. If not present,
the 'Connection Timeout' connectivity timeouts below will be used. `timeout` must be smaller than your `connection_timeout` to be used.
- `Connection Timeout`: can be changed through `connection_timeout` option. Changes the value on the client's http transport timeout when
connecting to the socket, as well as the per-request client timeout. Default value is 60s. If you'd like to split the two timeouts,
you will need to also use 'Client Timeout'.
- `Read Timeout`: can be changed through `read_timeout` option. Changes the value on the client's http transport timeout when
reading the service buffer stream, or receiving responses from the server. Default value is 300s.


### Resource Throttle Retry Policy config

The options for the resource throttle retry policy used for 429 error codes can be changed from the default client configurations with the options below. These are:
- `Retry Total`: Represents the total amount of retries. Can be changed by passing the `retry_total` option. Default value is 9.
- `Retry Fixed Interval`: Represents a fixed wait period between retry attempts in seconds. Can be changed by passing the
`retry_fixed_interval` option (`float`). The default behaviour is to use an exponential retry policy. Must be a value >= 1.
- `Retry Backoff Max`: Represents the maximum retry wait time. Can be changed by passing the `retry_backoff_max` option. Default value is 30s.


### Connection Retry config

The retry options below can be changed from the default client configurations. These are:
- `Retry Connect`: Maximum number of connection error retry attempts. Can be changed by passing the `retry_connect` option. Default value is 3.
- `Retry Read`: Maximum number of socket read retry attempts. Can be changed by passing the `retry_read` option. Default value is 3.
- `Retry Status`: Maximum number of retry attempts on error status codes. Can be changed by passing the `retry_status` option. Default value is 3.
- `Retry On Status Codes`: A list of specific status codes to retry on. Can be changed by passing the `retry_on_status_codes` option. Default value is an empty list.
- `Retry Backoff Factor`: Factor to calculate wait time between retry attempts. Can be changed by passing the `retry_backoff_factor` option. Default value is 0.8.

More information on the SDK's default retry behaviors can be found in our error codes and retries [document](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos/docs/ErrorCodesAndRetries.md).