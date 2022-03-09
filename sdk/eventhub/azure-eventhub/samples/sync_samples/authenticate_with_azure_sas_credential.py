#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to demonstrate utilizing azure.core.credentials.AzureSasCredential to authenticate with Event Hubs.
"""

import os
import time
import hmac
import hashlib
import base64
try:
    from urllib.parse import quote as url_parse_quote
except ImportError:
    from urllib import pathname2url as url_parse_quote

from azure.core.credentials import AzureSasCredential
from azure.eventhub import EventHubProducerClient, EventData


def generate_sas_token(uri, sas_name, sas_value, token_ttl):
    """Performs the signing and encoding needed to generate a sas token from a sas key."""
    sas = sas_value.encode('utf-8')
    expiry = str(int(time.time() + token_ttl))
    string_to_sign = (uri + '\n' + expiry).encode('utf-8')
    signed_hmac_sha256 = hmac.HMAC(sas, string_to_sign, hashlib.sha256)
    signature = url_parse_quote(base64.b64encode(signed_hmac_sha256.digest()))
    return 'SharedAccessSignature sr={}&sig={}&se={}&skn={}'.format(uri, signature, expiry, sas_name)


# Target namespace and hub must also be specified.  Consumer group is set to default unless required otherwise.
FULLY_QUALIFIED_NAMESPACE = os.environ['EVENT_HUB_HOSTNAME']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']

# The following part creates a SAS token. A SAS token is typically given to you after being created.
SAS_POLICY = os.environ['EVENT_HUB_SAS_POLICY']
SAS_KEY = os.environ['EVENT_HUB_SAS_KEY']

uri = "sb://{}/{}".format(FULLY_QUALIFIED_NAMESPACE, EVENTHUB_NAME)
token_ttl = 3000  # seconds
sas_token = generate_sas_token(uri, SAS_POLICY, SAS_KEY, token_ttl)

credential = AzureSasCredential(sas_token)

producer_client = EventHubProducerClient(
    fully_qualified_namespace=FULLY_QUALIFIED_NAMESPACE,
    eventhub_name=EVENTHUB_NAME,
    credential=credential,
    logging_enable=True
)

start_time = time.time()
with producer_client:
    event_data_batch = producer_client.create_batch()
    event_data_batch.add(EventData('Single message'))
    producer_client.send_batch(event_data_batch)

print("Send messages in {} seconds.".format(time.time() - start_time))
