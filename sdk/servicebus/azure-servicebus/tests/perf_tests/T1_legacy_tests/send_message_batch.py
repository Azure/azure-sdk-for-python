# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._test_base import _SendTest

from azure_devtools.perfstress_tests import get_random_bytes

from azure.servicebus import BatchMessage


class LegacySendMessageBatchTest(_SendTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.data = get_random_bytes(self.args.message_size)

    def run_sync(self):
        messages = (self.data for _ in range(self.args.num_messages))
        batch = BatchMessage(messages)
        self.sender.send(batch)

    async def run_async(self):
        messages = (self.data for _ in range(self.args.num_messages))
        batch = BatchMessage(messages)
        await self.async_sender.send(batch)
