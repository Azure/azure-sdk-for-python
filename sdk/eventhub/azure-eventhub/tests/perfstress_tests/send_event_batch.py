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
        self._preload_event_data_batches()

    def _preload_event_data_batches(self):
        batch = self.producer.create_batch()
        for _ in range(self.args.num_events):
            try:
                batch.add(EventData(self.data))
            except ValueError:
                # Batch full
                self.to_send_event_data_batches.append(batch)
                batch = self.producer.create_batch()
                batch.add(EventData(self.data))
        self.to_send_event_data_batches.append(batch)

    def run_sync(self):
        for event_data_batch in self.to_send_event_data_batches:
            self.producer.send_batch(event_data_batch)

    async def run_async(self):
        for event_data_batch in self.to_send_event_data_batches:
            await self.async_producer.send_batch(event_data_batch)
