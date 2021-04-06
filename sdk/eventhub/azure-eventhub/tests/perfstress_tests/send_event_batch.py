# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._test_base import _SendTest

from azure_devtools.perfstress_tests import get_random_bytes

from azure.eventhub import EventData


class SendEventBatchTest(_SendTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.data = get_random_bytes(self.args.event_size)
        self.to_send_event_data_batches = []

    def run_sync(self):
        batch = self.producer.create_batch()
        for _ in range(self.args.num_events):
            try:
                batch.add(EventData(self.data))
            except ValueError:
                # Batch full
                self.producer.send_batch(batch)
                batch = self.producer.create_batch()
                batch.add(EventData(self.data))
        self.producer.send_batch(batch)

    async def run_async(self):
        batch = await self.async_producer.create_batch()
        for _ in range(self.args.num_events):
            try:
                batch.add(EventData(self.data))
            except ValueError:
                # Batch full
                await self.async_producer.send_batch(batch)
                batch = await self.async_producer.create_batch()
                batch.add(EventData(self.data))
        await self.async_producer.send_batch(batch)
