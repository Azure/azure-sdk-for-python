#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
An example to show authentication using AzureSasCredential.
"""

import os
import time
import hmac
import hashlib
import base64
import asyncio
try:
    from urllib.parse import quote as url_parse_quote
except ImportError:
    from urllib import pathname2url as url_parse_quote
from azure.core.credentials import AzureSasCredential

from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient


def generate_sas_token(uri, sas_name, sas_value, token_ttl):
    """Performs the signing and encoding needed to generate a sas token from a sas key."""
    sas = sas_value.encode('utf-8')
    expiry = str(int(time.time() + token_ttl))
    string_to_sign = (uri + '\n' + expiry).encode('utf-8')
    signed_hmac_sha256 = hmac.HMAC(sas, string_to_sign, hashlib.sha256)
    signature = url_parse_quote(base64.b64encode(signed_hmac_sha256.digest()))
    return 'SharedAccessSignature sr={}&sig={}&se={}&skn={}'.format(uri, signature, expiry, sas_name)


FULLY_QUALIFIED_NAMESPACE = os.environ['SERVICE_BUS_FULLY_QUALIFIED_NAMESPACE']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]
SAS_POLICY = os.environ['SERVICE_BUS_SAS_POLICY']
SERVICEBUS_SAS_KEY = os.environ['SERVICE_BUS_SAS_KEY']

auth_uri = "sb://{}/{}".format(FULLY_QUALIFIED_NAMESPACE, QUEUE_NAME)
token_ttl = 3000  # seconds

sas_token = generate_sas_token(auth_uri, SAS_POLICY, SERVICEBUS_SAS_KEY, token_ttl)


async def send_message():
    credential=AzureSasCredential(sas_token)
    async with ServiceBusClient(FULLY_QUALIFIED_NAMESPACE, credential) as client:
        async with client.get_queue_sender(QUEUE_NAME) as sender:
            await sender.send_messages([ServiceBusMessage("hello")])


start_time = time.time()
asyncio.run(send_message())
