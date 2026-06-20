# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._batch_perf_test import BatchPerfTest


class PerfStressTest(BatchPerfTest):

    def run_batch_sync(self) -> int:
        self.run_sync()
        return 1

    async def run_batch_async(self) -> int:
        await self.run_async()
        return 1

    def run_sync(self) -> None:
        raise NotImplementedError("run_sync must be implemented for {}".format(self.__class__.__name__))

    async def run_async(self) -> None:
        raise NotImplementedError("run_async must be implemented for {}".format(self.__class__.__name__))
