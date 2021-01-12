# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import asyncio

from ._test_base import _ReceiveTest


class LegacyReceiveMessageStreamTest(_ReceiveTest):
    def run_sync(self):
        count = 0
        if self.args.peeklock:
            for msg in self.receiver:
                if count >= self.args.num_messages:
                    break
                count += 1
                msg.complete()
        else:
            for msg in self.receiver:
                if count >= self.args.num_messages:
                    break
                count += 1

    async def run_async(self):
        count = 0
        if self.args.peeklock:
            async for msg in self.async_receiver:
                if count >= self.args.num_messages:
                    break
                count += 1
                await msg.complete()
        else:
            async for msg in self.async_receiver:
                if count >= self.args.num_messages:
                    break
                count += 1
