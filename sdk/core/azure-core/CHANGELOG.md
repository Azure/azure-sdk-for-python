# Release History

## 1.29.5 (2023-10-19)

### Bugs Fixed

- Fixed an issue with `multipart/form-data` in the async transport where `data` was not getting encoded into the request body. #32473

### Other Changes

- Use ssl context from aiohttp by default.

## 1.29.4 (2023-09-07)

### Bugs Fixed

- Fixed the issue that some urls trigger an infinite loop. #31346
- Fixed issue where IndexError was raised if multipart responses did not match the number of requests. #31471
- Fixed issue unbound variable exception if dict is invalid in CloudEvent.from_dict. #31835
- Fixed issue asyncBearerTokenCredentialPolicy is not backward compatible with SansIOHTTPPolicy. #31836
- Fixed issue mypy complains with new version of azure-core. #31564

## 1.29.3 (2023-08-22)

### Bugs Fixed

- Typing fix: `message` cannot be `None` in `AzureError`. #31564

## 1.29.2 (2023-08-14)

### Bugs Fixed

- Added a default implementation for `AsyncTokenCredential.__aexit__()` #31573

### Other Changes

- Bumped `typing-extensions` version to 4.6.0.

## 1.29.1 (2023-08-09)

### Bugs Fixed

- Not pass `enabled_cae` unless it is explicitly enabled.

## 1.29.0 (2023-08-03)

### Features Added

- A keyword argument `enable_cae` was added to the `get_token` method of the `TokenCredential` protocol.  #31012
- `BearerTokenCredentialPolicy` and `AsyncBearerTokenCredentialPolicy` now accept `enable_cae` keyword arguments in their constructors. This is used in determining if [Continuous Access Evaluation (CAE)](https://learn.microsoft.com/azure/active-directory/conditional-access/concept-continuous-access-evaluation) should be enabled for each `get_token` request.  #31012

## 1.28.0 (2023-07-06)

### Features Added

- Added header name parameter to `RequestIdPolicy`. #30772
- Added `SensitiveHeaderCleanupPolicy` that cleans up sensitive headers if a redirect happens and the new destination is in another domain. #28349

### Other Changes

- Catch aiohttp errors and translate them into azure-core errors.

## 1.27.1 (2023-06-13)

### Bugs Fixed

- Fix url building for some complex query parameters scenarios  #30707

## 1.27.0 (2023-06-01)

### Features Added

- Added support to use sync credentials in `AsyncBearerTokenCredentialPolicy`. #30381
- Added "prefix" parameter to AzureKeyCredentialPolicy #29901

### Bugs Fixed

- Improve error message when providing the wrong credential type for AzureKeyCredential  #30380

## 1.26.4 (2023-04-06)

### Features Added

- Updated settings to include OpenTelemetry as a tracer provider.  #29095

### Other Changes

- Improved typing

## 1.26.3 (2023-02-02)

### Bugs Fixed

- Fixed deflate decompression for aiohttp   #28483

## 1.26.2 (2023-01-05)

### Bugs Fixed

- Fix 'ClientSession' object has no attribute 'auto_decompress'  (thanks to @mghextreme for the contribution)

### Other Changes

- Add "x-ms-error-code" as secure header to log
- Rename "DEFAULT_HEADERS_WHITELIST" to "DEFAULT_HEADERS_ALLOWLIST". Added a backward compatible alias.

## 1.26.1 (2022-11-03)

### Other Changes

- Added example of RequestsTransport with custom session.  (thanks to @inirudebwoy for the contribution)   #26768
- Added Python 3.11 support.

## 1.26.0 (2022-10-06)

### Other Changes

- LRO polling will not wait anymore before doing the first status check  #26376
- Added extra dependency for [aio]. pip install azure-core[aio] installs aiohttp too.

## 1.25.1 (2022-09-01)

### Bugs Fixed

- Added @runtime_checkable to `TokenCredential` protocol definitions  #25187

## 1.25.0 (2022-08-04)

Azure-core is supported on Python 3.7 or later. For more details, please read our page on [Azure SDK for Python version support policy](https://github.com/Azure/azure-sdk-for-python/wiki/Azure-SDKs-Python-version-support-policy).

### Features Added

- Added `CaseInsensitiveDict` implementation in `azure.core.utils` removing dependency on `requests` and `aiohttp`

## 1.24.2 (2022-06-30)

### Bugs Fixed

- Fixed the bug that azure-core could not be imported under Python 3.11.0b3  #24928
- `ContentDecodePolicy` can now correctly deserialize more JSON bodies with different mime types #22410

## 1.24.1 (2022-06-01)

### Bugs Fixed

- Declare method level span as INTERNAL by default  #24492
- Fixed type hints for `azure.core.paging.ItemPaged` #24548

## 1.24.0 (2022-05-06)

### Features Added

- Add `SerializationError` and `DeserializationError` in `azure.core.exceptions` for errors raised during serialization / deserialization  #24312

## 1.23.1 (2022-03-31)

### Bugs Fixed

- Allow stream inputs to the `content` kwarg of `azure.core.rest.HttpRequest` from objects with a `read` method  #23578

## 1.23.0 (2022-03-03)

### Features Added

- Improve intellisense type hinting for service client methods. #22891

- Add a case insensitive dict `case_insensitive_dict` in `azure.core.utils`.  #23206

### Bugs Fixed

- Use "\n" rather than "/n" for new line in log.     #23261

### Other Changes

- Log "WWW-Authenticate" header in `HttpLoggingPolicy`  #22990
- Added dependency on `typing-extensions` >= 4.0.1

## 1.22.1 (2022-02-09)

### Bugs Fixed

- Limiting `final-state-via` scope to POST until consuming SDKs has been fixed to use this option properly on PUT.  #22989

## 1.22.0 (2022-02-03)
_[**This version is deprecated.**]_

### Features Added

- Add support for `final-state-via` LRO option in core.  #22713

### Bugs Fixed

- Add response body to string representation of `HttpResponseError` if we're not able to parse out information #22302
- Raise `AttributeError` when calling azure.core.pipeline.transport.\_\_bases__    #22469

### Other Changes

- Python 2.7 is no longer supported. Please use Python version 3.6 or later.

## 1.21.1 (2021-12-06)

### Other Changes

- Revert change in str method  #22023

## 1.21.0 (2021-12-02)

### Breaking Changes

- Sync stream downloading now raises `azure.core.exceptions.DecodeError` rather than `requests.exceptions.ContentDecodingError`

### Bugs Fixed

- Add response body to string representation of `HttpResponseError` if we're not able to parse out information #21800

## 1.20.1 (2021-11-08)

### Bugs Fixed

- Correctly set response's content to decompressed body when users are using aiohttp transport with decompression headers #21620

## 1.20.0 (2021-11-04)

### Features Added

- GA `send_request` onto the `azure.core.PipelineClient` and `azure.core.AsyncPipelineClient`. This method takes in
requests and sends them through our pipelines.
- GA `azure.core.rest`. `azure.core.rest` is our new public simple HTTP library in `azure.core` that users will use to create requests, and consume responses.
- GA errors `StreamConsumedError`, `StreamClosedError`, and `ResponseNotReadError` to `azure.core.exceptions`. These errors
are thrown if you mishandle streamed responses from the `azure.core.rest` module
- add kwargs to the methods for `iter_raw` and `iter_bytes`  #21529
- no longer raise JSON errors if users pass in file descriptors of JSON to the `json` kwarg in `HttpRequest`  #21504
- Added new error type `IncompleteReadError` which is raised if peer closes the connection before we have received the complete message body.

### Breaking Changes

- SansIOHTTPPolicy.on_exception returns None instead of bool.

### Bugs Fixed

- The `Content-Length` header in a http response is strictly checked against the actual number of bytes in the body,
  rather than silently truncating data in case the underlying tcp connection is closed prematurely.
  (thanks to @jochen-ott-by for the contribution)   #20412
- UnboundLocalError when SansIOHTTPPolicy handles an exception    #15222
- Add default content type header of `text/plain` and content length header for users who pass unicode strings to the `content` kwarg of `HttpRequest` in 2.7  #21550

## 1.19.1 (2021-11-01)

### Bugs Fixed

- respect text encoding specified in argument (thanks to @ryohji for the contribution)  #20796
- Fix "coroutine x.read() was never awaited" warning from `ContentDecodePolicy`  #21318
- fix type check for `data` input to `azure.core.rest` for python 2.7 users  #21341
- use `charset_normalizer` if `chardet` is not installed to migrate aiohttp 3.8.0 changes.

### Other Changes

- Refactor AzureJSONEncoder (thanks to @Codejune for the contribution)  #21028

## 1.19.0 (2021-09-30)

### Breaking Changes in the Provisional `azure.core.rest` package

- `azure.core.rest.HttpResponse` and `azure.core.rest.AsyncHttpResponse` are now abstract base classes. They should not be initialized directly, instead
your transport responses should inherit from them and implement them.
- The properties of the `azure.core.rest` responses are now all read-only

- HttpLoggingPolicy integrates logs into one record #19925

## 1.18.0 (2021-09-02)

### Features Added

- `azure.core.serialization.AzureJSONEncoder` (introduced in 1.17.0) serializes `datetime.datetime` objects in ISO 8601 format, conforming to RFC 3339's specification.    #20190
- We now use `azure.core.serialization.AzureJSONEncoder` to serialize `json` input to `azure.core.rest.HttpRequest`.

### Breaking Changes in the Provisional `azure.core.rest` package

- The `text` property on `azure.core.rest.HttpResponse` and `azure.core.rest.AsyncHttpResponse` has changed to a method, which also takes
an `encoding` parameter.
- Removed `iter_text` and `iter_lines` from `azure.core.rest.HttpResponse` and `azure.core.rest.AsyncHttpResponse`

### Bugs Fixed

- The behaviour of the headers returned in `azure.core.rest` responses now aligns across sync and async. Items can now be checked case-insensitively and without raising an error for format.

## 1.17.0 (2021-08-05)

### Features Added

- Cut hard dependency on requests library
- Added a `from_json` method which now accepts storage QueueMessage, eventhub's EventData or ServiceBusMessage or simply json bytes to return a `CloudEvent`

### Fixed

- Not override "x-ms-client-request-id" if it already exists in the header.    #17757

### Breaking Changes in the Provisional `azure.core.rest` package

- `azure.core.rest` will not try to guess the `charset` anymore if it was impossible to extract it from `HttpResponse` analysis. This removes our dependency on `charset`.

## 1.16.0 (2021-07-01)

### Features Added

- Add new ***provisional*** methods `send_request` onto the `azure.core.PipelineClient` and `azure.core.AsyncPipelineClient`. This method takes in
requests and sends them through our pipelines.
- Add new ***provisional*** module `azure.core.rest`. `azure.core.rest` is our new public simple HTTP library in `azure.core` that users will use to create requests, and consume responses.
- Add new ***provisional*** errors `StreamConsumedError`, `StreamClosedError`, and `ResponseNotReadError` to `azure.core.exceptions`. These errors
are thrown if you mishandle streamed responses from the provisional `azure.core.rest` module

### Fixed

- Improved error message in the `from_dict` method of `CloudEvent` when a wrong schema is sent.

## 1.15.0 (2021-06-04)

### New Features

- Added `BearerTokenCredentialPolicy.on_challenge` and `.authorize_request` to allow subclasses to optionally handle authentication challenges

### Bug Fixes

- Retry policies don't sleep after operations time out
- The `from_dict` methhod in the `CloudEvent` can now convert a datetime string to datetime object when microsecond exceeds the python limitation

## 1.14.0 (2021-05-13)

### New Features

- Added `azure.core.credentials.AzureNamedKeyCredential` credential #17548.
- Added `decompress` parameter for `stream_download` method. If it is set to `False`, will not do decompression upon the stream.    #17920

## 1.13.0 (2021-04-02)

Azure core requires Python 2.7 or Python 3.6+ since this release.

### New Features

- Added `azure.core.utils.parse_connection_string` function to parse connection strings across SDKs, with common validation and support for case insensitive keys.
- Supported adding custom policies  #16519
- Added `~azure.core.tracing.Link` that should be used while passing `Links` to  `AbstractSpan`.
- `AbstractSpan` constructor can now take in additional keyword only args.

### Bug fixes

- Make NetworkTraceLoggingPolicy show the auth token in plain text. #14191
- Fixed RetryPolicy overriding default connection timeout with an extreme value #17481

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
- Some modules and classes that were importables from several different places have been removed:

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
