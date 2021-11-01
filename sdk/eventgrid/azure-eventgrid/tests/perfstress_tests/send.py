#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import asyncio
from azure_devtools.perfstress_tests import PerfStressTest

from azure.eventgrid import EventGridPublisherClient as SyncPublisherClient, EventGridEvent
from azure.eventgrid.aio import EventGridPublisherClient as AsyncPublisherClient

from azure.core.credentials import AzureKeyCredential

class EventGridPerfTest(PerfStressTest):
    def __init__(self, arguments):
        super().__init__(arguments)

        # auth configuration
        topic_key = self.get_from_env("EG_ACCESS_KEY")
        endpoint = self.get_from_env("EG_TOPIC_HOSTNAME")

        # Create clients
        self.publisher_client = SyncPublisherClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(topic_key)
        )
        self.async_publisher_client = AsyncPublisherClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(topic_key)
        )

        self.event_list = []
        for _ in range(self.args.num_events):
            self.event_list.append(EventGridEvent(
                event_type="Contoso.Items.ItemReceived",
                data={
                    "services": ["EventGrid", "ServiceBus", "EventHubs", "Storage"]
                },
                subject="Door1",
                data_version="2.0"
            ))

    async def close(self):
        """This is run after cleanup.
        
        Use this to close any open handles or clients.
        """
        await self.async_publisher_client.close()
        await super().close()

    def run_sync(self):
        """The synchronous perf test.
        
        Try to keep this minimal and focused. Using only a single client API.
        Avoid putting any ancilliary logic (e.g. generating UUIDs), and put this in the setup/init instead
        so that we're only measuring the client API call.
        """
        self.publisher_client.send(self.event_list)

    async def run_async(self):
        """The asynchronous perf test.
        
        Try to keep this minimal and focused. Using only a single client API.
        Avoid putting any ancilliary logic (e.g. generating UUIDs), and put this in the setup/init instead
        so that we're only measuring the client API call.
        """
        await self.async_publisher_client.send(self.event_list)

    @staticmethod
    def add_arguments(parser):
        super(EventGridPerfTest, EventGridPerfTest).add_arguments(parser)
        parser.add_argument('-n', '--num-events', nargs='?', type=int, help='Number of events to be sent. Defaults to 100', default=100)
