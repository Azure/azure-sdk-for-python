
# Azure Core shared client library for Python

Azure core provides shared exceptions and modules for Python SDK client libraries.
These libraries follow the [Azure SDK Design Guidelines for Python](https://azure.github.io/azure-sdk/python/guidelines/index.html) .

If you are a client library developer, please reference [client library developer reference](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md) for more information.

[Source code](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/) | [Package (Pypi)][package] | [API reference documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/)

## Getting started

Typically, you will not need to install azure core;
it will be installed when you install one of the client libraries using it.
In case you want to install it explicitly (to implement your own client library, for example),
you can find it [here](https://pypi.org/project/azure-core/).

## Key concepts

### Azure Core Library Exceptions

#### AzureError
AzureError is the base exception for all errors.
```python
class AzureError(Exception):
    def __init__(self, message, *args, **kwargs):
        self.inner_exception = kwargs.get('error')
        self.exc_type, self.exc_value, self.exc_traceback = sys.exc_info()
        self.exc_type = self.exc_type.__name__ if self.exc_type else type(self.inner_exception)
        self.exc_msg = "{}, {}: {}".format(message, self.exc_type, self.exc_value)  # type: ignore
        self.message = str(message)
        super(AzureError, self).__init__(self.message, *args)
```

*message* is any message (str) to be associated with the exception.

*args* are any additional args to be included with exception.

*kwargs* are keyword arguments to include with the exception. Use the keyword *error* to pass in an internal exception.

**The following exceptions inherit from AzureError:**

#### ServiceRequestError
An error occurred while attempt to make a request to the service. No request was sent.

#### ServiceResponseError
The request was sent, but the client failed to understand the response.
The connection may have timed out. These errors can be retried for idempotent or safe operations.

#### HttpResponseError
A request was made, and a non-success status code was received from the service.
```python
class HttpResponseError(AzureError):
    def __init__(self, message=None, response=None, **kwargs):
        self.reason = None
        self.response = response
        if response:
            self.reason = response.reason
        message = "Operation returned an invalid status code '{}'".format(self.reason)
        try:
            try:
                if self.error.error.code or self.error.error.message:
                    message = "({}) {}".format(
                        self.error.error.code,
                        self.error.error.message)
            except AttributeError:
                if self.error.message: #pylint: disable=no-member
                    message = self.error.message #pylint: disable=no-member
        except AttributeError:
            pass
        super(HttpResponseError, self).__init__(message=message, **kwargs)
```
*message* is the HTTP response error message (optional)

*response* is the HTTP response (optional).

*kwargs* are keyword arguments to include with the exception.

**The following exceptions inherit from HttpResponseError:**

#### DecodeError
An error raised during response deserialization.

#### ResourceExistsError
An error response with status code 4xx. This will not be raised directly by the Azure core pipeline.

#### ResourceNotFoundError
An error response, typically triggered by a 412 response (for update) or 404 (for get/post).

#### ClientAuthenticationError
An error response with status code 4xx. This will not be raised directly by the Azure core pipeline.

#### ResourceModifiedError
An error response with status code 4xx, typically 412 Conflict. This will not be raised directly by the Azure core pipeline.

#### ResourceNotModifiedError
An error response with status code 304. This will not be raised directly by the Azure core pipeline.

#### TooManyRedirectsError
An error raised when the maximum number of redirect attempts is reached. The maximum amount of redirects can be configured in the RedirectPolicy.
```python
class TooManyRedirectsError(HttpResponseError):
    def __init__(self, history, *args, **kwargs):
        self.history = history
        message = "Reached maximum redirect attempts."
        super(TooManyRedirectsError, self).__init__(message, *args, **kwargs)
```

*history* is used to document the requests/responses that resulted in redirected requests.

*args* are any additional args to be included with exception.

*kwargs* are keyword arguments to include with the exception.

### Configurations

When calling the methods, some properties can be configured by passing in as kwargs arguments.

| Parameters | Description |
| --- | --- |
| headers | The HTTP Request headers. |
| request_id | The request id to be added into header. |
| user_agent | If specified, this will be added in front of the user agent string. |
| logging_enable| Use to enable per operation. Defaults to `False`. |
| logger | If specified, it will be used to log information. |
| response_encoding | The encoding to use if known for this service (will disable auto-detection). |
| proxies | Maps protocol or protocol and hostname to the URL of the proxy. |
| raw_request_hook | Callback function. Will be invoked on request. |
| raw_response_hook | Callback function. Will be invoked on response. |
| network_span_namer | A callable to customize the span name. |
| tracing_attributes | Attributes to set on all created spans. |
| permit_redirects | Whether the client allows redirects. Defaults to `True`. |
| redirect_max | The maximum allowed redirects. Defaults to `30`. |
| retry_total | Total number of retries to allow. Takes precedence over other counts. Default value is `10`. |
| retry_connect | How many connection-related errors to retry on. These are errors raised before the request is sent to the remote server, which we assume has not triggered the server to process the request. Default value is `3`. |
| retry_read | How many times to retry on read errors. These errors are raised after the request was sent to the server, so the request may have side-effects. Default value is `3`. |
| retry_status | How many times to retry on bad status codes. Default value is `3`. |
| retry_backoff_factor | A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a second try without a delay). Retry policy will sleep for: `{backoff factor} * (2 ** ({number of total retries} - 1))` seconds. If the backoff_factor is 0.1, then the retry will sleep for [0.0s, 0.2s, 0.4s, ...] between retries. The default value is `0.8`. |
| retry_backoff_max | The maximum back off time. Default value is `120` seconds (2 minutes). |
| retry_mode | Fixed or exponential delay between attemps, default is `Exponential`. |
| timeout | Timeout setting for the operation in seconds, default is `604800`s (7 days). |
| connection_timeout | A single float in seconds for the connection timeout. Defaults to `300` seconds. |
| read_timeout | A single float in seconds for the read timeout. Defaults to `300` seconds. |
| connection_verify | SSL certificate verification. Enabled by default. Set to False to disable, alternatively can be set to the path to a CA_BUNDLE file or directory with certificates of trusted CAs. |
| connection_cert | Client-side certificates. You can specify a local cert to use as client side certificate, as a single file (containing the private key and the certificate) or as a tuple of both files' paths. |
| proxies | Dictionary mapping protocol or protocol and hostname to the URL of the proxy. |
| cookies | Dict or CookieJar object to send with the `Request`. |
| connection_data_block_size | The block size of data sent over the connection. Defaults to `4096` bytes. |

### Async transport

The async transport is designed to be opt-in. [AioHttp](https://pypi.org/project/aiohttp/) is one of the supported implementations of async transport. It is not installed by default. You need to install it separately.

### Shared modules

#### MatchConditions

MatchConditions is an enum to describe match conditions.
```python
class MatchConditions(Enum):
    Unconditionally = 1
    IfNotModified = 2
    IfModified = 3
    IfPresent = 4
    IfMissing = 5
```

#### CaseInsensitiveEnumMeta

A metaclass to support case-insensitive enums.
```python
from enum import Enum
from six import with_metaclass

from azure.core import CaseInsensitiveEnumMeta

class MyCustomEnum(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    FOO = 'foo'
    BAR = 'bar'
```

#### Null Sentinel Value

A falsy sentinel object which is supposed to be used to specify attributes
with no data. This gets serialized to `null` on the wire.

```python
from azure.core.serialization import NULL

assert bool(NULL) is False

foo = Foo(
    attr=NULL
)
```

## Contributing
This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit [https://cla.microsoft.com](https://cla.microsoft.com).

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information, see the
[Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/)
or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any
additional questions or comments.

<!-- LINKS -->
[package]: https://pypi.org/project/azure-core/
