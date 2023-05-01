## Cosmos DB Python SDK – Timeout configurations and Retry configurations

### Timeout config

The timeout options for the client can be changed from the default configurations with the options below. These are:
- `Client Timeout`: can be changed by passing the `timeout` option. This option has no default value, and is only present
if it is passed in by the user. If not present, the other connectivity timeouts will be used.
- `Request Timeout`: can be changed by passing the `request_timeout` option. Default value is 60s.
- `Connection Timeout`: can be changed through `connection_timeout` option. Default value is 60s.
- `Read Timeout`: can be changed through `read_timeout` option. Default value is 300s.


### Resource Throttle Retry Policy config

The options for the resource throttle retry policy used for 429 error codes can be changed from the default client configurations with the options below. These are:
- `Retry Total`: can be changed by passing the `retry_total` option. Default value is 9.
- `Retry Fixed Interval`: can be changed by passing the `retry_fixed_interval` option. This option has no default value,
and is only present if it is passed in by the user.
- `Retry Backoff Max`: can be changed by passing the `retry_backoff_max` option. Default value is 30s.


### Connection Retry config

The retry options below can be changed from the default client configurations. These are:
- `Retry Connect`: can be changed by passing the `retry_connect` option. None.
- `Retry Read`: can be changed by passing the `retry_read` option. None.
- `Retry Status`: can be changed by passing the `retry_status` option. None.
- `Retry On Status Codes`: Error codes to be retried on. Can be changed by passing the `retry_on_status_codes` option.
- `Retry Backoff Factor`: can be changed by passing the `retry_backoff_factor` option. Default value is 0.8.

More information on the SDK's default retry behaviors can be found in our error codes and retries [document](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cosmos/azure-cosmos/docs/ErrorCodesAndRetries.md).