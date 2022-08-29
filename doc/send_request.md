# Using your Client's `send_request` Method

In this doc, we will be showing how to build your own ***http requests*** and how to send these requests directly to the service using the ***send_request*** method.

Here's how to get started:

```python
>>> from azure.identity import DefaultAzureCredential
>>> from azure.example.service import ExampleClient
>>> from azure.core.rest import HttpRequest, HttpResponse
>>> client = ExampleClient(endpoint="https://www.example.org/", credential=DefaultAzureCredential())
>>> request = HttpRequest(method="GET", url="https://www.example.org")
>>> request
<HttpRequest [GET], url: "https://www.example.org">
>>> response = client.send_request(request)
>>> response
<HttpResponse: 200 OK, Content-Type: text/plain>
>>> response.raise_for_status()
>>> response.text()
'Happy to see you!'
```

## Code Snippets

**End-to-end code snippets for creating and sending requests with `send_request`**:

1. [Sync client](#sync-client)
2. [Async client](#async-client)

## Steps To Make a Call

1. [Create a request](#1-create-a-request "Create a Request")
2. [Send the request](#2-send-the-request "Send the Request")
3. [Handle the response](#3-handle-the-response "Handle the Response")

We will go into each step in the following sections. To initialize and authenticate your client, please follow your client's README examples.

## 1. Create a Request

First, we will go over how to create the [`HttpRequest`][azure_core_http_request] you want to be sent to the service.

We will be making a `POST` request with a `JSON` body. The following code snippet uses a relative url, which will be relative
to your client's `endpoint`. You can also pass in a full-path url, and we will honor that full path.

```python
from azure.core.rest import HttpRequest

# this URL is relative to the endpoint we passed our client
request = HttpRequest(
    method="POST",
    url="/helloWorld",
    json={"document": "Hello world!"},
    params={"language": "en"}
)
```

## 2. Send the Request

Now, we pass this request to your client's `send_request` method. This actually makes the network call.

```python
from azure.example.service import ExampleClient

response = client.send_request(request) # makes the network call
```

## 3. Handle the Response

Our `send_request` call returns an [`HttpResponse`][azure_core_http_response].

### Error handling

The response you get back from `send_request` will not automatically raise if your response is an error.
If you wish to raise an error if your response is bad, call [`.raise_for_status()`][azure_core_raise_for_status] on your returned
response.

```python
try:
    response.raise_for_status()  # raises an error if your response is not good
except HttpResponseError as e:
    print(str(e))
```

### JSON response

If the response you get back should be a `json` object, you can call `.json()` on your response
to get it `json`-deserialized.

Putting this all together, see our code snippets for how you can deal with your response object

```python

response = client.send_request(request)
try:
    response.raise_for_status()  # raises an error if your response is not good
    json_response = response.json()  # get your response as a json object
    # Now play with your JSON response!

except HttpResponseError as e:
    print(str(e))
```

## Examples

### Sync Client

```python
from azure.identity import DefaultAzureCredential
from azure.example.service import ExampleClient
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.exceptions import HttpResponseError

client = ExampleClient(
    endpoint="https://example.org",
    credential=DefaultAzureCredential()
)

request = HttpRequest(
    method="POST",
    url="/helloWorld",
    json={"document": "Hello world!"},
    params={"language": "en"}
)

response = client.send_request(request)  # returns an azure.core.rest.HttpResponse

try:
    response.raise_for_status()
    json_response = response.json()
    # Play with your response!
    print(json_response["language"])
except HttpResponseError:
    print(str(e))
```

### Async Client

```python
from azure.identity.aio import DefaultAzureCredential
from azure.example.service.aio import ExampleClient
from azure.core.rest import HttpRequest, AsyncHttpResponse
from azure.core.exceptions import HttpResponseError

request = HttpRequest(
    method="POST",
    url="/helloWorld",
    json={"document": "Hello world!"},
    params={"language": "en"}
)

with DefaultAzureCredential() as credential:
    with ExampleClient(endpoint="https://example.org", credential=credential) as client:
        response = await client.send_request(request)

        try:
            response.raise_for_status()
            await response.load_body()
            json_response = response.json()  # returns an azure.core.rest.AsyncHttpResponse
            # Play with your response!
            print(json_response["language"])
        except HttpResponseError:
            print(str(e))
```

## Troubleshooting

### Errors

All errors thrown by `.raise_for_error()` are [exceptions defined in `azure-core`][azure_core_exceptions].

### Logging

Our clients also have logging support. They use the standard
[logging][python_logging] library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

Detailed DEBUG level logging, including request/response bodies and un-redacted
headers, can be enabled on a client with the `logging_enable` keyword argument.

```python
from azure.identity import DefaultAzureCredential
from azure.example.service import ExampleClient

client = ExampleClient(
    endpoint="https://example.org",
    credential=DefaultAzureCredential(),
    logging_enable=True
)
```

### File an Issue

You can file issues [here][issues] in our repo.

<!-- LINKS -->

[azure_core_docs]: https://docs.microsoft.com/python/api/overview/azure/core-readme?view=azure-python
[azure_identity_docs]: https://docs.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python
[http_response]: https://docs.microsoft.com/python/api/azure-core/azure.core.pipeline.transport.httpresponse?view=azure-python
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[aad_authentication]: https://docs.microsoft.com/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-an-authentication-token
[identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[default_azure_credential]: https://docs.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential?view=azure-python
[azure_key_credential]: https://docs.microsoft.com/python/api/azure-core/azure.core.credentials.azurekeycredential?view=azure-python
[bearer_token_credential_policy]: https://docs.microsoft.com/python/api/azure-core/azure.core.pipeline.policies.bearertokencredentialpolicy?view=azure-python
[azure_key_credential_policy]: https://docs.microsoft.com/python/api/azure-core/azure.core.pipeline.policies.azurekeycredentialpolicy?view=azure-python
[azure_core_exceptions]: https://docs.microsoft.com/python/api/azure-core/azure.core.exceptions?view=azure-python
[azure_core_http_request]: https://docsupport.blob.core.windows.net/$web/azure-core/azure.core.html#azure.core.protocol.HttpRequest
[azure_core_http_response]: https://docsupport.blob.core.windows.net/$web/azure-core/azure.core.html#azure.core.protocol.HttpResponse
[azure_core_async_http_response]: https://docsupport.blob.core.windows.net/$web/azure-core/azure.core.html#azure.core.protocol.AsyncHttpResponse
[azure_core_raise_for_status]: https://docsupport.blob.core.windows.net/$web/azure-core/azure.core.html#azure.core.protocol.HttpResponse.raise_for_status
[python_logging]: https://docs.python.org/3.5/library/logging.html
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
[issues]: https://github.com/Azure/azure-sdk-for-python/issues
