#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Examples to show how to create async EventHubProducerClient and EventHubConsumerClient that connect to custom endpoint.
"""

import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.identity import DefaultAzureCredential


FULLY_QUALIFIED_NAMESPACE = os.environ["SERVICEBUS_FULLY_QUALIFIED_NAMESPACE"]
QUEUE_NAME = os.environ["SERVICEBUS_QUEUE_NAME"]
# The custom endpoint address to use for establishing a connection to the Service Bus service,
# allowing network requests to be routed through any application gateways
# or other paths needed for the host environment.
CUSTOM_ENDPOINT_ADDRESS = "sb://<custom_endpoint_hostname>:<custom_endpoint_port>"
# The optional absolute path to the custom certificate file used by client to authenticate the
# identity of the connection endpoint in the case that endpoint has its own issued CA.
# If not set, the certifi library will be used to load certificates.
CUSTOM_CA_BUNDLE_PATH = "<your_custom_ca_bundle_file_path>"


def send_single_message(sender):
    message = ServiceBusMessage("Single Message")
    sender.send_messages(message)


credential = DefaultAzureCredential()
servicebus_client = ServiceBusClient(
    FULLY_QUALIFIED_NAMESPACE,
    credential,
    logging_enable=True,
    custom_endpoint_address=CUSTOM_ENDPOINT_ADDRESS,
    connection_verify=CUSTOM_CA_BUNDLE_PATH,
)
with servicebus_client:
    sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
    with sender:
        send_single_message(sender)
