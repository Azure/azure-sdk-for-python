# AzureWebPubSub Service client library for Python

[Source code](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/signalr/azure-messaging-webpubsubservice) | [Package (Pypi)][package] | [API reference documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/signalr/azure-messaging-webpubsubservice) | [Product documentation][webpubsubservice_docs]

## Getting started

### Installating the package

```bash
python -m pip install azure-messaging-webpubsubservice
```

#### Prequisites

* Python 2.7, or 3.6 or later is required to use this package.
* You need an [Azure subscription][azure_sub], and a [Azure WebPubSub service instance][webpubsubservice] to use this package.

### Authenticating the client

In order to interact with the Azure WebPubSub service, you'll need to create an instance of the [WebPubSubServiceClient][webpubsubservice_client_class] class. In order to authenticate against the service, you need to pass in an AzureKeyCredential instance with endpoint and api key. The endpoint and api key can be found on the azure portal.

```python
>>> from azure.messaging.webpubsubservice import WebPubSubServiceClient
>>> from azure.core.credentials import AzureKeyCredential
>>> client = WebPubSubServiceClient(endpoint='<endpoint>', credential=AzureKeyCredential('somesecret'))
>>> client
<WebPubSubServiceClient endpoint:'<endpoint>'>
```

### Sending a request

```python
>>> from azure.messaging.webpubsubservice import WebPubSubServiceClient
>>> from azure.core.credentials import AzureKeyCredential
>>> from azure.messaging.webpubsubservicerest import prepare_send_to_all
>>> client = WebPubSubServiceClient(endpoint='<endpoint>', credential=AzureKeyCredential('somesecret'))
>>> request = prepare_send_to_all('default', { 'Hello':  'webpubsub!' })
>>> request
<HttpRequest [POST], url: '/api/hubs/default/:send?api-version=2020-10-01'>
>>> response = client.send_request()
>>> response
<RequestsTransportResponse: 202 Accepted>
>>> response.status_code 
202
>>> with open('send_messages.py', 'r') as f:
>>>    request = prepare_send_to_all('ahub', f, content_type='text/plain')
>>>    response = client.send_request(request)
>>> print(response)
<RequestsTransportResponse: 202 Accepted>
```

## Key concepts

### Hubs, groups, connections and users

<TODO>

## Troubleshooting

### Logging

This SDK uses Python standard logging library.
You can configure logging print out debugging information to the stdout or anywhere you want.

```python
import logging

logging.basicConfig(level=logging.DEBUG)
````

Http request and response details are printed to stdout with this logging config.

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact opencode@microsoft.com with any
additional questions or comments.

<!-- LINKS -->
[webpubsubservice_docs]: https://docs.microsoft.com/azure/azure-messaging-webpubsubservice/
[azure_cli]: https://docs.microsoft.com/cli/azure
[azure_sub]: https://azure.microsoft.com/free/
[webpubsubservice_client_class]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/signalr/azure-messaging-webpubsubservice/azure/messaging/webpubsubservice/__init__.py
[package]: https://pypi.org/project/azure-messaging-webpubsubservice/
[webpubsubservice]: https://azure.microsoft.com/services/webpubsubservice/
[default_cred_ref]: https://aka.ms/azsdk-python-identity-default-cred-ref
[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
