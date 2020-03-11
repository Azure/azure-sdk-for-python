# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: blob_samples_proxy_configuration.py

DESCRIPTION:
    This example shows how to work with a proxy, using the storage
    library as an example.

USAGE: python blob_samples_proxy_configuration.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account

EXAMPLE OUTPUT:
X containers.
"""

import logging

import os
import sys

from azure.storage.blob import BlobServiceClient
from azure.storage.blob._shared.base_client import create_configuration

# Retrieve connection string from environment variables
connection_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING', None)
if not connection_string:
    print('AZURE_STORAGE_CONNECTION_STRING required.')
    sys.exit(1)

# configure logging
logger = logging.getLogger('azure')
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
logger.setLevel(logging.DEBUG)

# TODO: Update this with your actual proxy information.
http_proxy = 'http://10.10.1.10:1180'
https_proxy = 'http://user:password@10.10.1.10:1180/'

# Create a storage Configuration object and update the proxy policy.
config = create_configuration(storage_sdk='blob')
config.proxy_policy.proxies = {
    'http': http_proxy,
    'https': https_proxy
}
# Construct the BlobServiceClient, including the customized configuation.
service_client = BlobServiceClient.from_connection_string(connection_string, _configuration=config)
containers = list(service_client.list_containers(logging_enable=True))
print("{} containers.".format(len(containers)))

# Alternatively, proxy settings can be set using environment variables, with no
# custom configuration necessary.
HTTP_PROXY_ENV_VAR = 'HTTP_PROXY'
HTTPS_PROXY_ENV_VAR = 'HTTPS_PROXY'
os.environ[HTTPS_PROXY_ENV_VAR] = https_proxy

service_client = BlobServiceClient.from_connection_string(connection_string)
containers = list(service_client.list_containers(logging_enable=True))
print("{} containers.".format(len(containers)))
