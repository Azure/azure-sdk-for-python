# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import asyncio

from .perf_stress_runner import PerfStressRunner
from .perf_stress_test import PerfStressTest
from .random_stream import RandomStream, WriteStream, get_random_bytes
from .async_random_stream import AsyncRandomStream

__all__ = [
    "PerfStressRunner",
    "PerfStressTest",
    "RandomStream",
    "WriteStream",
    "AsyncRandomStream",
    "get_random_bytes"
]


def run_perfstress_cmd():
    main_loop = PerfStressRunner()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_loop.start())


def run_system_perfstress_tests_cmd():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    sys_test_dir = os.path.join(root_dir, 'system_perfstress')
    main_loop = PerfStressRunner(test_folder_path=sys_test_dir)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_loop.start())
