# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import asyncio
import time
import queue
from typing import List
import multiprocessing
import threading
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import importlib

from ._perf_stress_base import _PerfTestABC, _PerfTestBase


def run_process(index, args, module, test_name, num_tests, test_stages, results, status):
    """The child process main function.

    Here we load the test class from the correct module and start it.
    """
    test_module = importlib.import_module(module)
    test_class = getattr(test_module, test_name)
    value = asyncio.run(_start_tests(index, test_class, num_tests, args, test_stages, results, status))
    return value


def _synchronize(stages, ignore_error=False):
    """Synchronize all processes by waiting on the barrier.

    Optionally we can also ignore a broken barrier during the cleanup stages
    so that if some processes have failed, the others can still complete cleanup.
    """
    try:
        stages.wait()
    except threading.BrokenBarrierError:
        if not ignore_error:
            raise

async def _start_tests(index, test_class, num_tests, args, test_stages, results, status):
    """Create test classes, run setup, tests and cleanup."""
    # Create all parallel tests with a global unique index value
    tests = []

    try:
        with _PerfTestBase._global_parallel_index_lock:
            _PerfTestBase._global_parallel_index = index
            tests = [test_class(args) for _ in range(num_tests)]

        # Run the global setup once per process.
        await tests[0].global_setup()

        # Waiting till all processes are ready to start "Setup". This allows each child
        # process to setup any global resources before the rest of setup is run.
        _synchronize(test_stages["Setup"])
        await asyncio.gather(*[test.setup() for test in tests])

        # Waiting till all processes are ready to start "Post Setup"
        _synchronize(test_stages["Post Setup"])
        await asyncio.gather(*[test.post_setup() for test in tests])

        if args.warmup:
            # Waiting till all processes are ready to start "Warmup"
            _synchronize(test_stages["Warmup"])
            await _run_tests(args.warmup, args, tests, results, status, with_profiler=False)

        # Waiting till all processes are ready to start "Tests"
        _synchronize(test_stages["Tests"])
        await _run_tests(args.duration, args, tests, results, status, with_profiler=args.profile)

        # Waiting till all processes have finished tests, ready to start "Pre Cleanup"
        _synchronize(test_stages["Pre Cleanup"])
    except threading.BrokenBarrierError:
        # A separate process has failed, so all of them are shutting down.
        print("Another test process has aborted - shutting down.")
    except Exception as e:
        print(f"Test processes failed - aborting. Error: {e}")
        for barrier in test_stages.values():
            barrier.abort()
    finally:
        try:
            # We'll attempt to clean up the tests using the barrier.
            # This may fail if the tests are already in an unrecoverable error state.
            # If one process has failed, we'll still attempt to clean up without the barrier.
            await asyncio.gather(*[test.pre_cleanup() for test in tests])
            if not args.no_cleanup:
                # Waiting till all processes are ready to start "Cleanup"
                # If any process has failed earlier, the barrier will be broken - so wait
                # if we can but otherwise attempt to clean up anyway.
                _synchronize(test_stages["Cleanup"], ignore_error=True)
                await asyncio.gather(*[test.cleanup() for test in tests])

            # Waiting till all processes have completed the cleanup stages.
            _synchronize(test_stages["Finished"], ignore_error=True)
            if not args.no_cleanup:
                # Run global cleanup once per process.
                await tests[0].global_cleanup()
        except Exception as e:
            # Tests were unable to clean up, maybe due to earlier failure state.
            print(f"Failed to cleanup up tests: {e}")
        finally:
            # Always call close on the tests, even if cleanup failed.
            try:
                await asyncio.gather(*[test.close() for test in tests])
            except Exception as e:
                print(f"Failed to close tests: {e}")


async def _run_tests(duration: int, args, tests, results, status, *, with_profiler: bool = False) -> None:
    """Run the listed tests either in parallel asynchronously or in a thread pool."""
    # Kick of a status monitoring thread.
    stop_status = threading.Event()
    status_thread = threading.Thread(
        target=_report_status,
        args=(status, tests, stop_status),
        daemon=True)
    status_thread.start()

    try:
        if args.sync:
            with ThreadPoolExecutor(max_workers=args.parallel) as ex:
                tasks = [ex.submit(test.run_all_sync, duration, run_profiler=with_profiler) for test in tests]
                wait(tasks, return_when=ALL_COMPLETED)
        else:
            tasks = [asyncio.create_task(test.run_all_async(duration, run_profiler=with_profiler)) for test in tests]
            await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

        # If any of the parallel test runs raised an exception, let it be propagated, after all tasks have
        # completed.
        # TODO: This will only raise the first Exception encountered. Once we migrate the perf pipelines
        # to 3.11 we could refactor to use ExceptionGroups so all exceptions will be captured.
        for task in tasks:
            task.result()

        # Add final test results to the results queue to be accumulated by the parent process.
        for test in tests:
            results.put((test._parallel_index, test.completed_operations, test.last_completion_time))
    finally:
        # Clean up status reporting thread.
        stop_status.set()
        status_thread.join()


def _report_status(status: multiprocessing.JoinableQueue, tests: List[_PerfTestABC], stop: threading.Event):
    """Report ongoing status of running tests.

    This is achieved by adding status to a joinable queue then waiting for that queue to be cleared
    by the parent processes. This should implicitly synchronize the status reporting across all child
    processes and the parent will dictate the frequency by which status is gathered.
    """
    # Delay the start a tiny bit to let the tests reset their status after warmup
    time.sleep(1)
    while not stop.is_set():
        for test in tests:
            status.put((test._parallel_index, test.completed_operations, test.last_completion_time))
        status.join()
