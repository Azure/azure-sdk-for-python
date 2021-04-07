# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._test_base import _ReceiveTest


class ReceiveEventBatchTest(_ReceiveTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self._total_received_cnt = 0
        self._async_total_received_cnt = 0

    def _on_event_batch_received(self, partition_context, event_batch):
        self._total_received_cnt += len(event_batch)
        if self._total_received_cnt >= self.args.num_events:
            self.consumer.close()

    async def _on_event_batch_received_async(self, partition_context, event_batch):
        self._async_total_received_cnt += len(event_batch)
        if self._async_total_received_cnt >= self.args.num_events:
            await self.async_consumer.close()

    def run_sync(self):
        self._total_received_cnt = 0
        self.consumer.receive_batch(
            on_event_batch=self._on_event_batch_received,
            max_batch_size=self.args.num_events,
            max_wait_time=self.args.max_wait_time,
            starting_position="-1",
        )

    async def run_async(self):
        self._async_total_received_cnt = 0
        await self.async_consumer.receive_batch(
            on_event_batch=self._on_event_batch_received_async,
            max_batch_size=self.args.num_events,
            max_wait_time=self.args.max_wait_time,
            starting_position="-1",
        )
