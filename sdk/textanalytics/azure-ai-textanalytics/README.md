# Azure Text Analytics Low-Level Client library for Python

## Low Level Client

Our low level clients provide simple, reliable connection to raw HTTP for previews and advanced usage. We provide caller `send_request` on the client to send requests to the service.
Calls through this method fully harness the power of `azure-core` (TODO: link to sphinx docs) and [`azure-identity`][azure_identity_docs].

The basic structure of calls with low level clients is:

1. [Initialize your client](#initialize-your-client "Initialize Your Client")
2. [Create a request](#create-a-request "Create a Request")
3. [Send the request](#send-the-request "Send the Request")
4. [Handle the response](#handle-the-response "Handle the Response")

We will go into each step in the following sections

### Initialize Your Client

First you import your client from the namespace of your package. For example, let's say your namespace is `azure.pets` and your client's name
is `PetsClient`. Your import would look like

```python
from azure.pets import PetsClient
```

Follow the instructions here (TODO: link to sphinx docs) for all of the input parameters to your client.

Most clients require authenticating through their `credential` parameter.

#### Authenticating with AAD

Our clients support authenticating with an [Azure Active Directory (AAD) token credential][aad_authentication]. We always recommend
using a [credential type][identity_credentials] obtained from the [`azure-identity`][azure_identity_docs] library for AAD authentication. For this example,
we use the most common [`DefaultAzureCredential`][default_azure_credential].

As an installation note, the [`azure-identity`][azure_identity_docs] library is not a dependency of this library. Please pip install [`azure-identity`][azure_identity_pip]
before using [AAD authentication][aad_authentication]

```bash
pip install azure-identity
```

Now, on to our code example:

```python
from azure.identity import DefaultAzureCredential
from azure.pets import PetsClient

client = PetsClient(credential=DefaultAzureCredential())
```

#### Authenticating with [`AzureKeyCredential`][azure_key_credential]

Some libraries also support authenticating with an [`AzureKeyCredential`][azure_key_credential]. See this client's docs (TODO: link to sphinx docs) to see
if you can use an [`AzureKeyCredential`][azure_key_credential] to authenticate. The following code snippet shows you how to authenticate with an
[`AzureKeyCredential`][azure_key_credential]

```python
from azure.core.credentials import AzureKeyCredential
from azure.pets import PetsClient

credential: str = "myCredential"
client = PetsClient(credential=AzureKeyCredential(credential))
```

### Create a Request

Next, you need to create the request you want to be sent to the service.

You have two options here: create the `HttpRequest` (TODO: link to sphinx docs) fully by yourself, or enlist the help of our request preparers.

When creating your `HttpRequest`, always refer to the [REST API][rest_api_docs] docs to see what your requests should look like.

#### Create Your Own `HttpRequest`

Creating an `HttpRequest` (TODO: link to sphinx docs) by yourself offers you the most flexibility, and is always a great fallback option. Below is a code
example for how to create an `HttpRequest` (TODO: link to sphinx docs). Here we `POST` a `json` body to a service's `3.0` endpoint. Please refer
to the [REST API][rest_api_docs] docs to see what requests to the service should look like.

```python
from azure.core.pipeline.transport import HttpRequest

request = HttpRequest("POST", "https://myPets/v3.0/cutePets",
    json={
        "pets": [
            {
                "name": "Fido",
                "age": 42,
                "favoriteFood": "meat"
            },
            {
                "name": "Bessie",
                "age": 1,
                "favoriteFood": "fish"
            }
        ]
    }
)

# now we format the query parameters
request.format_parameters(
    {
        "petOwnerName": "azure",
    }
)
```

#### Use our Request Preparers

We offer request preparers to help you create requests for each of the documented endpoints. With the request preparers, we handle things like
the URL path and formatting query and header parameters. We also provide better intellisense, so you know just what to pass to our preparers.

Let's make the same call as in the [previous example](#create-your-own-httprequest "Create Your Own `HttpRequest`"). Once again, lease refer
to the [REST API][rest_api_docs] docs to see what actual requests to the service should look like.

```python
from azure.pets.protocol import PetsPreparers
from azure.core.pipeline.transport import HttpRequest

request: HttpRequest = PetsPreparers.prepare_cute_pets(
    api_version="v3.0",
    body={
        "pets": [
            {
                "name": "Fido",
                "age": 42,
                "favoriteFood": "meat"
            },
            {
                "name": "Bessie",
                "age": 1,
                "favoriteFood": "fish"
            }
        ]
    },
    pet_owner_name="azure",
)
```

### Send the Request

Now, we pass this request to your client's `send_request` method.

```python
from azure.pets import PetsClient
from azure.core.pipeline.transport import HttpResponse

# Create your request. See above examples for how to.

response: HttpResponse = client.send_request(request)
```

### Handle the Response

You can see the [REST API docs][rest_api_docs] for examples of good and bad responses.

Our `send_request` call returns an `HttpResponse` (TODO: link to sphinx docs).

Below is an example of how we handle a json response

```python

# Get your response following the previous example

response.raise_for_status()  # raises an error if your response is not good

json_response = response.json()  # get your response as a json object

# Now play with your response!
```


## Troubleshooting

### General

The Text Analytics client will raise [exceptions defined in `azure-core`][azure_core_exceptions].

### Logging

This library uses the standard
[logging][python_logging] library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

Detailed DEBUG level logging, including request/response bodies and unredacted
headers, can be enabled on a client with the `logging_enable` keyword argument.

```python
from azure.identity import DefaultAzureCredential
from azure.pets import PetsClient

client = PetsClient(
    credential=DefaultAzureCredential(),
    logging_enable=True
)
```

### Additional documentation

For more extensive documentation on Azure Cognitive Services Text Analytics' REST API endpoint, see [here][rest_api_docs]

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[azure_core_docs]: https://docs.microsoft.com/python/api/overview/azure/core-readme?view=azure-python
[azure_identity_docs]: https://docs.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python
[http_response]: https://docs.microsoft.com/python/api/azure-core/azure.core.pipeline.transport.httpresponse?view=azure-python
[azure_identity_pip]: https://pypi.org/project/azure-identity/

[aad_authentication]: https://docs.microsoft.com/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-an-authentication-token
[identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity#credentials
[default_azure_credential]: https://docs.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential?view=azure-python
[azure_key_credential]: https://docs.microsoft.com/python/api/azure-core/azure.core.credentials.azurekeycredential?view=azure-python
[bearer_token_credential_policy]: https://docs.microsoft.com/python/api/azure-core/azure.core.pipeline.policies.bearertokencredentialpolicy?view=azure-python
[azure_key_credential_policy]: https://docs.microsoft.com/python/api/azure-core/azure.core.pipeline.policies.azurekeycredentialpolicy?view=azure-python
[azure_core_exceptions]: https://docs.microsoft.com/python/api/azure-core/azure.core.exceptions?view=azure-python

[python_logging]: https://docs.python.org/3.5/library/logging.html
[rest_api_docs]: https://westus2.dev.cognitive.microsoft.com/docs/services/TextAnalytics-v3-1-preview-1/operations/Languages
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
