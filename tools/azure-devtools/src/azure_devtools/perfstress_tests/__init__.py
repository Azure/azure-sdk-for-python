# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import asyncio

from .perf_stress_runner import PerfStressRunner
from .perf_stress_test import PerfStressTest
from .random_stream import RandomStream
from .async_random_stream import AsyncRandomStream

__all__ = [
    "PerfStressRunner",
    "PerfStressTest",
    "RandomStream",
    "AsyncRandomStream"
]


def run_perfstress_cmd():
    main_loop = PerfStressRunner()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_loop.start())
