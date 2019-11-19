#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
An example to show authentication using aad credentials
"""

import os
from azure.eventhub import EventData, EventHubProducerClient
from azure.identity import EnvironmentCredential


fully_qualified_namespace = os.environ['EVENT_HUB_HOSTNAME']
eventhub_name = os.environ['EVENT_HUB_NAME']


credential = EnvironmentCredential()
producer = EventHubProducerClient(fully_qualified_namespace=fully_qualified_namespace,
                                  eventhub_name=eventhub_name,
                                  credential=credential)

with producer:
    event = EventData(body='A single message')
    producer.send(event, partition_id='0')
