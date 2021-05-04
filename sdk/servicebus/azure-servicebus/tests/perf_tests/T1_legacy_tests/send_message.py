# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._test_base import _SendTest

from azure_devtools.perfstress_tests import get_random_bytes

from azure.servicebus import Message
from azure.servicebus.aio import Message as AsyncMessage


class LegacySendMessageTest(_SendTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.data = get_random_bytes(self.args.message_size)

    def run_sync(self):
        message = Message(self.data)
        self.sender.send(message)

    async def run_async(self):
        message = AsyncMessage(self.data)
        await self.async_sender.send(message)
