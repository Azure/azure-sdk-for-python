# Release History

## 1.13.0 (Unreleased)

- Add support for multiapi base client.

## 1.12.0 (2021-03-08)

This version will be the last version to officially support Python 3.5, future versions will require Python 2.7 or Python 3.6+.

### Features

- Added `azure.core.messaging.CloudEvent` model that follows the cloud event spec.
- Added `azure.core.serialization.NULL` sentinel value
- Improve `repr`s for `HttpRequest` and `HttpResponse`s  #16972

### Bug Fixes

- Disable retry in stream downloading. (thanks to @jochen-ott-by @hoffmann for the contribution)  #16723

## 1.11.0 (2021-02-08)

### Features

- Added `CaseInsensitiveEnumMeta` class for case-insensitive enums.  #16316
- Add `raise_for_status` method onto `HttpResponse`. Calling `response.raise_for_status()` on a response with an error code
will raise an `HttpResponseError`. Calling it on a good response will do nothing  #16399

### Bug Fixes

- Update conn.conn_kw rather than overriding it when setting block size. (thanks for @jiasli for the contribution)  #16587

## 1.10.0 (2021-01-11)

### Features

- Added `AzureSasCredential` and its respective policy. #15946

## 1.9.0 (2020-11-09)

### Features

- Add a `continuation_token` attribute to the base `AzureError` exception, and set this value for errors raised
  during paged or long-running operations.

### Bug Fixes

- Set retry_interval to 1 second instead of 1000 seconds (thanks **vbarbaresi** for contributing)  #14357


## 1.8.2 (2020-10-05)

### Bug Fixes

- Fixed bug to allow polling in the case of parameterized endpoints with relative polling urls  #14097


## 1.8.1 (2020-09-08)

### Bug fixes

- SAS credential replicated "/" fix #13159

## 1.8.0 (2020-08-10)

### Features

- Support params as list for exploding parameters  #12410


## 1.7.0 (2020-07-06)

### Bug fixes

- `AzureKeyCredentialPolicy` will now accept (and ignore) passed in kwargs  #11963
- Better error messages if passed endpoint is incorrect  #12106
- Do not JSON encore a string if content type is "text"  #12137

### Features

- Added `http_logging_policy` property on the `Configuration` object, allowing users to individually
set the http logging policy of the config  #12218

## 1.6.0 (2020-06-03)

### Bug fixes

- Fixed deadlocks in AsyncBearerTokenCredentialPolicy #11543
- Fix AttributeException in StreamDownloadGenerator #11462

### Features

- Added support for changesets as part of multipart message support #10485
- Add AsyncLROPoller in azure.core.polling #10801
- Add get_continuation_token/from_continuation_token/polling_method methods in pollers (sync and async) #10801
- HttpResponse and PipelineContext objects are now pickable #10801

## 1.5.0 (2020-05-04)

### Features

- Support "x-ms-retry-after-ms" in response header   #10743
- `link` and `link_from_headers` now accepts attributes   #10765

### Bug fixes

- Not retry if the status code is less than 400 #10778
- "x-ms-request-id" is not considered safe header for logging #10967

## 1.4.0 (2020-04-06)

### Features

- Support a default error type in map_error #9773
- Added `AzureKeyCredential` and its respective policy. #10509
- Added `azure.core.polling.base_polling` module with a "Microsoft One API" polling implementation #10090
  Also contains the async version in `azure.core.polling.async_base_polling`
- Support kwarg `enforce_https` to disable HTTPS check on authentication #9821
- Support additional kwargs in `HttpRequest.set_multipart_mixed` that will be passed into pipeline context.

## 1.3.0 (2020-03-09)

### Bug fixes

- Appended RequestIdPolicy to the default pipeline  #9841
- Rewind the body position in async_retry   #10117

### Features

- Add raw_request_hook support in custom_hook_policy   #9958
- Add timeout support in retry_policy   #10011
- Add OdataV4 error format auto-parsing in all exceptions ('error' attribute)  #9738

## 1.2.2 (2020-02-10)

### Bug fixes

- Fixed a bug that sends None as request_id #9545
- Enable mypy for customers #9572
- Handle TypeError in deep copy #9620
- Fix text/plain content-type in decoder #9589

## 1.2.1 (2020-01-14)

### Bug fixes

- Fixed a regression in 1.2.0 that was incompatible with azure-keyvault-* 4.0.0
[#9462](https://github.com/Azure/azure-sdk-for-python/issues/9462)


## 1.2.0 (2020-01-14)

### Features

- Add user_agent & sdk_moniker kwargs in UserAgentPolicy init   #9355
- Support OPTIONS HTTP verb     #9322
- Add tracing_attributes to tracing decorator   #9297
- Support auto_request_id in RequestIdPolicy   #9163
- Support fixed retry   #6419
- Support "retry-after-ms" in response header   #9240

### Bug fixes

- Removed `__enter__` and `__exit__` from async context managers    #9313

## 1.1.1 (2019-12-03)

### Bug fixes

- Bearer token authorization requires HTTPS
- Rewind the body position in retry #8307

## 1.1.0 (2019-11-25)

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

## 1.0.0 (2019-10-29)

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

## 1.0.0b4 (2019-10-07)

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

## 1.0.0b3 (2019-09-09)

### Bug fixes

-  Fix aiohttp auto-headers #6992
-  Add tracing to policies module init  #6951

## 1.0.0b2 (2019-08-05)

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

## 1.0.0b1 (2019-06-26)

- Preview 1 release
