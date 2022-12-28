#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to demonstrate utilizing SAS (Shared Access Signature) tokens to authenticate with Event Hubs.
"""

import os
import time
import hmac
import hashlib
import base64
from urllib.parse import quote as url_parse_quote


from azure.core.credentials import AccessToken
from azure.eventhub import EventHubProducerClient, EventData


def generate_sas_token(uri: str, sas_name: str, sas_value: str, token_ttl: int) -> str:
    """Performs the signing and encoding needed to generate a sas token from a sas key."""
    sas = sas_value.encode('utf-8')
    expiry = str(int(time.time() + token_ttl))
    string_to_sign = (uri + '\n' + expiry).encode('utf-8')
    signed_hmac_sha256 = hmac.HMAC(sas, string_to_sign, hashlib.sha256)
    signature = url_parse_quote(base64.b64encode(signed_hmac_sha256.digest()))
    return f'SharedAccessSignature sr={uri}&sig={signature}&se={expiry}&skn={sas_name}'


class CustomizedSASCredential(object):
    def __init__(self, token: str, expiry: float) -> None:
        """
        :param str token: The token string
        :param float expiry: The epoch timestamp

        """
        self.token: str = token
        self.expiry: float = expiry
        self.token_type = b"servicebus.windows.net:sastoken"

    def get_token(self, *scopes, **kwargs):
        """
        This method is automatically called when token is about to expire.
        """
        return AccessToken(self.token, self.expiry)


# Target namespace and hub must also be specified.  Consumer group is set to default unless required otherwise.
FULLY_QUALIFIED_NAMESPACE: str = os.environ['EVENT_HUB_HOSTNAME']
EVENTHUB_NAME: str = os.environ['EVENT_HUB_NAME']

# The following part creates a SAS token. Users can use any way to create a SAS token.
SAS_POLICY: str = os.environ['EVENT_HUB_SAS_POLICY']
SAS_KEY: str = os.environ['EVENT_HUB_SAS_KEY']

uri: str = f"sb://{FULLY_QUALIFIED_NAMESPACE}/{EVENTHUB_NAME}"
token_ttl: int = 3000  # seconds
sas_token: str = generate_sas_token(uri, SAS_POLICY, SAS_KEY, token_ttl)
# end of creating a SAS token

producer_client: EventHubProducerClient = EventHubProducerClient(
    fully_qualified_namespace=FULLY_QUALIFIED_NAMESPACE,
    eventhub_name=EVENTHUB_NAME,
    credential=CustomizedSASCredential(sas_token, time.time() + token_ttl),
    logging_enable=True
)

start_time: float = time.time()
with producer_client:
    event_data_batch = producer_client.create_batch()
    event_data_batch.add(EventData('Single message'))
    producer_client.send_batch(event_data_batch)

print(f"Send messages in {time.time() - start_time} seconds.")
