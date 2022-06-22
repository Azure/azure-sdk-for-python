# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import time
import os

from azure.core.utils import parse_connection_string
from uamqp.client import ReceiveClient
from uamqp.async_ops.client_async import ReceiveClientAsync
from uamqp import authentication

from azure_devtools.perfstress_tests import EventPerfTest


class UamqpReceiveEventTest(EventPerfTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        live_eventhub_config = self._get_eh_connection_config()
        uri = "{}{}".format(live_eventhub_config['hostname'], live_eventhub_config['event_hub'])
        source = "{}{}/ConsumerGroups/{}/Partitions/{}".format(
            live_eventhub_config['hostname'],
            live_eventhub_config['event_hub'],
            live_eventhub_config['consumer_group'],
            live_eventhub_config['partition']).replace("sb://", "amqps://")

        # Setup service clients
        self.receive_client = ReceiveClient(
            source,
            auth=authentication.SASTokenAuth.from_shared_access_key(
                uri,
                live_eventhub_config['key_name'],
                live_eventhub_config['access_key']
            ),
            timeout=0,
            debug=False
        )
        self.async_receive_client = ReceiveClientAsync(
            source,
            auth=authentication.SASTokenAsync.from_shared_access_key(
                uri,
                live_eventhub_config['key_name'],
                live_eventhub_config['access_key']
            ),
            timeout=0,
            debug=False
        )
    def _get_eh_connection_config(self):
        connection_string = self.get_from_env("AZURE_EVENTHUB_CONNECTION_STRING")
        auth_info = parse_connection_string(connection_string)
        config = {}
        config['hostname'] = auth_info['endpoint']
        config['event_hub'] = self.get_from_env("AZURE_EVENTHUB_NAME")
        config['key_name'] = auth_info['sharedaccesskeyname']
        config['access_key'] = auth_info['sharedaccesskey']
        config['consumer_group'] = "$Default"
        config['partition'] = "0"
        return config
        
    def process_event_sync(self, message):
        try:
            message.annotations
            message.properties
            message.get_data()
            message.header
            message.delivery_annotations
            self.event_raised_sync()
        except Exception as e:
            self.error_raised_sync(e)

    def start_events_sync(self) -> None:
        """
        Start the process for receiving events.
        """
        self.receive_client.receive_messages(self.process_event_sync)

    def stop_events_sync(self) -> None:
        """
        Stop the process for receiving events.
        """
        self.receive_client.close()

    async def start_events_async(self) -> None:
        """
        Start the process for receiving events.
        """
        await self.async_receive_client.receive_messages_async(self.process_event_sync)

    async def stop_events_async(self) -> None:
        """
        Stop the process for receiving events.
        """
        await self.async_receive_client.close_async()
