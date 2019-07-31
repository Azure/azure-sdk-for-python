
# Release History

-------------------

2019-08-XX Version 1.0.0b2

## Breaking changes

- Transport classes don't take `config` parameter anymore (use kwargs instead)  #6372
- `azure.core.paging` has been completely refactored  #6420
- HttpResponse.content_type attribute is now a string (was a list)  #6490
- For `StreamDownloadGenerator` subclasses, `response` is now an `HttpResponse`, and not a transport response like `aiohttp.ClientResponse` or `requests.Response`. The transport response is available in `internal_response` attribute  #6490

## Bug fixes

- aiohttp is not required to import async pipelines classes #6496
- `AsyncioRequestsTransport.sleep` is now a coroutine as expected #6490
- `RequestsTransport` is not tight to `ProxyPolicy` implementation details anymore #6372
- `AiohttpTransport` does not raise on unexpected kwargs  #6355

## Features

- New paging base classes that support `continuation_token` and `by_page()`  #6420
- Proxy support for `AiohttpTransport`  #6372

2019-06-26 Version 1.0.0b1

- Preview 1 release
