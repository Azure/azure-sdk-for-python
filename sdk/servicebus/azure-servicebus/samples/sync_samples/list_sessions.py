#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""List sessions using both supported modes.

Default listing returns sessions with active messages or stored session state and excludes
sessions with neither. A cutoff returns only sessions whose stored state was set or updated
after that time.
"""

import os
from datetime import datetime, timedelta, timezone

from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient


FULLY_QUALIFIED_NAMESPACE = os.environ["SERVICEBUS_FULLY_QUALIFIED_NAMESPACE"]
SESSION_QUEUE_NAME = os.environ["SERVICEBUS_SESSION_QUEUE_NAME"]
TOPIC_NAME = os.environ["SERVICEBUS_TOPIC_NAME"]
SUBSCRIPTION_NAME = os.environ["SERVICEBUS_SUBSCRIPTION_NAME"]


def list_queue_sessions(servicebus_client):
    for session_id in servicebus_client.list_queue_sessions(SESSION_QUEUE_NAME):
        print("Queue session:", session_id)


def list_subscription_sessions(servicebus_client):
    for session_id in servicebus_client.list_subscription_sessions(
        TOPIC_NAME, SUBSCRIPTION_NAME
    ):
        print("Subscription session:", session_id)


def list_recently_updated_queue_sessions(servicebus_client):
    state_updated_after = datetime.now(timezone.utc) - timedelta(days=7)
    for session_id in servicebus_client.list_queue_sessions(
        SESSION_QUEUE_NAME, state_updated_after=state_updated_after
    ):
        print("Recently updated queue session:", session_id)


def main():
    with DefaultAzureCredential() as credential:
        with ServiceBusClient(
            FULLY_QUALIFIED_NAMESPACE, credential
        ) as servicebus_client:
            list_queue_sessions(servicebus_client)
            list_subscription_sessions(servicebus_client)
            list_recently_updated_queue_sessions(servicebus_client)


if __name__ == "__main__":
    main()
