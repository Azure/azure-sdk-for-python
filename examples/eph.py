# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import logging
import asyncio
import time
import urllib
import hmac
import hashlib
import base64
from eventprocessorhost.abstract_event_processor import AbstractEventProcessor
from eventprocessorhost.azure_storage_checkpoint_manager import AzureStorageCheckpointLeaseManager
from eventprocessorhost.eph import EventProcessorHost

import examples
logger = examples.get_logger(logging.INFO)

class EventProcessor(AbstractEventProcessor):
    """
    Example Implmentation of AbstractEventProcessor
    """
    def __init__(self):
        """
        Init Event processor
        """
        self._msg_counter = 0
    async def open_async(self, context):
        """
        Called by processor host to initialize the event processor.
        """
        logger.info("Connection established %s", context.partition_id)

    async def close_async(self, context, reason):
        """
        Called by processor host to indicate that the event processor is being stopped.
        (Params) Context:Information about the partition
        """
        logger.info("Connection closed (reason %s, id %s, offset %s, sq_number %s)", reason,
                     context.partition_id, context.offset, context.sequence_number)

    async def process_events_async(self, context, messages):
        """
        Called by the processor host when a batch of events has arrived.
        This is where the real work of the event processor is done.
        (Params) Context: Information about the partition, Messages: The events to be processed.
        """
        logger.info("Events processed %s %s", context.partition_id, messages)
        await context.checkpoint_async()

    async def process_error_async(self, context, error):
        """
        Called when the underlying client experiences an error while receiving.
        EventProcessorHost will take care of recovering from the error and
        continuing to pump messages,so no action is required from
        (Params) Context: Information about the partition, Error: The error that occured.
        """
        logger.error("Event Processor Error %s ", repr(error))
        await context.host.close_async()

def generate_eh_rest_credentials(sb_name, eh_name, key_name, sas_token):
    """
    Returns an auth token dictionary for making calls to eventhub
    REST API.
    """
    uri = urllib.parse.quote_plus("https://{}.servicebus.windows.net/{}" \
                                  .format(sb_name, eh_name))
    sas = sas_token.encode('utf-8')
    expiry = str(int(time.time() + 10000))
    string_to_sign = ('{}\n{}'.format(uri,expiry)).encode('utf-8')
    signed_hmac_sha256 = hmac.HMAC(sas, string_to_sign, hashlib.sha256)
    signature = urllib.parse.quote(base64.b64encode(signed_hmac_sha256.digest()))
    return  {"sb_name": sb_name,
             "eh_name": eh_name,
             "token":'SharedAccessSignature sr={}&sig={}&se={}&skn={}' \
                     .format(uri, signature, expiry, key_name)
            }


try:
    # Storage Account Credentials
    STORAGE_ACCOUNT_NAME = "mystorageaccount"
    STORAGE_KEY = "sas encoded storage key"
    LEASE_CONTAINER_NAME = "leases"

    # Eventhub client address and consumer group
    ADDRESS = ("amqps://"
               "<URL-encoded-SAS-policy>"
               ":"
               "<URL-encoded-SAS-key>"
               "@"
               "<mynamespace>.servicebus.windows.net"
               "/"
               "myeventhub")

    CONSUMER_GROUP = "$default"

    # Generate Auth credentials for EH Rest API (Used to list of partitions)
    EH_REST_CREDENTIALS = generate_eh_rest_credentials('<mynamespace>',
                                                       '<myeventhub>',
                                                       '<URL-encoded-SAS-policy>',
                                                       '<URL-encoded-SAS-key>')

    STORAGE_MANAGER = AzureStorageCheckpointLeaseManager(STORAGE_ACCOUNT_NAME, STORAGE_KEY,
                                                         LEASE_CONTAINER_NAME)

    LOOP = asyncio.get_event_loop()

    HOST = EventProcessorHost(EventProcessor, ADDRESS, CONSUMER_GROUP,
                              STORAGE_MANAGER, EH_REST_CREDENTIALS, loop=LOOP)

    LOOP.run_until_complete(HOST.open_async())
    LOOP.run_until_complete(HOST.close_async())

finally:
    LOOP.stop()
