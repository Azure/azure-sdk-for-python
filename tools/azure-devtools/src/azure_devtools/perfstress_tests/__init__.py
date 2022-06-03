# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import asyncio

from ._perf_stress_runner import _PerfStressRunner
from ._perf_stress_test import PerfStressTest
from ._random_stream import RandomStream, WriteStream, get_random_bytes
from ._async_random_stream import AsyncRandomStream
from ._batch_perf_test import BatchPerfTest
from ._event_perf_test import EventPerfTest

__all__ = [
    "PerfStressTest",
    "BatchPerfTest",
    "EventPerfTest",
    "RandomStream",
    "WriteStream",
    "AsyncRandomStream",
    "get_random_bytes"
]


def run_perfstress_cmd():
    main_loop = _PerfStressRunner()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_loop.start())


def run_perfstress_debug_cmd():
    main_loop = _PerfStressRunner(debug=True)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_loop.start())


def run_system_perfstress_tests_cmd():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    sys_test_dir = os.path.join(root_dir, "system_perfstress")
    main_loop = _PerfStressRunner(test_folder_path=sys_test_dir, debug=True)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_loop.start())
