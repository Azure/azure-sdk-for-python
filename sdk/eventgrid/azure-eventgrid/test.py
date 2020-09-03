from azure.eventgrid import  CloudEvent, EventGridPublisherClient
from azure.eventgrid._generated.models import CloudEvent as ICL
# from cloudevents.http import from_http, to_binary, to_structured
from azure.core.credentials import AzureKeyCredential
import os
import json
# c = CloudEvent(
#     {'source':'MyApp',
#     'type':'CreateStuff'},
#     'asasa'
# )  # specversion is set by default to "1.0"

# c = CloudEvent(
#     id=12,
#     source='MyApp',
#     type='CreateStuff'
# )  

# c ={
#     'source':'sdsda',
#     'id':'asas',
#     'specversion':'1.0',
#     'type':'dsdsd'
# }

key = "iT/OY/ZGqMi3d78DueblHkRgKVA0VLH8IGcdAYjHJAM="
topic_hostname = "https://rakshith-cloud.westus2-1.eventgrid.azure.net"
credential = AzureKeyCredential(key)
client = EventGridPublisherClient(topic_hostname, credential)


c = CloudEvent(
                source = "http://samplesource.dev",
                data = "cloudevent",
                type="Sample.Cloud.Event",
                jaja="sadf",
                reasonCode="asdf"
                )

print(json.dumps(c.__dict__))

# class A():
#     def __init__(self, a, b, **kwargs):
#         self.a = a
#         self.b = b
#         self.c = kwargs.get('c', None)
        

# a = A(1, 2, c=3, d=4)
# print(a.__dict__)