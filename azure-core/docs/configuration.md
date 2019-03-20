# Service Client Configuration

## Configuring policies

# TODO - document values and their defaults.
# Show snippets with per-call overrides

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
# How many times to retry on bad status codes.
config.retry.status_retries = 3

```
### Configuring logging
```python
# Show dump to console/file

logger = logging.getLogger("azure")
logger.set_level(logging.DEBUG)

config = FooService.create_config()

# Enable network trace logging. This will be logged at DEBUG level.
config.logging.enable_http_logger = True
```
