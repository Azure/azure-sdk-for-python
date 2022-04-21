# Using Request Builders with Your Service Client

In this doc, we will be showing how to use our ***request builders*** to build ***http requests*** - or create raw ***http requests*** yourselves - and
send these requests directly to the service using the ***send_request*** method.

Here's how to get started:

```python
>>> from azure.identity import DefaultAzureCredential
>>> from azure.example import ExampleClient
>>> from azure.example.rest import build_example_request
>>> client = ExampleClient(endpoint='https://www.example.org/', credential=DefaultAzureCredential())
>>> request = build_example_request()
>>> request
<HttpRequest [GET], url: 'https://www.example.org'>
>>> response = client.send_request(request)
>>> response
<HttpResponse: 200 OK, Content-Type: text/plain>
>>> response.raise_for_status()
>>> response.text
'Happy to see you!'
```

## Code Snippets

**Code snippets for how to use our request builders with our clients**:

1. [Sync client](#sync-client)
2. [Async client](#async-client)

## Steps To Make a Call

1. [Initialize your client](#1-initialize-your-client "Initialize Your Client")
2. [Create a request](#2-create-a-request "Create a Request")
3. [Send the request](#3-send-the-request "Send the Request")
4. [Handle the response](#4-handle-the-response "Handle the Response")

We will go into each step in the following sections

## 1. Initialize Your Client

First you import your client from the namespace of your package. For example, let's say your namespace is `azure.example` and your client's name
is `ExampleClient`. Your import would look like

```python
from azure.example import ExampleClient
```

Most clients require authenticating through their `credential` parameter. Depending on what authentication support your library is using, you can either [authenticate with aad](#authenticating-with-aad) or [authenticate with an `AzureKeyCredential`](#authenticating-with-azurekeycredential).

Additionally, most of our clients accept an `endpoint` parameter at initialization, usually a link to your own resource.

### Authenticating with AAD

If your client supports authenticating with an [Azure Active Directory (AAD) token credential][aad_authentication], we provide a convenient library for AAD authentication called [`azure-identity`][azure_identity_docs] that can be installed additionally with:

```bash
pip install azure-identity
```

Once [`azure-identity`][azure_identity_pip] is installed, the simplest way to authenticate is to use the [`DefaultAzureCredential`][default_azure_credential] class.

The following code snippet shows you how to authenticate with a [`DefaultAzureCredential`][default_azure_credential].

```python
from azure.identity import DefaultAzureCredential
from azure.example import ExampleClient

client = ExampleClient(
    endpoint="https://www.example.org/",
    credential=DefaultAzureCredential()
)
```

### Authenticating with [`AzureKeyCredential`][azure_key_credential]

Some libraries support authenticating with an [`AzureKeyCredential`][azure_key_credential]. The following code snippet shows you how to authenticate with an
[`AzureKeyCredential`][azure_key_credential]

```python
from azure.core.credentials import AzureKeyCredential
from azure.example import ExampleClient

credential = "myCredential"
client = ExampleClient(
    endpoint="https://www.example.org/",
    credential=AzureKeyCredential(credential)
)
```

## 2. Create a Request

Next, you need to create the request you want to be sent to the service.

We offer [request builders](#use-our-request-builders) to make creating your `HttpRequest`s easier.

For more advanced users, you can also [create your `HttpRequest` fully by yourself](#create-your-own-httprequest)

### Use our Request Builders

Our request builders:

- Keep track of the URL and method of the call, so you don't have to
- Let you know what parameters the service needs
- Take care of formatting your parameters
- Will be grouped into submodules if there's a natural grouping to them.

These request builders are located in the `rest` module of our libraries. If there's
a natural grouping to request builders, these submodule groups will live inside the `rest` module.

Now, let's make a request with a `json` body.

```python
from azure.example.rest import build_analyze_text_request

request = build_analyze_text_request(
    json={"document": "Hello world!"},
    language="en",
)
```

If the `rest` module has grouped submodules, we recommend importing the whole submodule like this to
avoid name conflicts:

```python
from azure.example.rest import languages

request = languages.build_detect_request(
    json={"document": "世界你好！"}
)
```

### Create Your Own [`HttpRequest`][azure_core_http_request]

For more advanced scenarios, you can also create your own [`HttpRequest`][azure_core_http_request].

Let's make the same request as we do in our [previous example](#use-our-request-builders)

```python
from azure.example.core.rest import HttpRequest

# this URL is relative to the endpoint we passed our client
request = HttpRequest("POST", "/helloWorld",
    json={"document": "Hello world!"},
    params={"language": "en"}
)
```

## 3. Send the Request

Now, we pass this request to your client's `send_request` method. This actually makes the network call.

```python
from azure.example import ExampleClient

response = client.send_request(request) # makes the network call
```

## 4. Handle the Response

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
from azure.example import ExampleClient
from azure.example.rest import build_analyze_text_request
from azure.core.exceptions import HttpResponseError

client = ExampleClient(
    endpoint="https://example.org",
    credential=DefaultAzureCredential()
)

request = build_analyze_text_request(
    json={"document": "Hello world!"},
    language="en",
)

response = client.send_request(request)

try:
    response.raise_for_status()
    json_response = response.json()
    # Play with your response!
except HttpResponseError:
    print(str(e))
```

### Async Client

```python
from azure.identity.aio import DefaultAzureCredential
from azure.example.aio import ExampleClient
from azure.example.rest import build_analyze_text_request
from azure.core.exceptions import HttpResponseError

request = build_analyze_text_request(
    json={"document": "Hello world!"},
    language="en",
)

with DefaultAzureCredential() as credential:
    with ExampleClient(endpoint="https://example.org", credential=credential) as client:
        response = await client.send_request(request)

        try:
            response.raise_for_status()
            await response.load_body()
            json_response = response.json()
            # Play with your response!
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
from azure.example import ExampleClient

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
