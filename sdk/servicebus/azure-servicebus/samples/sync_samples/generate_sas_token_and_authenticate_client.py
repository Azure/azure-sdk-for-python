#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
An example to show authentication using a SAS token generated from a SAS key, as well as the generation process.
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
from azure.core.credentials import AccessToken

from azure.servicebus import ServiceBusClient

def generate_sas_token(uri, sas_name, sas_value, token_ttl):
    """Performs the signing and encoding needed to generate a sas token from a sas key."""
    sas = sas_value.encode('utf-8')
    expiry = str(int(time.time() + token_ttl))
    string_to_sign = (uri + '\n' + expiry).encode('utf-8')
    signed_hmac_sha256 = hmac.HMAC(sas, string_to_sign, hashlib.sha256)
    signature = url_parse_quote(base64.b64encode(signed_hmac_sha256.digest()))
    return 'SharedAccessSignature sr={}&sig={}&se={}&skn={}'.format(uri, signature, expiry, sas_name)

class CustomizedSASCredential(object):
    def __init__(self, token, expiry):
        """
        :param str token: The token string
        :param float expiry: The epoch timestamp
        """
        self.token = token
        self.expiry = expiry
        self.token_type = b"servicebus.windows.net:sastoken"

    def get_token(self, *scopes, **kwargs):
        """
        This method is automatically called when token is about to expire.
        """
        return AccessToken(self.token, self.expiry)

FULLY_QUALIFIED_NAMESPACE = os.environ['SERVICE_BUS_FULLY_QUALIFIED_NAMESPACE']
SESSION_QUEUE_NAME = os.environ["SERVICE_BUS_SESSION_QUEUE_NAME"]
SAS_POLICY = os.environ['SERVICE_BUS_SAS_POLICY']
SAS_KEY = os.environ['SERVICE_BUS_SAS_KEY']

auth_uri = "sb://{}/{}".format(FULLY_QUALIFIED_NAMESPACE, SESSION_QUEUE_NAME)
token_ttl = 3000  # seconds

sas_token = generate_sas_token(auth_uri, SAS_POLICY, SAS_KEY, token_ttl)

credential=CustomizedSASCredential(sas_token, time.time() + token_ttl)

with ServiceBusClient(FULLY_QUALIFIED_NAMESPACE, credential) as client:
    pass # client now connected, your logic goes here.
