# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import time
import urllib
import hmac
import hashlib
import base64

class EventHubConfig:
    """
    A container class for event hub properties. Takes sb_name (service bus name),
    eh_name (event hub name), policy (SAS-policy),
    sas_key(SAS-key), consumer_group
    """
    def __init__(self, sb_name, eh_name, policy, sas_key, consumer_group):
        self.sb_name = sb_name
        self.eh_name = eh_name
        self.policy = policy
        self.sas_key = sas_key
        self.consumer_group = consumer_group
        self.client_address = self.get_client_address()
        self.rest_token = self.get_rest_token()
        

    def get_client_address(self):
        """
        Returns an auth token dictionary for making calls to eventhub
        REST API.
        """
        return ("amqps://{}:{}@{}.servicebus.windows.net:5671/{}"\
                .format(self.policy, self.sas_key, self.sb_name, self.eh_name))

    def get_rest_token(self):
        """
        Returns an auth token for making calls to eventhub REST API.
        """
        uri = urllib.parse.quote_plus("https://{}.servicebus.windows.net/{}" \
                                    .format(self.sb_name, self.eh_name))
        sas = self.sas_key.encode('utf-8')
        expiry = str(int(time.time() + 10000))
        string_to_sign = ('{}\n{}'.format(uri,expiry)).encode('utf-8')
        signed_hmac_sha256 = hmac.HMAC(sas, string_to_sign, hashlib.sha256)
        signature = urllib.parse.quote(base64.b64encode(signed_hmac_sha256.digest()))
        return 'SharedAccessSignature sr={}&sig={}&se={}&skn={}' \
                .format(uri, signature, expiry, self.policy)
                
