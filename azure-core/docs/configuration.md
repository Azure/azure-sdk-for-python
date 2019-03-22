# Service Client Configuration


### Configuring retries

The retry policy in the pipeline can be configured directly, or tweaked on a per-call basis.
```python
config = FooService.create_config()
# Total number of retries to allow. Takes precedence over other counts.
# Default value is 10.
config.retry.total_retries = 5
# How many connection-related errors to retry on.
# These are errors raised before the request is sent to the remote server,
# which we assume has not triggered the server to process the request. Default value is 3
config.retry.connect_retries = 2
# How many times to retry on read errors.
# These errors are raised after the request was sent to the server, so the
# request may have side-effects. Default value is 3.
config.retry.read_retries = 4
# How many times to retry on bad status codes. Default value is 3.
config.retry.status_retries = 3
# A backoff factor to apply between attempts after the second try
# (most errors are resolved immediately by a second try without a delay).
# Retry policy will sleep for:
#    {backoff factor} * (2 ** ({number of total retries} - 1))
# seconds. If the backoff_factor is 0.1, then the retry will sleep
# for [0.0s, 0.2s, 0.4s, ...] between retries.
# The default value is 0.8.
config.retry.backoff_factor = 0.5
# The maximum back off time. Default value is 120 seconds (2 minutes).
config.retry.backoff_max

# Alternatively you can disable redirects entirely
from azure.core.pipeline.policies import RetryPolicy
config.retry = RetryPolicy.no_retries()
```

All of these settings can also be configured per operation.
```python
result = client.get_operation(
    retry_total=10,
    retry_connect=1,
    retry_read=1,
    retry_status=5,
    retry_backoff_factory=0.5,
    retry_backoff_max=60,
    retry_on_methods=['GET']
)
```

### Configuring redirects

The redirect policy in the pipeline can be configured directly or per operation.
```python
config = FooService.create_config()

# The maximum allowed redirects. The default value is 30
config.redirect.redirects = 10

# It can also be overridden per operation.
result = client.get_operation(redirect_max=5)

# Alternatively you can disable redirects entirely
from azure.core.pipeline.policies import RedirectPolicy
config.redirect = RedirectPolicy.no_redirects()
```

### Configuring logging

The logging policy in the pipeline is used to output HTTP network trace to the
configured logger.

```python
import sys
import logging

# Create a logger for the 'azure' SDK
logger = logging.getLogger("azure")
logger.set_level(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

# Configure a file output
file_handler = logging.FileHandler(filename)
logger.addHandler(file_handler)

# Enable network trace logging. This will be logged at DEBUG level.
# By default, logging is disabled.
config = FooService.create_config()
config.logging.enable_http_logger = True
```
The logger can also be enabled per operation.
```python
result = client.get_operation(enable_http_logging=True)
```

### Configuring headers

Headers can be configured up front, where any custom headers will be applied to all outgoing operations, and additional headers can also be added dynamically per operation.
```python
config = FooService.create_config()
config.headers.headers = {'CustomValue': 'Foo'}

# Or headers can be added per operation. These headers will supplement existing headers
# or those defined in the config headers policy. They will also overwrite existing
# identical headers.
result = client.get_operation(headers={'CustomValue': 'Bar'})
```

### Configuring user-agent

Custom values can be added to the User-Agent header via the pipeline configuration.
```python
config = FooService.create_config()
# The user-agent policy allows you to append a custom value to the header.
config.user_agent.add_user_agent("CustomValue")

# You can also pass in a custom value per operation to append to the end of the user-agent.
# This can be used together with the policy configuration to append multiple values.
result = client.get_operation(user_agent="AnotherValue")
```
