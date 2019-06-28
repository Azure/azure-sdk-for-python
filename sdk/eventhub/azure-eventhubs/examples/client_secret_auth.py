#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
An example to show authentication using aad credentials
"""

import os
import time
import logging

from azure.eventhub import EventHubClient
from azure.eventhub import EventData
from azure.identity import ClientSecretCredential

import examples
logger = examples.get_logger(logging.INFO)


HOSTNAME = os.environ.get('EVENT_HUB_HOSTNAME')  # <mynamespace>.servicebus.windows.net
EVENT_HUB = os.environ.get('EVENT_HUB_NAME')

USER = os.environ.get('EVENT_HUB_SAS_POLICY')
KEY = os.environ.get('EVENT_HUB_SAS_KEY')

CLIENT_ID = os.environ.get('AAD_CLIENT_ID')
SECRET = os.environ.get('AAD_SECRET')
TENANT_ID = os.environ.get('AAD_TENANT_ID')


credential = ClientSecretCredential(client_id=CLIENT_ID, secret=SECRET, tenant_id=TENANT_ID)
client = EventHubClient(host=HOSTNAME,
                        event_hub_path=EVENT_HUB,
                        credential=credential)
try:
    producer = client.create_producer(partition_id='0')

    with producer:
        event = EventData(body='A single message')
        producer.send(event)

except KeyboardInterrupt:
    pass
except Exception as e:
    print(e)
