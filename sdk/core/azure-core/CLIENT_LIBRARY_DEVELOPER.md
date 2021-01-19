
# Azure Core Library - Client library developer reference

## Pipeline

The Azure Core pipeline is a re-structuring of the msrest pipeline introduced in msrest 0.6.0.
Further discussions on the msrest implementation can be found in the [msrest wiki](https://github.com/Azure/msrest-for-python/wiki/msrest-0.6.0---Pipeline).

The Azure Core Pipeline is an implementation of chained policies as described in the [Azure SDK guidelines](https://github.com/Azure/azure-sdk/blob/master/docs/general/design.md).

The Python implementation of the pipeline has some mechanisms specific to Python. This is due to the fact that both synchronous and asynchronous implementations of the pipeline must be supported independently.

When constructing an SDK, a developer may consume the pipeline like so:

```python
from azure.core.pipeline import Pipeline
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

class FooServiceClient:

    def __init__(self, **kwargs):
        transport = kwargs.get('transport', RequestsTransport(**kwargs))
        policies = [
            kwargs.get('user_agent_policy', UserAgentPolicy("ServiceUserAgentValue", **kwargs)),
            kwargs.get('headers_policy', HeadersPolicy({"CustomHeader": "Value"}, **kwargs)),
            kwargs.get('authentication_policy', BearerTokenCredentialPolicy(credential, scopes, **kwargs)),
            ContentDecodePolicy(),
            kwargs.get('proxy_policy', ProxyPolicy(**kwargs)),
            kwargs.get('redirect_policy', RedirectPolicy(**kwargs)),
            kwargs.get('retry_policy', RetryPolicy(**kwargs)),
            kwargs.get('logging_policy', NetworkTraceLoggingPolicy(**kwargs)),
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
# All configuration options are passed through kwargs
client = FooServiceClient(
    endpoint,
    creds,
    retry_policy=CustomRetryPolicy()
    redirect_max=5,
    logging_enable=True
)
response = client.get_foo_properties()
```

### Pipeline client configurations

| Parameters | Description |
| --- | --- |
| `pipeline` | While `PipelineClient` will create a default pipeline, users can opt to use their own pipeline by passing in a `Pipeline` object. If passed in, the other configurations will be ignored.  |
| `config` | While `PipelineClient` will create a default `Configuration`, users can opt to use their own configuration by passing in a `Configuration` object. If passed in, it will be used to create a `Pipeline` object. |
| `transport` | While `PipelineClient` will create a default `RequestsTransport`, users can opt to use their own transport by passing in a `RequestsTransport` object. If it is omitted, `PipelineClient` will honor the other described [transport customizations](#transport). |


### Transport

Various combinations of sync/async HTTP libraries as well as alternative event loop implementations are available. Therefore to support the widest range of customer scenarios, we must allow a customer to easily swap out the HTTP transport layer to one of those supported.

The transport is the last node in the pipeline, and adheres to the same basic API as any policy within the pipeline.
The only currently available transport for synchronous pipelines uses the `Requests` library:
```python
from azure.core.pipeline.transport import RequestsTransport
synchronous_transport = RequestsTransport()
```

For asynchronous pipelines a couple of transport options are available. Each of these transports are interchangable depending on whether the user has installed various 3rd party dependencies (i.e. aiohttp or trio), and the user
should easily be able to specify their chosen transport. SDK developers should use the `aiohttp` transport as the default for asynchronous pipelines where the user has not specified an alternative.
```python
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

client = FooServiceClient(endpoint, creds, transport=AioHttpTransport())
response = await client.get_foo_properties()
```

Some common properties can be configured on all transports. They must be passed
as kwargs arguments while building the transport instance. These include the following properties:
```python
transport = AioHttpTransport(
        # The connect and read timeout value. Defaults to 100 seconds.
        connection_timeout=100,

        # SSL certificate verification. Enabled by default. Set to False to disable,
        # alternatively can be set to the path to a CA_BUNDLE file or directory with
        # certificates of trusted CAs.
        connection_verify=True,

        # Client-side certificates. You can specify a local cert to use as client side
        # certificate, as a single file (containing the private key and the certificate)
        # or as a # tuple of both files' paths.
        connection_cert=None,

        # The block size of data sent over the connection. Defaults to 4096 bytes.
        connection_data_block_size=4096
)
```

### Proxy Settings

There are two ways to configure proxy settings.

- Use environment proxy settings

When creating the transport, "use_env_settings" parameter can be used to enable or disable the environment proxy settings. e.g.:

```python
synchronous_transport = RequestsTransport(use_env_settings=True)
```

If "use_env_settings" is set to True(by default), the transport will look for environment variables 

- HTTP_PROXY
- HTTPS_PROXY

and use their values to configure the proxy settings.

- Use ProxyPolicy

You can use ProxyPolicy to configure the proxy settings as well. e.g.

```python
from azure.core.pipeline.policies import ProxyPolicy

proxy_policy = ProxyPolicy()

proxy_policy.proxies = {'http': 'http://10.10.1.10:3148'}

# Use basic auth
proxy_policy.proxies = {'https': 'http://user:password@10.10.1.10:1180/'}
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

    def set_multipart_mixed(self, *requests, **kwargs):
        """Set requests for a multipart/mixed body.
        Optionally apply "policies" in kwargs to each request.
        """
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
        self.headers = CaseInsensitiveDict()
        self.reason = None
        self.content_type = None

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

    def parts(self):
        """An iterator of parts if content-type is multipart/mixed.
        For the AsyncHttpResponse object this function will return
        and asynchronous iterator.
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

The Python pipeline implementation provides two flavors of policy. These are referred to as an HttpPolicy and a SansIOHTTPPolicy.

#### SansIOHTTPPolicy

If a policy just modifies or annotates the request based on the HTTP specification, it's then a subclass of SansIOHTTPPolicy and will work in either Pipeline or AsyncPipeline context.
This is a simple abstract class, that can act before the request is done, or after. For instance:

- Setting headers in the request
- Logging the request and/or response

A SansIOHTTPPolicy should implement one or more of the following methods:
```python
def on_request(self, request):
    """Is executed before sending the request to next policy."""

def on_response(self, request, response):
    """Is executed after the request comes back from the policy."""

def on_exception(self, request):
    """Is executed if an exception is raised while executing this policy.

    Return True if the exception has been handled and should not
    be forwarded to the caller.
    """
```

SansIOHTTPPolicy methods can be declared as coroutines, but then they can only be used with a AsyncPipeline.

Current provided sans IO policies include:
```python
from azure.core.pipeline.policies import (
    HeadersPolicy,  # Add custom headers to all requests
    UserAgentPolicy,  # Add a custom user agent header
    NetworkTraceLoggingPolicy,  # Log request and response contents
    ContentDecodePolicy,  # Mandatory policy for decoding unstreamed response content
    HttpLoggingPolicy,  # Handles logging of HTTP requests and responses
    ProxyPolicy,    # Enable proxy settings
    CustomHookPolicy,   # Enable the given callback with the response
    DistributedTracingPolicy    # Create spans for Azure calls
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

    def send(self, request):
        """Mutate the request."""

        return self.next.send(request)

class CustomAsyncPolicy(AsyncHTTPPolicy):

    async def send(self, request):
        """Mutate the request."""

        return await self.next.send(request)
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

#### Available Policies

| Name | Policy Flavor | Parameters | Accepted in Init? | Accepted in Request? | Description |
| --- | --- | --- | --- | --- | --- |
| HeadersPolicy | SansIOHTTPPolicy |  |  |  |  |
|  |  | base_headers | x |  | Headers to send with the request. |
|  |  | headers | x | x | The HTTP Request headers. |
| RequestIdPolicy | SansIOHTTPPolicy |  |  |  |  |
|  |  | request_id | x | x | The request id to be added into header. |
|  |  | auto_request_id | x |  | Auto generates a unique request ID per call if `True` which is by default. |
| UserAgentPolicy | SansIOHTTPPolicy |  |  |  |  |
|  |  | base_user_agent | x |  | Sets the base user agent value. |
|  |  | user_agent_overwrite | x |  | Overwrites User-Agent when True. Defaults to `False`. |
|  |  | user_agent_use_env | x |  | Gets user-agent from environment. Defaults to `True`. |
|  |  | user_agent | x | x | If specified, this will be added in front of the user agent string. |
|  |  | sdk_moniker | x |  | If specified, the user agent string will be `azsdk-python-[sdk_moniker] Python/[python_version] ([platform_version])` |
| NetworkTraceLoggingPolicy | SansIOHTTPPolicy |  |  |  |  |
|  |  | logging_enable | x | x | Use to enable per operation. Defaults to `False`. |
| HttpLoggingPolicy | SansIOHTTPPolicy |  |  |  |  |
|  |  | logger | x | x | If specified, it will be used to log information |
| ContentDecodePolicy | SansIOHTTPPolicy |  |  |  |  |
|  |  | response_encoding | x | x | The encoding to use if known for this service (will disable auto-detection). |
| ProxyPolicy | SansIOHTTPPolicy |  |  |  |  |
|  |  | proxies | x | x | Maps protocol or protocol and hostname to the URL of the proxy. |
| CustomHookPolicy | SansIOHTTPPolicy |  |  |  |  |
|  |  | raw_request_hook | x | x | Callback function. Will be invoked on request. |
|  |  | raw_response_hook | x | x | Callback function. Will be invoked on response. |
| DistributedTracingPolicy | SansIOHTTPPolicy |  |  |  |  |
|  |  | network_span_namer | x | x | A callable to customize the span name. |
|  |  | tracing_attributes | x | x | Attributes to set on all created spans. |
| --- | --- | --- | --- | --- | --- |
| RedirectPolicy | HTTPPolicy |  |  |  |  |
|  |  | permit_redirects | x | x | Whether the client allows redirects. Defaults to `True`. |
|  |  | redirect_max | x | x | The maximum allowed redirects. Defaults to `30`. |
| AsyncRedirectPolicy | AsyncHTTPPolicy |  |  |  |  |
|  |  | permit_redirects | x | x | Whether the client allows redirects. Defaults to `True`. |
|  |  | redirect_max | x | x | The maximum allowed redirects. Defaults to `30`. |
| RetryPolicy | HTTPPolicy |  |  |  |  |
|  |  | retry_total | x | x | Total number of retries to allow. Takes precedence over other counts. Default value is `10`. |
|  |  | retry_connect | x | x | How many connection-related errors to retry on. These are errors raised before the request is sent to the remote server, which we assume has not triggered the server to process the request. Default value is `3`. |
|  |  | retry_read | x | x | How many times to retry on read errors. These errors are raised after the request was sent to the server, so the request may have side-effects. Default value is `3`. |
|  |  | retry_status | x | x | How many times to retry on bad status codes. Default value is `3`. |
|  |  | retry_backoff_factor | x | x | A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a second try without a delay). Retry policy will sleep for: `{backoff factor} * (2 ** ({number of total retries} - 1))` seconds. If the backoff_factor is 0.1, then the retry will sleep for [0.0s, 0.2s, 0.4s, ...] between retries. The default value is `0.8`. |
|  |  | retry_backoff_max | x | x | The maximum back off time. Default value is `120` seconds (2 minutes). |
|  |  | retry_mode | x | x | Fixed or exponential delay between attemps, default is `exponential`. |
|  |  | timeout | x | x | Timeout setting for the operation in seconds, default is `604800s` (7 days). |
| AsyncRetryPolicy | AsyncHTTPPolicy |  |  |  |  |
|  |  | retry_total | x | x | Total number of retries to allow. Takes precedence over other counts. Default value is `10`. |
|  |  | retry_connect | x | x | How many connection-related errors to retry on. These are errors raised before the request is sent to the remote server, which we assume has not triggered the server to process the request. Default value is `3`. |
|  |  | retry_read | x | x | How many times to retry on read errors. These errors are raised after the request was sent to the server, so the request may have side-effects. Default value is `3`. |
|  |  | retry_status | x | x | How many times to retry on bad status codes. Default value is `3`. |
|  |  | retry_backoff_factor | x | x | A backoff factor to apply between attempts after the second try (most errors are resolved immediately by a second try without a delay). Retry policy will sleep for: `{backoff factor} * (2 ** ({number of total retries} - 1))` seconds. If the backoff_factor is 0.1, then the retry will sleep for [0.0s, 0.2s, 0.4s, ...] between retries. The default value is `0.8`. |
|  |  | retry_backoff_max | x | x | The maximum back off time. Default value is `120` seconds (2 minutes). |
|  |  | retry_mode | x | x | Fixed or exponential delay between attemps, default is exponential. |
|  |  | timeout | x | x | Timeout setting for the operation in seconds, default is `604800s` (7 days). |


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
