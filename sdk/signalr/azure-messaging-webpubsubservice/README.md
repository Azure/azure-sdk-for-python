# Azure client library for the AzureWebPubSub Service 

## Getting started

### Installating the package

```bash
python -m pip install azure-messaging-webpubsubservice
```

#### Prequisites

Python 3.6 or later.

### Authenticating the client

```python
>>> from azure.messaging.webpubsub import WebPubSubServiceClient
>>> from azure.core.credentials import AzureKeyCredential
>>> client = WebPubSubServiceClient(endpoint='<endpoint>', credentials=AzureKeyCredential('somesecret'))
>>> client
<something something>
```

### Sending a request

```python
>>> from azure.messaging.webpubsub import WebPubSubServiceClient
>>> from azure.core.credentials import AzureKeyCredential
>>> from azure.messaging.webpubsub.rest import prepare_send_to_all
>>> client = WebPubSubServiceClient(endpoint='<endpoint>', credentials=AzureKeyCredential('somesecret'))
>>> request = prepare_send_to_all('default', 'Hello, webpubsub!')
>>> request
<something something>
>>> response = client.send_request()
>>> response
<something something>
>>> response.status_code 
202
```
