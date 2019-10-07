# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import logging
import sys
import os

from azure.servicebus import TopicClient
from azure.servicebus import Message


def get_logger(level):
    azure_logger = logging.getLogger("azure")
    if not azure_logger.handlers:
        azure_logger.setLevel(level)
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s'))
        azure_logger.addHandler(handler)

    uamqp_logger = logging.getLogger("uamqp")
    if not uamqp_logger.handlers:
        uamqp_logger.setLevel(logging.INFO)
        uamqp_logger.addHandler(handler)
    return azure_logger


logger = get_logger(logging.DEBUG)
connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']


if __name__ == '__main__':

    topic_client = TopicClient.from_connection_string(connection_str, name="pytopic", debug=False)
    with topic_client.get_sender() as sender:
        message = Message(b"sample topic message")
        sender.send(message)
