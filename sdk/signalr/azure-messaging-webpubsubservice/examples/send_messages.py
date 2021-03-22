import os

from azure.core.credentials import AzureKeyCredential
from azure.messaging.webpubsubservice import WebPubSubServiceClient
from azure.messaging.webpubsubservice.rest import *

endpoint = os.environ['ENDPOINT']
api_key = os.environ['API_KEY']

client = WebPubSubServiceClient(endpoint, credential=AzureKeyCredential(api_key))

request = prepare_send_to_all('skalman', 'Hello, all!', content_type='application/json')
response = client.send_request(request)
response.raise_for_status()
print(response)

request = prepare_add_user_to_group('skalman', group='someGroup', user_id='me')
response = client.send_request(request)
response.raise_for_status()
print(response)

request = prepare_grant_permission('skalman', permission='sendToGroup', connection_id='someConnection')
response = client.send_request(request)
response.raise_for_status()
print(response)
