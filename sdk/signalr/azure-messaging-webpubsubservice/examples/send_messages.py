import os

from azure.core.credentials import AzureKeyCredential
from azure.messaging.webpubsubservice import WebPubSubServiceClient
from azure.messaging.webpubsubservice.rest import *

endpoint = os.environ.get('ENDPOINT', 'https://johanstewebpubsub.service.signalr.net')
api_key = os.environ.get('API_KEY', 'rvMSyJnRJsPLugamjdSl84HXM7w/jE6w2BLfYLiyJ3E=')

endpoint = 'https://johanstewebpubsub.service.signalr.net'
api_key = 'rvMSyJnRJsPLugamjdSl84HXM7w/jE6w2BLfYLiyJ3E='
client = WebPubSubServiceClient(endpoint, credentials=AzureKeyCredential(api_key))

request = prepare_send_to_all('_default', 'Hello, all!', content_type='application/json')
response = client.send_request(request)
response.raise_for_status()
print(response)

request = prepare_add_user_to_group('_default', group='someGroup', user_id='me')
response = client.send_request(request)
response.raise_for_status()
print(response)

request = prepare_grant_permission('_default', permission='sendToGroup', connection_id='someConnection')
response = client.send_request(request)
response.raise_for_status()
print(response)
