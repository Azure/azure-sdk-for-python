# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
import inspect
import logging
import os
import pkgutil
import sys
from typing import List, Optional, Tuple
import multiprocessing
import threading

from ._perf_stress_base import _PerfTestABC, _PerfTestBase
from ._batch_perf_test import BatchPerfTest
from ._event_perf_test import EventPerfTest
from ._perf_stress_test import PerfStressTest
from ._repeated_timer import RepeatedTimer
from ._perf_stress_proc import run_process


class _PerfStressRunner:
    def __init__(self, test_folder_path: Optional[str] = None, debug: bool = False):
        self._operation_status_tracker: int = -1

        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        if debug:
            self.logger.setLevel(level=logging.DEBUG)
            handler.setLevel(level=logging.DEBUG)
        else:
            self.logger.setLevel(level=logging.INFO)
            handler.setLevel(level=logging.INFO)
        self.logger.addHandler(handler)

        # NOTE: If you need to support registering multiple test locations, move this into Initialize, call lazily on Run, expose RegisterTestLocation function.
        self._discover_tests(test_folder_path or os.getcwd())
        self._test_name: str = self._parse_args()

    def _get_completed_operations(self, results: List[Tuple[int, int, float]]) -> int:
        return sum([r[1] for r in results])

    def _get_operations_per_second(self, results: List[Tuple[int, int, float]]) -> float:
        return sum(map(lambda x: x[1] / x[2] if x[2] else 0, results))

    def _parse_args(self) -> str:
        # First, detect which test we're running.
        arg_parser = argparse.ArgumentParser(
            description="Python Perf Test Runner", usage="{} <TEST> [<args>]".format(__file__)
        )

        # NOTE: remove this and add another help string to query for available tests
        # if/when # of classes become enough that this isn't practical.
        arg_parser.add_argument(
            "test", help="Which test to run.  Supported tests: {}".format(" ".join(sorted(self._test_classes.keys())))
        )

        args = arg_parser.parse_args(sys.argv[1:2])
        test_name = args.test
        try:
            self._test_class_to_run = self._test_classes[test_name][0]
        except KeyError as e:
            self.logger.error(
                "Invalid test: {}\n    Test must be one of: {}\n".format(
                    args.test, " ".join(sorted(self._test_classes.keys()))
                )
            )
            raise

        # Next, parse args for that test.  We also do global args here too so as not to confuse the initial test parse.
        per_test_arg_parser = argparse.ArgumentParser(
            description=self._test_class_to_run.__doc__ or test_name, usage="{} {} [<args>]".format(__file__, args.test)
        )

        # Global args
        per_test_arg_parser.add_argument(
            "-p", "--parallel", nargs="?", type=int, help="Degree of parallelism to run with.  Default is 1.", default=1
        )
        per_test_arg_parser.add_argument(
            "--processes", nargs="?", type=int, help="Number of concurrent processes over which to distribute the parallel runs.  Default is the number of cores.", default=multiprocessing.cpu_count()
        )
        per_test_arg_parser.add_argument(
            "-d", "--duration", nargs="?", type=int, help="Duration of the test in seconds.  Default is 10.", default=10
        )
        per_test_arg_parser.add_argument(
            "-w", "--warmup", nargs="?", type=int, help="Duration of warmup in seconds.  Default is 5.", default=5
        )
        per_test_arg_parser.add_argument(
            "--no-cleanup", action="store_true", help="Do not run cleanup logic.  Default is false.", default=False
        )
        per_test_arg_parser.add_argument(
            "--sync", action="store_true", help="Run tests in sync mode.  Default is False.", default=False
        )
        per_test_arg_parser.add_argument(
            "--profile", action="store_true", help="Run tests with profiler.  Default is False.", default=False
        )
        per_test_arg_parser.add_argument(
            "-x", "--test-proxies", help="URIs of TestProxy Servers (separated by ';')",
            type=lambda s: s.split(';')
        )
        per_test_arg_parser.add_argument(
            "--insecure", action="store_true", help="Disable SSL validation. Default is False.", default=False
        )

        # Per-test args
        self._test_class_to_run.add_arguments(per_test_arg_parser)
        self.per_test_args = per_test_arg_parser.parse_args(sys.argv[2:])

        self.logger.info("")
        self.logger.info("=== Options ===")
        self.logger.info(args)
        self.logger.info(self.per_test_args)
        self.logger.info("")
        return test_name

    def _discover_tests(self, test_folder_path):
        base_classes = [PerfStressTest, BatchPerfTest, EventPerfTest]
        self._test_classes = {}
        if os.path.isdir(os.path.join(test_folder_path, 'tests')):
            test_folder_path = os.path.join(test_folder_path, 'tests')
        self.logger.debug("Searching for tests in {}".format(test_folder_path))

        # Dynamically enumerate all python modules under the tests path for classes that implement PerfStressTest
        for loader, module_name, _ in pkgutil.walk_packages([test_folder_path]):
            try:
                module_loader = loader.find_module(module_name)
                module = module_loader.load_module(module_name)
            except Exception as e:
                self.logger.debug("Unable to load module {}: {}".format(module_name, e))
                continue
            for name, value in inspect.getmembers(module):
                if name.startswith("_"):
                    continue
                if inspect.isclass(value):
                    if issubclass(value, _PerfTestABC) and value not in base_classes:
                        self.logger.info("Loaded test class: {}".format(name))
                        self._test_classes[name] = (value, (module_loader, module_name))

    def _next_stage(self, title: str, track_status: bool = False, report_results: bool = False):
        # Wait for previous stage to complete.
        self.test_stages[title].wait()

        # Stop any status tracking of the previous stage.
        if self.status_thread.is_running:
            self.status_thread.stop()

        # If previous stage had results, report.
        if report_results:
            self._report_results()

        self.logger.info("")
        self.logger.info("=== {} ===".format(title))

        # If next stage status should be tracked, restart tracker.
        if track_status:
            self._operation_status_tracker = -1
            self.status_thread.start()

    async def start(self):
        # If unspecified, number of process will be the lesser of number of cores
        # and number of parallel tests.
        processes = min(self.per_test_args.parallel, self.per_test_args.processes)

        # Evenly divide the number of parallel tests between the processes into a list
        # of tuples containing the first parallel index used by each process, and the number
        # of threads that will be run by each process.
        # E.g. if parallel=10, processes=4: mapping=[(0, 3), (3, 3), (6, 2), (8, 2)]
        k, m = divmod(self.per_test_args.parallel, processes)
        mapping = [(i*k+min(i, m), ((i+1)*k+min(i+1, m)) - (i*k+min(i, m))) for i in range(processes)]

        self.results = multiprocessing.Queue()
        self.status = multiprocessing.JoinableQueue()
        self.status_thread = RepeatedTimer(1, self._print_status, start_now=False)

        # The barrier will synchronize each child proc with the parent at each stage of the
        # the testing run. This prevents one proc from running tests while global resources
        # are still being configured or cleaned up.
        self.test_stages = {
            "Setup": multiprocessing.Barrier(processes + 1),
            "Post Setup": multiprocessing.Barrier(processes + 1),
            "Warmup": multiprocessing.Barrier(processes + 1),
            "Tests": multiprocessing.Barrier(processes + 1),
            "Pre Cleanup": multiprocessing.Barrier(processes + 1),
            "Cleanup": multiprocessing.Barrier(processes + 1),
            "Finished": multiprocessing.Barrier(processes + 1)
        }

        try:
            futures = [multiprocessing.Process(
                        target=run_process,
                        args=(
                            index,
                            self.per_test_args,
                            self._test_classes[self._test_name][1],
                            self._test_name,
                            threads,
                            self.test_stages,
                            self.results,
                            self.status),
                        daemon=True) for index, threads in mapping]
            [f.start() for f in futures]

            # All tests wait to start "Setup".
            # This allows one proc to finish the "GlobalSetup" before all of them
            # start the per-test "Setup".
            self._next_stage("Setup")

            # All tests wait to start Post Setup.
            self._next_stage("Post Setup")

            # If a warm up is configured, wait will all tests have finished all setup
            # stages before beginning "Warmup".
            if self.per_test_args.warmup:
                self._next_stage("Warmup", track_status=True)

            # Wait will all tests have completed setup and warmup before beginning "Tests".
            self._next_stage("Tests", track_status=True, report_results=True)

            # Wait till all tests have completed before beginning cleanup and shutdown.
            self._next_stage("Pre Cleanup", report_results=True)

            # If cleanup is configured, wait till all tests are ready to begin "Cleanup"
            if not self.per_test_args.no_cleanup:
                self._next_stage("Cleanup")

            # Wait till all tests have finished cleaning up, this allows one proc to start
            # the "GlobalCleanup" which may start pulling down resources.
            self._next_stage("Finished")

            # Close all processes.
            [f.join() for f in futures]

        except threading.BrokenBarrierError:
            self.logger.warn("Exception: One or more test processes failed and exited.")
        except Exception as e:
            self.logger.warn("Exception: " + str(e))

    def _report_results(self):
        """Calculate and log the test run results across all child processes"""
        operations = []
        while not self.results.empty():
            operations.append(self.results.get())

        total_operations = self._get_completed_operations(operations)
        self.logger.info("")
        operations_per_second = self._get_operations_per_second(operations)
        if operations_per_second:
            seconds_per_operation = 1 / operations_per_second
            weighted_average_seconds = total_operations / operations_per_second
            self.logger.info(
                "Completed {:,} operations in a weighted-average of {:,.2f}s ({:,.2f} ops/s, {:,.3f} s/op)".format(
                    total_operations, weighted_average_seconds, operations_per_second, seconds_per_operation
                )
            )
        else:
            self.logger.info("Completed without generating operation statistics.")
        self.logger.info("")

    def _print_status(self):
        """Print the ongoing status as reported by all child processes"""
        if self._operation_status_tracker == -1:
            self._operation_status_tracker = 0
            self.logger.info("Current\t\tTotal\t\tAverage")

        operations = []
        while not self.status.empty():
            operations.append(self.status.get())
            self.status.task_done()
        total_operations = self._get_completed_operations(operations)
        current_operations = total_operations - self._operation_status_tracker
        average_operations = self._get_operations_per_second(operations)

        self._operation_status_tracker = total_operations
        self.logger.info("{}\t\t{}\t\t{:.2f}".format(current_operations, total_operations, average_operations))
