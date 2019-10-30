# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: blob_samples_network_activity_logging.py

DESCRIPTION:
    This example shows how to enable logging to console, using the storage
    library as an example. This sample expects that the
    `AZURE_STORAGE_CONNECTION_STRING` environment variable is set.
    It SHOULD NOT be hardcoded in any code derived from this sample.

USAGE: python blob_samples_network_activity_logging.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account

EXAMPLE OUTPUT:
Request with logging enabled and log level set to DEBUG.
... <logged network activity> ...
X containers.
Request with logging enabled and log level set to WARNING.
X containers.
"""

import logging

import os
import sys

from azure.storage.blob import BlobServiceClient

# Retrieve connection string from environment variables
# and construct a blob service client.
connection_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING', None)
if not connection_string:
    print('AZURE_STORAGE_CONNECTION_STRING required.')
    sys.exit(1)
service_client = BlobServiceClient.from_connection_string(connection_string)

# Retrieve a compatible logger and add a handler to send the output to console (STDOUT).
# Compatible loggers in this case include `azure` and `azure.storage`.
logger = logging.getLogger('azure.storage.blob')
logger.addHandler(logging.StreamHandler(stream=sys.stdout))

# Logging policy logs network activity at the DEBUG level. Set the level on the logger prior to the call.
logger.setLevel(logging.DEBUG)

# The logger level must be set to DEBUG, AND one of the following must be true:
# `logging_enable=True` passed as kwarg to the client constructor.
print("Request with logging enabled and log level set to DEBUG.")
containers = list(service_client.list_containers(logging_enable=True))
print("{} containers.".format(len(containers)))

logger.setLevel(logging.WARNING)
# Although logging is enabled, because the logger level is set to WARNING,
# no logs will be output.
print("Request with logging enabled and log level set to WARNING.")
containers = list(service_client.list_containers(logging_enable=True))
print("{} containers.".format(len(containers)))
