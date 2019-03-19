

# Azure Core Library

## Pipeline

The Azure Core pipeline is a re-strucuting of the msrest pipeline introduced in msrest 0.6.0.
Further discussions on the msrest implementation can be found in the [msrest wiki](https://github.com/Azure/msrest-for-python/wiki/msrest-0.6.0---Pipeline).

The Azure Core Pipeline is an implementation of chained policies as described in the [Azure SDK guidelines](https://github.com/Azure/azure-sdk/tree/master/docs/design).

The Python implementation of the pipeline has some mechanisms specific to Python. This is due to the fact that both synchronous and asynchronous implementations of the pipeline must be supported indepedently.

When constructing an SDK, a developer may consume the pipeline like so:

```python
from azure.core import Configuration, Pipeline
from azure.core.transport import RequestsTransport, HttpRequest
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    HeadersPolicy,
    RetryPolicy,
    RedirectPolicy,
    ContentDecodePolicy
)

class FooServiceClient():

    @staticmethod
    def create_config(**kwargs):
        # Here the SDK developer would define the default
        # config to interact with the service
        config = Configuration(**kwargs)
        config.user_agent = UserAgentPolicy("ServiceUserAgentValue", **kwargs)
        config.headers = HeadersPolicy({"CustomHeader": "Value"})
        config.retry = RetryPolicy(**kwargs)
        config.redirect = RedirectPolicy(**kwargs)

    def __init__(self, credentials, config=None, transport=None):
        config = config or FooServiceClient.create_config()
        transport = RequestsTransport(config)
        policies = [
            config.user_agent,
            config.headers,
            credentials,
            ContentDecodePolicy(),
            config.redirect,
            config.retry,
            config.logging,
        ]
        self._pipeline = Pipeline(transport, policies=policies)

    def get_request(self, **kwargs)
        # Create a generic HTTP Request. This is not specific to any particular transport
        # or pipeline configuration.
        new_request = HttpRequest("GET", "/")

        response = self._pipeline.run(new_request, **kwargs)
        return deserialize_data(response.http_response)
```

An end user consuming this SDK may write code like so:
```python
from azure.core.credentials import FooCredentials
from azure.foo import FooServiceClient

creds = FooCredentials("api-key")

# Scenario using entirely default configuration
client = FooServiceClient(creds)
response = client.get_request()

# Scenario where user wishes to tweak a couple of settings
foo_config = FooserviceClient.create_config()
foo_config.retry.total_retries = 5
foo_config.logging.enable_http_logger = True

client = FooServiceClient(creds, config=config)
response = client.get_request()

# Scenario where user wishes to tweak settings for only a specific request
client = FooServiceClient(creds)
response = client.get_request(redirects_max=0)

# Scenario where user wishes to substitute custom policy
foo_config = FooserviceClient.create_config()
foo_config.retry = CustomRetryPolicy()

client = FooServiceClient(creds, config=config)
response = client.get_request()
```

### Configuration

The Configuration object is the home of all the configurable policies in the pipeline. It is also used
to provide configuration parameters for the Transport. A new Configuration object provides *no default policies*.
It is up to the SDK developer to specify each of the policy defaults as required by the service.

This can be seen in the above code sample as implemented in a staticmethod on the client class.
The Configuration object does not specify in what order the policies will be added to the pipeline.
It is up to the SDK developer to use the policies in the Configuration to construct the pipeline correctly, as well
as inserting any unexposed/non-configurable policies.
```python
config = config or FooServiceClient.create_config()
transport = RequestsTransport(config)

# SDK developer needs to build the policy order for the pipeline.
policies = [
    config.user_agent,
    config.headers,
    credentials,  # Credentials policy needs to be inserted after all request mutation to accomodate signing.
    ContentDecodePolicy(),
    config.redirect,
    config.retry,
    config.logging,  # Logger should come last to accurately record the request/response as they are on the wire
]
self._pipeline = Pipeline(transport, policies=policies)
```
The policies that should currently be defined on the Configuration object are as follows:
```python
- Configuration.headers  # HeadersPolicy
- Configuration.retry  # RetryPolicy
- Configuration.redirect  # RedirectPolicu
- Configuration.logging  # NetworkTraceLoggingPolicy
- Configuration.user_agent  # UserAgentPolicy
- Configuration.connection  # The is a ConnectionConfiguration, used to provide common transport parameters.
- Configuration.proxy  # While this is a ProxyPolicy object, current implementation is transport configuration.
```

### Transport 

Various combinations of sync/async HTTP libraries as well as alternative event loop implementations are available. Therefore to support the widest range of customer scenarios, we must allow a customer to easily swap out the HTTP transport layer to one of those supported.

The transport is the last node in the pipeline, and adheres to the same basic API as any policy within the pipeline.
The only currently available transport for synchronous pipelines uses the `Requests` library:
```
from azure.core.pipeline.transport import RequestsTransport
synchronous_transport = RequestsTransport()
```

For asynchronous pipelines a couple of transport options are available. Each of these transports are interchangable depending on whether the user has installed various 3rd party dependencies (i.e. aiohttp or trio), and the user
should easily be able to specify their chosen transport. SDK developers should use the `aiohttp` transport as the default for asynchronous pipelines where the user has not specified as alternative.
```
from azure.core.pipeline.transport import (
    # Identical implementation as the synchronous RequestsTrasport wrapped in an asynchronous using the
    # built-in asyncio event loop.
    AsyncioRequestsTransport,

    # Identical implementation as the synchronous RequestsTrasport wrapped in an asynchronous using the
    # third party trio event loop.
    TrioRequestsTransport,

    # Fully asynchronous implementation using the aiohttp library, using the built-in asyncio event loop.
    AioHttpTransport,
)
```

Some common properties can be configured on all transports, and can be set on the TransportConfiguration, found in the Configuration object described above. These include the following properties:
```python
class ConnectionConfiguration(object):

    def __init__(self, **kwargs):
        self.timeout = kwargs.pop('connection_timeout', 100)
        self.verify = kwargs.pop('connection_verify', True)
        self.cert = kwargs.pop('connection_cert', None)
        self.data_block_size = kwargs.pop('connection_data_block_size', 4096)
        self.keep_alive = kwargs.pop('connection_keep_alive', False)
```
Currently we are also using transport configuration for Proxy support - although this may at some point be turned into a dedicated policy.

### HttpRequest and HttpResponse

The HttpRequest and HttpResponse objects represent a generic concept of HTTP request and response constructs and are in no way tied to a particular transport or HTTP library.

The HttpRequest has the following API. It does not vary between transports:
```python
class HttpRequest(object):
    
    def __init__(self, method, url, headers=None, files=None, data=None):
        self.method = method
        self.url = url
        self.headers = CaseInsensitiveDict(headers)
        self.files = files
        self.data = data

    @property
    def body(self):
        return self.data

    @body.setter
    def body(self, value):
        self.data = value

    def format_parameters(self, params):
        """Format parameters into a valid query string.
        It's assumed all parameters have already been quoted as
        valid URL strings."""

    def add_content(self, data):
        """Add a body to the request."""

    def add_formdata(self, content=None):
        """Add data as a multipart form-data request to the request."""
```

The HttpResponse object on the other hand will generally have a transport-specific derivative.
This is to accomodate how the data is extracted for the object returned by the HTTP library.
There is also an async flavor: AsyncHttpResponse. This is to allow for the asynchronous streaming of
data from the response.
For example:
```python
from azure.core.pipeline.transport import (
    RequestsTransportResponse,  # HttpResponse
    AioHttpTransportResponse, # AsyncHttpResponse
    TrioRequestsTransportResponse,  # AsyncHttpResponse
    AsyncioRequestsTransportResponse,  # AsyncHttpResponse
)
```
The API for each of these response types is identical, so the consumer of the Response need not know about these
particular types.

The HttpResponse has the following API. It does not vary between transports:
```python
class HttpResponse(object):

    def __init__(self, request, internal_response):
        self.request = request
        self.internal_response = internal_response  # The object returned be the HTTP library
        self.status_code = None
        self.headers = {}
        self.reason = None 

    def body(self):
        """Return the whole body as bytes in memory."""

    def text(self, encoding=None):
        """Return the whole body as a string."""

    def raise_for_status(self):
        """Raise for status."""

    def stream_download(self, chunk_size=None, callback=None):
        """Generator for streaming request body data.
        Should be implemented by sub-classes if streaming download
        is supported.
        For the AsyncHttpResponse object this function will return
        and asynchronous generator.
        """

```

### PipelineRequest and PipelineResponse

These objects provide containers for moving the HttpRequest and HttpResponse through the pipeline.
While the SDK developer will not construct the PipelineRequest explicitly, they will handle the PipelineResponse
object that is returned from `pipeline.run()`
These objects are universal for all transports, both synchronous and asynchronous.

The pipeline request and response containers are also responsable for carrying a `context` object. This is
transport specific and can contain data persisted between pipeline requests (for example reusing an open connection
or "session"), as well as used by the SDK developer to carry arbitrary data through the pipeline.

The API for PipelineRequest and PipelineResponse is as follows:
```python
class PipelineRequest(object):

    def __init__(self, http_request, context=None):
        self.http_request = http_request  # The HttpRequest
        self.context = context # A transport specific data container object


class PipelineResponse(object):

    def __init__(self, http_request, http_response, context=None):
        self.http_request = http_request  # The HttpRequest
        self.http_response = http_response  # The HttpResponse
        self.history = []  # A list of retry and redirect attempts.
        self.context = context or {}  # A transport specific data container object
```

### Policies

The Python pipeline implementation provides two flavors of policy. These are referred to as an HttpPolicy and a SansIOPolicy.

#### SansIOHTTPPolicy

If a policy just modifies or annotate the request based on the HTTP specification, it's then a subclass of SansIOHTTPPolicy and will work in either Pipeline or AsyncPipeline context.
This is a simple abstract class, that can act before the request is done, or act after. For instance:

- Setting headers in the request
- Logging the request in and the response out

A SansIOHTTPPolicy should implement one or more of the following methods:
```python
def on_request(self, request, **kwargs):
    """Is executed before sending the request to next policy."""

def on_response(self, request, response, **kwargs):
    """Is executed after the request comes back from the policy."""

def on_exception(self, request, **kwargs):
    """Is executed if an exception comes back fron the following
    policy.
    Return True if the exception has been handled and should not
    be forwarded to the caller.
    """
```

Current provided sans IO policies include:
```python
from azure.core.pipeline.policies import (
    HeadersPolicy,  # Add custom headers to all requests
    UserAgentPolicy,  # Add a custom user agent header
    NetworkTraceLoggingPolicy,  # Log request and response contents
    ContentDecodePolicy,  # Mandatory policy for decoding unstreamed response content
)
```

#### HTTPPolicy and AsyncHTTPPolicy

Some policies are more complex, like retry strategy, and need to have control of the HTTP workflow.
In the current version, they are subclasses of HTTPPolicy or AsyncHTTPPolicy, and can be used only their corresponding synchronous or asynchronous pipeline type.

An HTTPPolicy or AsyncHTTPPolicy must implement the `send` method, and this implementation must in include a call to process the next policy in the pipeline:
```python
class CustomPolicy(HTTPPolicy):

    def __init__(self):
        self.next = None  # Will be set when pipeline is instantiated and all the policies chained.

    def send(self, request, **kwargs):
        """Mutate the request."""

        return self.next.send(request, **kwargs)

class CustomAsyncPolicy(AsyncHTTPPolicy):

    async def send(self, request, **kwargs):
        """Mutate the request."""

        return await self.next.send(request, **kwargs)
```

Currently provided HTTP policies include:
```python
from azure.core.pipeline.policies import (
    CredentialsPolicy,
    AsyncCredentialsPolicy,
    RetryPolicy,
    AsyncRetryPolicy.
    RedirectPolicy,
    AsyncRedirectPolicy
)
```
