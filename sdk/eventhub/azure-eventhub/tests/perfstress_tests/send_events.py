# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._test_base import _SendTest

from azure_devtools.perfstress_tests import get_random_bytes

from azure.eventhub import EventData


class SendEventsTest(_SendTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.data = get_random_bytes(self.args.event_size)

    def run_batch_sync(self):
        if self.args.batch_size > 1:
            self.producer.send_batch(
                [EventData(self.data) for _ in range(self.args.batch_size)]
            )
        else:
            self.producer.send_event(EventData(self.data))
        return self.args.batch_size

    async def run_batch_async(self):
        if self.args.batch_size > 1:
            await self.async_producer.send_batch(
                [EventData(self.data) for _ in range(self.args.batch_size)]
            )
        else:
            await self.async_producer.send_event(EventData(self.data))
        return self.args.batch_size
