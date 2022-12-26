#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
An example to show authentication using AzureNamedKeyCredential.
"""

import os

from azure.core.credentials import AzureNamedKeyCredential
from azure.servicebus import ServiceBusClient, ServiceBusMessage


FULLY_QUALIFIED_NAMESPACE = os.environ['SERVICEBUS_FULLY_QUALIFIED_NAMESPACE']
QUEUE_NAME = os.environ["SERVICEBUS_QUEUE_NAME"]
SAS_POLICY = os.environ['SERVICEBUS_SAS_POLICY']
SERVICEBUS_SAS_KEY = os.environ['SERVICEBUS_SAS_KEY']


credential = AzureNamedKeyCredential(SAS_POLICY, SERVICEBUS_SAS_KEY)

with ServiceBusClient(FULLY_QUALIFIED_NAMESPACE, credential) as client:
    with client.get_queue_sender(QUEUE_NAME) as sender:
        sender.send_messages([ServiceBusMessage("hello")])
