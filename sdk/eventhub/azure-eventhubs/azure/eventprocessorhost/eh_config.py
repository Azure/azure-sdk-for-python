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
    A container class for Event Hub properties.

    :param sb_name: The EventHub (ServiceBus) namespace.
    :type sb_name: str
    :param eh_name: The EventHub name.
    :type eh_name: str
    :param policy: The SAS policy name.
    :type policy: str
    :param sas_key: The SAS access key.
    :type sas_key: str
    :param consumer_group: The EventHub consumer group to receive from. The
     default value is '$default'.
    :type consumer_group: str
    :param namespace_suffix: The ServiceBus namespace URL suffix.
     The default value is 'servicebus.windows.net'.
    :type namespace_suffix: str
    """
    def __init__(self, sb_name, eh_name, policy, sas_key,
                 consumer_group="$default",
                 namespace_suffix="servicebus.windows.net"):
        self.sb_name = sb_name
        self.eh_name = eh_name
        self.policy = policy
        self.sas_key = sas_key
        self.namespace_suffix = namespace_suffix
        self.consumer_group = consumer_group
        self.client_address = self.get_client_address()
        self.rest_token = self.get_rest_token()

    def get_client_address(self):
        """
        Returns an auth token dictionary for making calls to eventhub
        REST API.

        :rtype: str
        """
        return "amqps://{}:{}@{}.{}:5671/{}".format(
            urllib.parse.quote_plus(self.policy),
            urllib.parse.quote_plus(self.sas_key),
            self.sb_name,
            self.namespace_suffix,
            self.eh_name)

    def get_rest_token(self):
        """
        Returns an auth token for making calls to eventhub REST API.

        :rtype: str
        """
        uri = urllib.parse.quote_plus(
            "https://{}.{}/{}".format(self.sb_name, self.namespace_suffix, self.eh_name))
        sas = self.sas_key.encode('utf-8')
        expiry = str(int(time.time() + 10000))
        string_to_sign = ('{}\n{}'.format(uri, expiry)).encode('utf-8')
        signed_hmac_sha256 = hmac.HMAC(sas, string_to_sign, hashlib.sha256)
        signature = urllib.parse.quote(base64.b64encode(signed_hmac_sha256.digest()))
        return 'SharedAccessSignature sr={}&sig={}&se={}&skn={}' \
                .format(uri, signature, expiry, self.policy)
