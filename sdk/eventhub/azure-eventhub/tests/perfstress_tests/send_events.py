# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from ._test_base import _SendTest


class SendEventsTest(_SendTest):
    def __init__(self, arguments):
        super().__init__(arguments)

    def run_batch_sync(self):
        if self.args.batch_size > 1:
            self.producer.send_batch(
                [self._build_event() for _ in range(self.args.batch_size)]
            )
        else:
            self.producer.send_event(self._build_event())
        return self.args.batch_size

    async def run_batch_async(self):
        if self.args.batch_size > 1:
            await self.async_producer.send_batch(
                [self._build_event() for _ in range(self.args.batch_size)]
            )
        else:
            await self.async_producer.send_event(self._build_event())
        return self.args.batch_size
