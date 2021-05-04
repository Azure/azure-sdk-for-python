# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._test_base import _SendTest

from azure_devtools.perfstress_tests import get_random_bytes

from azure.eventhub import EventData


class LegacySendEventBatchTest(_SendTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.data = get_random_bytes(self.args.event_size)

    def data_generator(self):
        for i in range(self.args.num_events):
            yield self.data

    def run_sync(self):
        event = EventData(batch=self.data_generator())
        self.sender.send(event)

    async def run_async(self):
        event = EventData(batch=self.data_generator())
        await self.async_sender.send(event)