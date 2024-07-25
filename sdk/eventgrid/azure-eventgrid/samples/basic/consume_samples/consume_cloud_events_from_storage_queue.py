# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: consume_cloud_events_from_storage_queue.py
DESCRIPTION:
    These samples demonstrate receiving events from a Storage Queue.
USAGE:
    python consume_cloud_events_from_storage_queue.py
    Set the environment variables with your own values before running the sample:
    1) STORAGE_QUEUE_CONN_STR: The connection string to the Storage account
    3) STORAGE_QUEUE_NAME: The name of the storage queue.
"""
from typing import List
from azure.core.messaging import CloudEvent
from azure.storage.queue import QueueServiceClient, BinaryBase64DecodePolicy
from azure.identity import DefaultAzureCredential
import os
import json

# all types of CloudEvents below produce same DeserializedEvent
queue_name = os.environ["STORAGE_QUEUE_NAME"]
queue_account_url = os.environ["STORAGE_QUEUE_ACCOUNT_URL"]

with QueueServiceClient(queue_account_url, DefaultAzureCredential()) as qsc:
    payload = qsc.get_queue_client(queue=queue_name, message_decode_policy=BinaryBase64DecodePolicy()).peek_messages(
        max_messages=32
    )

    ## deserialize payload into a list of typed Events
    events: List[CloudEvent] = [CloudEvent.from_json(msg) for msg in payload]

    for event in events:
        print(type(event))  ## CloudEvent
