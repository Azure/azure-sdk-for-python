# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from ._test_base import _SendTest


class SendEventBatchTest(_SendTest):
    def __init__(self, arguments):
        super().__init__(arguments)

    def run_batch_sync(self):
        batch = self.producer.create_batch()
        for _ in range(self.args.batch_size):
            batch.add(self._build_event())
        self.producer.send_batch(batch)
        return self.args.batch_size

    async def run_batch_async(self):
        batch = await self.async_producer.create_batch()
        for _ in range(self.args.batch_size):
            batch.add(self._build_event())
        await self.async_producer.send_batch(batch)
        return self.args.batch_size
