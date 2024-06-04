# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: network_activity_logging.py

DESCRIPTION:
    This example shows how to enable logging to console, using the storage
    library as an example. This sample expects that the
    `AZURE_STORAGE_CONNECTION_STRING` environment variable is set.
    It SHOULD NOT be hardcoded in any code derived from this sample.

USAGE: python network_activity_logging.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account

EXAMPLE OUTPUT:
Request with logging enabled and log level set to DEBUG.
Queue test
... <logged network activity> ...
  Message: b'here is a message'
  Message: Here is a non-base64 encoded message.
"""

import base64
import binascii
import logging

import os
import sys

from azure.storage.queue import QueueServiceClient

# Retrieve connection string from environment variables
# and construct a blob service client.
connection_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING', None)
if not connection_string:
    print('AZURE_STORAGE_CONNECTION_STRING required.')
    sys.exit(1)
service_client = QueueServiceClient.from_connection_string(connection_string)

# Retrieve a compatible logger and add a handler to send the output to console (STDOUT).
# Compatible loggers in this case include `azure` and `azure.storage`.
logger = logging.getLogger('azure.storage.queue')
logger.addHandler(logging.StreamHandler(stream=sys.stdout))

# Logging policy logs network activity at the DEBUG level. Set the level on the logger prior to the call.
logger.setLevel(logging.DEBUG)

# The logger level must be set to DEBUG, AND the following must be true:
# `logging_enable=True` passed as kwarg to the client constructor OR the API call
print('Request with logging enabled and log level set to DEBUG.')
queues = service_client.list_queues(logging_enable=True)
for queue in queues:
    print('Queue: {}'.format(queue.name))
    queue_client = service_client.get_queue_client(queue.name)
    messages = queue_client.peek_messages(max_messages=20, logging_enable=True)
    for message in messages:
        try:
            print('  Message: {!r}'.format(base64.b64decode(message.content)))
        except binascii.Error:
            print('  Message: {}'.format(message.content))
