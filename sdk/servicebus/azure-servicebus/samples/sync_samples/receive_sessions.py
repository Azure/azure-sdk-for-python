#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show browsing sessions.
"""

import os
from azure.servicebus import ServiceBusClient
from azure.identity import DefaultAzureCredential

FULLY_QUALIFIED_NAMESPACE = os.environ["SERVICEBUS_FULLY_QUALIFIED_NAMESPACE"]
QUEUE_NAME = os.environ["SERVICEBUS_SESSION_QUEUE_NAME"]

credential = DefaultAzureCredential()
servicebus_client = ServiceBusClient(FULLY_QUALIFIED_NAMESPACE, credential, logging_enable=True, retry_total=0, uamqp_transport=True)

with servicebus_client:
    receiver = servicebus_client.get_management_operation_client(entity_name=QUEUE_NAME)
    with receiver:
        sessions = receiver.get_sessions(max_num_sessions=2)
        for session in sessions:
            print(str(session))
