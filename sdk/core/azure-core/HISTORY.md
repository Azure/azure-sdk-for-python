
# Release History

-------------------
## 2019-11-25 Version 1.1.0

### Features

- New RequestIdPolicy   #8437
- Enable logging policy in default pipeline #8053
- Normalize transport timeout.   #8000
  Now we have:
  * 'connection_timeout' - a single float in seconds for the connection timeout. Default 5min
  * 'read_timeout' - a single float in seconds for the read timeout. Default 5min

### Bug fixes

- RequestHistory: deepcopy fails if request contains a stream  #7732
- Retry: retry raises error if response does not have http_response #8629
- Client kwargs are now passed to DistributedTracingPolicy correctly    #8051
- NetworkLoggingPolicy now logs correctly all requests in case of retry #8262

## 2019-10-29 Version 1.0.0

### Features

- Tracing: DistributedTracingPolicy now accepts kwargs network_span_namer to change network span name  #7773
- Tracing: Implementation of AbstractSpan can now use the mixin HttpSpanMixin to get HTTP span update automatically  #7773
- Tracing: AbstractSpan contract "change_context" introduced  #7773
- Introduce new policy HttpLoggingPolicy  #7988

### Bug fixes

- Fix AsyncioRequestsTransport if input stream is an async generator  #7743
- Fix form-data with aiohttp transport  #7749

### Breaking changes

- Tracing: AbstractSpan.set_current_span is longer supported. Use change_context instead.  #7773
- azure.core.pipeline.policies.ContentDecodePolicy.deserialize_from_text changed

## 2019-10-07 Version 1.0.0b4

### Features

- Tracing: network span context is available with the TRACING_CONTEXT in pipeline response  #7252
- Tracing: Span contract now has `kind`, `traceparent` and is a context manager  #7252
- SansIOHTTPPolicy methods can now be coroutines #7497
- Add multipart/mixed support #7083:

  - HttpRequest now has a "set_multipart_mixed" method to set the parts of this request
  - HttpRequest now has a "prepare_multipart_body" method to build final body.
  - HttpResponse now has a "parts" method to return an iterator of parts
  - AsyncHttpResponse now has a "parts" methods to return an async iterator of parts
  - Note that multipart/mixed is a Python 3.x only feature

### Bug fixes

- Tracing: policy cannot fail the pipeline, even in the worst condition  #7252
- Tracing: policy pass correctly status message if exception  #7252
- Tracing: incorrect span if exception raised from decorated function  #7133
- Fixed urllib3 ConnectTimeoutError being raised by Requests during a socket timeout. Now this exception is caught and wrapped as a `ServiceRequestError`  #7542

### Breaking changes

- Tracing: `azure.core.tracing.context` removed
- Tracing: `azure.core.tracing.context.tracing_context.with_current_context` renamed to `azure.core.tracing.common.with_current_context`  #7252
- Tracing: `link` renamed `link_from_headers`  and `link` takes now a string
- Tracing: opencensus implementation has been moved to the package `azure-core-tracing-opencensus`
- Some modules and classes that were importables from several differente places have been removed:

   - `azure.core.HttpResponseError` is now only `azure.core.exceptions.HttpResponseError`
   - `azure.core.Configuration` is now only `azure.core.configuration.Configuration`
   - `azure.core.HttpRequest` is now only `azure.core.pipeline.transport.HttpRequest`
   - `azure.core.version` module has been removed. Use `azure.core.__version__` to get version number.
   - `azure.core.pipeline_client` has been removed. Import from `azure.core` instead.
   - `azure.core.pipeline_client_async` has been removed. Import from `azure.core` instead.
   - `azure.core.pipeline.base` has been removed. Import from `azure.core.pipeline` instead.
   - `azure.core.pipeline.base_async` has been removed. Import from `azure.core.pipeline` instead.
   - `azure.core.pipeline.policies.base` has been removed. Import from `azure.core.pipeline.policies` instead.
   - `azure.core.pipeline.policies.base_async` has been removed. Import from `azure.core.pipeline.policies` instead.
   - `azure.core.pipeline.policies.authentication` has been removed. Import from `azure.core.pipeline.policies` instead.
   - `azure.core.pipeline.policies.authentication_async` has been removed. Import from `azure.core.pipeline.policies` instead.
   - `azure.core.pipeline.policies.custom_hook` has been removed. Import from `azure.core.pipeline.policies` instead.
   - `azure.core.pipeline.policies.redirect` has been removed. Import from `azure.core.pipeline.policies` instead.
   - `azure.core.pipeline.policies.redirect_async` has been removed. Import from `azure.core.pipeline.policies` instead.
   - `azure.core.pipeline.policies.retry` has been removed. Import from `azure.core.pipeline.policies` instead.
   - `azure.core.pipeline.policies.retry_async` has been removed. Import from `azure.core.pipeline.policies` instead.
   - `azure.core.pipeline.policies.distributed_tracing` has been removed. Import from `azure.core.pipeline.policies` instead.
   - `azure.core.pipeline.policies.universal` has been removed. Import from `azure.core.pipeline.policies` instead.
   - `azure.core.tracing.abstract_span` has been removed. Import from `azure.core.tracing` instead.
   - `azure.core.pipeline.transport.base` has been removed. Import from `azure.core.pipeline.transport` instead.
   - `azure.core.pipeline.transport.base_async` has been removed. Import from `azure.core.pipeline.transport` instead.
   - `azure.core.pipeline.transport.requests_basic` has been removed. Import from `azure.core.pipeline.transport` instead.
   - `azure.core.pipeline.transport.requests_asyncio` has been removed. Import from `azure.core.pipeline.transport` instead.
   - `azure.core.pipeline.transport.requests_trio` has been removed. Import from `azure.core.pipeline.transport` instead.
   - `azure.core.pipeline.transport.aiohttp` has been removed. Import from `azure.core.pipeline.transport` instead.
   - `azure.core.polling.poller` has been removed. Import from `azure.core.polling` instead.
   - `azure.core.polling.async_poller` has been removed. Import from `azure.core.polling` instead.

## 2019-09-09 Version 1.0.0b3

### Bug fixes

-  Fix aiohttp auto-headers #6992
-  Add tracing to policies module init  #6951

## 2019-08-05 Version 1.0.0b2

### Breaking changes

- Transport classes don't take `config` parameter anymore (use kwargs instead)  #6372
- `azure.core.paging` has been completely refactored  #6420
- HttpResponse.content_type attribute is now a string (was a list)  #6490
- For `StreamDownloadGenerator` subclasses, `response` is now an `HttpResponse`, and not a transport response like `aiohttp.ClientResponse` or `requests.Response`. The transport response is available in `internal_response` attribute  #6490

### Bug fixes

- aiohttp is not required to import async pipelines classes #6496
- `AsyncioRequestsTransport.sleep` is now a coroutine as expected #6490
- `RequestsTransport` is not tight to `ProxyPolicy` implementation details anymore #6372
- `AiohttpTransport` does not raise on unexpected kwargs  #6355

### Features

- New paging base classes that support `continuation_token` and `by_page()`  #6420
- Proxy support for `AiohttpTransport`  #6372

## 2019-06-26 Version 1.0.0b1

- Preview 1 release
