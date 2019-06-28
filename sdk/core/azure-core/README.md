

# Azure Core Library

## Pipeline

The Azure Core pipeline is a re-structuring of the msrest pipeline introduced in msrest 0.6.0.
Further discussions on the msrest implementation can be found in the [msrest wiki](https://github.com/Azure/msrest-for-python/wiki/msrest-0.6.0---Pipeline).

The Azure Core Pipeline is an implementation of chained policies as described in the [Azure SDK guidelines](https://github.com/Azure/azure-sdk/tree/master/docs/design).

The Python implementation of the pipeline has some mechanisms specific to Python. This is due to the fact that both synchronous and asynchronous implementations of the pipeline must be supported independently.

When constructing an SDK, a developer may consume the pipeline like so:

```python
from azure.core import Configuration, Pipeline
from azure.core.transport import RequestsTransport, HttpRequest
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    HeadersPolicy,
    RetryPolicy,
    RedirectPolicy,
    BearerTokenCredentialPolicy,
    ContentDecodePolicy,
    NetworkTraceLoggingPolicy,
    ProxyPolicy
)

class FooServiceClient():

    @staticmethod
    def create_config(credential, scopes, **kwargs):
        # Here the SDK developer would define the default
        # config to interact with the service
        config = Configuration(**kwargs)
        config.headers_policy = HeadersPolicy({"CustomHeader": "Value"}, **kwargs)
        config.user_agent_policy = UserAgentPolicy("ServiceUserAgentValue", **kwargs)
        config.authentication_policy = BearerTokenCredentialPolicy(credential, scopes, **kwargs)
        config.retry_policy = RetryPolicy(**kwargs)
        config.redirect_policy = RedirectPolicy(**kwargs)
        config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
        config.proxy_policy = ProxyPolicy(**kwargs)
        config.transport = kwargs.get('transport', RequestsTransport)

    def __init__(self, transport=None, configuration=None, **kwargs):
        config = configuration or FooServiceClient.create_config(**kwargs)
        transport = config.get_transport(**kwargs)
        policies = [
            config.user_agent_policy,
            config.headers_policy,
            config.authentication_policy,
            ContentDecodePolicy(),
            config.redirect_policy,
            config.retry_policy,
            config.logging_policy,
        ]
        self._pipeline = Pipeline(transport, policies=policies)

    def get_foo_properties(self, **kwargs)
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
endpoint = "http://service.azure.net

# Scenario using entirely default configuration
# We use the SDK-developer defined configuration.
client = FooServiceClient(endpoint, creds)
response = client.get_foo_properties()

# Scenario where user wishes to tweak a couple of settings
# In this case the configurable options can be passed directly into the client constructor.
client = FooServiceClient(endpoint, creds, logging_enable=True, retries_total=5)
response = client.get_foo_properties()

# Scenario where user wishes to tweak settings for only a specific request
# All the options available on construction are available as per-request overrides.
# These can also be specified by the SDK developer - and it will be up to them to resolve
# conflicts with user-defined parameters.
client = FooServiceClient(endpoint, creds)
response = client.get_foo_properties(redirects_max=0)

# Scenario where user wishes to fully customize the policies.
# We expose the SDK-developer defined configuration to allow it to be tweaked
# or entire policies replaced or patched.
foo_config = FooServiceClient.create_config()

foo_config.retry_policy = CustomRetryPolicy()
foo_config.redirect_policy.max_redirects = 5
foo_config.logging_policy.enable_http_logger = True

client = FooServiceClient(endpoint, creds, config=config)
response = client.get_foo_properties()
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
config = config or FooServiceClient.create_config(**kwargs)
transport = RequestsTransport(config)

# SDK developer needs to build the policy order for the pipeline.
policies = [
    config.headers_policy,
    config.user_agent_policy,
    config.authentication_policy,  # Authentication policy needs to be inserted after all request mutation to accommodate signing.
    ContentDecodePolicy(),
    config.redirect_policy,
    config.retry_policy,
    config.logging_policy,  # Logger should come last to accurately record the request/response as they are on the wire
]
self._pipeline = Pipeline(transport, policies=policies)
```
The policies that should currently be defined on the Configuration object are as follows:
```python
- Configuration.headers_policy  # HeadersPolicy
- Configuration.retry_policy  # RetryPolicy
- Configuration.redirect_policy  # RedirectPolicy
- Configuration.logging_policy  # NetworkTraceLoggingPolicy
- Configuration.user_agent_policy  # UserAgentPolicy
- Configuration.connection  # The is a ConnectionConfiguration, used to provide common transport parameters.
- Configuration.proxy_policy  # While this is a ProxyPolicy object, current implementation is transport configuration.
- Configuration.authentication_policy  # BearerTokenCredentialPolicy

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
should easily be able to specify their chosen transport. SDK developers should use the `aiohttp` transport as the default for asynchronous pipelines where the user has not specified an alternative.
```
from azure.foo.aio import FooServiceClient
from azure.core.pipeline.transport import (
    # Identical implementation as the synchronous RequestsTransport wrapped in an asynchronous using the
    # built-in asyncio event loop.
    AsyncioRequestsTransport,

    # Identical implementation as the synchronous RequestsTransport wrapped in an asynchronous using the
    # third party trio event loop.
    TrioRequestsTransport,

    # Fully asynchronous implementation using the aiohttp library, using the built-in asyncio event loop.
    AioHttpTransport,
)

client = FooServiceClient(endpoint, creds, transport=AioHttpTransport)
response = await client.get_foo_properties()
```

Some common properties can be configured on all transports, and can be set on the ConnectionConfiguration, found in the Configuration object described above. These include the following properties:
```python
class ConnectionConfiguration(object):
    """Configuration of HTTP transport.

    :param int connection_timeout: The connect and read timeout value. Defaults to 100 seconds.
    :param bool connection_verify: SSL certificate verification. Enabled by default. Set to False to disable,
     alternatively can be set to the path to a CA_BUNDLE file or directory with certificates of trusted CAs.
    :param str connection_cert: Client-side certificates. You can specify a local cert to use as client side
     certificate, as a single file (containing the private key and the certificate) or as a tuple of both files' paths.
    :param int connection_data_block_size: The block size of data sent over the connection. Defaults to 4096 bytes.
    """

    def __init__(self, **kwargs):
        self.timeout = kwargs.pop('connection_timeout', 100)
        self.verify = kwargs.pop('connection_verify', True)
        self.cert = kwargs.pop('connection_cert', None)
        self.data_block_size = kwargs.pop('connection_data_block_size', 4096)
```

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

    def set_xml_body(self, data):
        """Set an XML element tree as the body of the request."""

    def set_json_body(self, data):
        """Set a JSON-friendly object as the body of the request."""

    def set_multipart_body(self, data=None):
        """Set form-encoded data as the body of the request.
        Supported content-types are:
            - application/x-www-form-urlencoded
            - multipart/form-data
        """

    def set_bytes_body(self, data):
        """Set generic bytes as the body of the request."""
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
        self.internal_response = internal_response  # The object returned by the HTTP library
        self.status_code = None
        self.headers = {}
        self.reason = None 

    def body(self):
        """Return the whole body as bytes in memory."""

    def text(self, encoding=None):
        """Return the whole body as a string."""

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

The pipeline request and response containers are also responsible for carrying a `context` object. This is
transport specific and can contain data persisted between pipeline requests (for example reusing an open connection
pool or "session"), as well as used by the SDK developer to carry arbitrary data through the pipeline.

The API for PipelineRequest and PipelineResponse is as follows:
```python
class PipelineRequest(object):

    def __init__(self, http_request, context):
        self.http_request = http_request  # The HttpRequest
        self.context = context # A transport specific data container object


class PipelineResponse(object):

    def __init__(self, http_request, http_response, context):
        self.http_request = http_request  # The HttpRequest
        self.http_response = http_response  # The HttpResponse
        self.history = []  # A list of redirect attempts.
        self.context = context  # A transport specific data container object
```

### Policies

The Python pipeline implementation provides two flavors of policy. These are referred to as an HttpPolicy and a SansIOPolicy.

#### SansIOHTTPPolicy

If a policy just modifies or annotates the request based on the HTTP specification, it's then a subclass of SansIOHTTPPolicy and will work in either Pipeline or AsyncPipeline context.
This is a simple abstract class, that can act before the request is done, or after. For instance:

- Setting headers in the request
- Logging the request and/or response

A SansIOHTTPPolicy should implement one or more of the following methods:
```python
def on_request(self, request, **kwargs):
    """Is executed before sending the request to next policy."""

def on_response(self, request, response, **kwargs):
    """Is executed after the request comes back from the policy."""

def on_exception(self, request, **kwargs):
    """Is executed if an exception is raised while executing this policy.

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
    RetryPolicy,
    AsyncRetryPolicy,
    RedirectPolicy,
    AsyncRedirectPolicy
)
```

### The Pipeline

The pipeline itself represents a chain of policies where the final node in the chain is the HTTP transport.
A pipeline can either be synchronous or asynchronous.
The pipeline does not expose the policy chain, so individual policies cannot/should not be further
configured once the pipeline has been instantiated.

The pipeline has a single exposed operation: `run(request)` which will send a new HttpRequest object down
the pipeline. This operation returns a `PipelineResponse` object.

```python
class Pipeline:
    """A pipeline implementation.

    This is implemented as a context manager, that will activate the context
    of the HTTP sender.
    """

    def __init__(self, transport, policies=None):
        # type: (HttpTransport, List[Union[HTTPPolicy, SansIOHTTPPolicy]]) -> None
        self._impl_policies = []  # type: List[HTTPPolicy]
        self._transport = transport  # type: HTTPPolicy

        for policy in (policies or []):
            if isinstance(policy, SansIOHTTPPolicy):
                self._impl_policies.append(_SansIOHTTPPolicyRunner(policy))
            elif policy:
                self._impl_policies.append(policy)
        for index in range(len(self._impl_policies)-1):
            self._impl_policies[index].next = self._impl_policies[index+1]
        if self._impl_policies:
            self._impl_policies[-1].next = _TransportRunner(self._transport)

    def run(self, request, **kwargs):
        # type: (HTTPRequestType, Any) -> PipelineResponse
        context = PipelineContext(self._transport, **kwargs)
        pipeline_request = PipelineRequest(request, context)  # type: PipelineRequest[HTTPRequestType]
        first_node = self._impl_policies[0] if self._impl_policies else _TransportRunner(self._transport)
        return first_node.send(pipeline_request)  # type: ignore

```
