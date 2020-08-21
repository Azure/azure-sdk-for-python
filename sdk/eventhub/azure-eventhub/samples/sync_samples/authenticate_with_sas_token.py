#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to demonstrate utilizing SAS (Shared Access Signature) tokens to authenticate with ServiceBus
"""

# pylint: disable=C0111

import time
import datetime
import os

from azure.core.credentials import AccessToken
from azure.eventhub import EventHubConsumerClient

# Caller must provide SAS credentials
SAS_TOKEN = os.environ['EVENT_HUB_SAS_TOKEN']

# Target namespace and hub must also be specified.  Consumer group is set to default unless required otherwise.
FULLY_QUALIFIED_NAMESPACE = os.environ['EVENT_HUB_HOSTNAME']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']
CONSUMER_GROUP = "$Default"

class CustomizedSASToken(object):
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
        If you need to update a token, call the above `update_token`
        """
        return AccessToken(self.token, self.expiry)


token_ttl = datetime.timedelta(seconds=300)

consumer_client = EventHubConsumerClient(
    fully_qualified_namespace=FULLY_QUALIFIED_NAMESPACE,
    eventhub_name=EVENTHUB_NAME,
    consumer_group=CONSUMER_GROUP,
    credential=CustomizedSASToken(SAS_TOKEN, time.time() + token_ttl.seconds),
    logging_enable=True
)

with consumer_client:
    consumer_client.receive(
        lambda pc, event: print(pc.partition_id, ":", event),
        starting_position=-1
    )
