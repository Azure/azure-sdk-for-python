# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
import asyncio
import time
import inspect
import logging
import os
import pkgutil
import sys
import threading

from .perf_stress_test import PerfStressTest
from .repeated_timer import RepeatedTimer


class PerfStressRunner:
    def __init__(self, test_folder_path=None):
        if test_folder_path is None:
            # Use current working directory
            test_folder_path = os.getcwd()

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level=logging.INFO)
        handler = logging.StreamHandler()
        handler.setLevel(level=logging.INFO)
        self.logger.addHandler(handler)

        #NOTE: If you need to support registering multiple test locations, move this into Initialize, call lazily on Run, expose RegisterTestLocation function.
        self._discover_tests(test_folder_path)
        self._parse_args()

    def _get_completed_operations(self):
        return sum(self._completed_operations)

    def _get_operations_per_second(self):
        return sum(map(
            lambda x: x[0] / x[1] if x[1] else 0,
            zip(self._completed_operations, self._last_completion_times)))

    def _parse_args(self):
        # First, detect which test we're running.
        arg_parser = argparse.ArgumentParser(
            description='Python Perf Test Runner',
            usage='{} <TEST> [<args>]'.format(__file__))

        # NOTE: remove this and add another help string to query for available tests
        # if/when # of classes become enough that this isn't practical.
        arg_parser.add_argument('test', help='Which test to run.  Supported tests: {}'.format(" ".join(sorted(self._test_classes.keys()))))

        args = arg_parser.parse_args(sys.argv[1:2])
        try:
            self._test_class_to_run = self._test_classes[args.test]
        except KeyError as e:
            self.logger.error("Invalid test: {}\n    Test must be one of: {}\n".format(args.test, " ".join(sorted(self._test_classes.keys()))))
            raise

        # Next, parse args for that test.  We also do global args here too so as not to confuse the initial test parse.
        per_test_arg_parser = argparse.ArgumentParser(
            description=self._test_class_to_run.__doc__ or args.test,
            usage='{} {} [<args>]'.format(__file__, args.test))

        # Global args
        per_test_arg_parser.add_argument('-p', '--parallel', nargs='?', type=int, help='Degree of parallelism to run with.  Default is 1.', default=1)
        per_test_arg_parser.add_argument('-d', '--duration', nargs='?', type=int, help='Duration of the test in seconds.  Default is 10.', default=10)
        per_test_arg_parser.add_argument('-i', '--iterations', nargs='?', type=int, help='Number of iterations in the main test loop.  Default is 1.', default=1)
        per_test_arg_parser.add_argument('-w', '--warmup', nargs='?', type=int, help='Duration of warmup in seconds.  Default is 5.', default=5)
        per_test_arg_parser.add_argument('--no-cleanup', action='store_true', help='Do not run cleanup logic.  Default is false.', default=False)
        per_test_arg_parser.add_argument('--sync', action='store_true', help='Run tests in sync mode.  Default is False.', default=False)

        # Per-test args
        self._test_class_to_run.add_arguments(per_test_arg_parser)
        self.per_test_args = per_test_arg_parser.parse_args(sys.argv[2:])

        self.logger.info("")
        self.logger.info("=== Options ===")
        self.logger.info(args)
        self.logger.info(self.per_test_args)
        self.logger.info("")

    def _discover_tests(self, test_folder_path):
        self._test_classes = {}

        # Dynamically enumerate all python modules under the tests path for classes that implement PerfStressTest
        for loader, name, _ in pkgutil.walk_packages([test_folder_path]):
            try:
                module = loader.find_module(name).load_module(name)
            except Exception as e:
                self.logger.warn("Unable to load module {}: {}".format(name, e))
                continue
            for name, value in inspect.getmembers(module):

                if name.startswith('_'):
                    continue
                if inspect.isclass(value) and issubclass(value, PerfStressTest) and value != PerfStressTest:
                    self.logger.info("Loaded test class: {}".format(name))
                    self._test_classes[name] = value

    async def start(self):      
        self.logger.info("=== Setup ===")
       
        tests = []
        for _ in range(0, self.per_test_args.parallel):
            tests.append(self._test_class_to_run(self.per_test_args))

        try:
            try:
                await tests[0].global_setup()
                try:
                    await asyncio.gather(*[test.setup() for test in tests])

                    self.logger.info("")

                    if self.per_test_args.warmup > 0:
                        await self._run_tests(tests, self.per_test_args.warmup, "Warmup")

                    for i in range(0, self.per_test_args.iterations):
                        title = "Test"
                        if self.per_test_args.iterations > 1:
                            title += " " + (i + 1)
                        await self._run_tests(tests, self.per_test_args.duration, title)
                except Exception as e:
                    print("Exception: " + str(e))
                finally:
                    if not self.per_test_args.no_cleanup:
                        self.logger.info("=== Cleanup ===")
                        await asyncio.gather(*[test.cleanup() for test in tests])
            except Exception as e:
                print("Exception: " + str(e))
            finally:
                if not self.per_test_args.no_cleanup:
                    await tests[0].global_cleanup()
        except Exception as e:
            print("Exception: " + str(e))
        finally:
            await asyncio.gather(*[test.close() for test in tests])

    async def _run_tests(self, tests, duration, title):
        self._completed_operations = [0] * len(tests)
        self._last_completion_times = [0] * len(tests)
        self._last_total_operations = -1

        status_thread = RepeatedTimer(1, self._print_status, title)

        if self.per_test_args.sync:
            threads = []
            for id, test in enumerate(tests):
                thread = threading.Thread(target=lambda: self._run_sync_loop(test, duration, id))
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()
        else:
            await asyncio.gather(*[self._run_async_loop(test, duration, id) for id, test in enumerate(tests)])

        status_thread.stop()

        self.logger.info("")
        self.logger.info("=== Results ===")

        total_operations = self._get_completed_operations()
        operations_per_second = self._get_operations_per_second()
        seconds_per_operation = 1 / operations_per_second
        weighted_average_seconds = total_operations / operations_per_second

        self.logger.info("Completed {:,} operations in a weighted-average of {:,.2f}s ({:,.2f} ops/s, {:,.3f} s/op)".format(
            total_operations, weighted_average_seconds, operations_per_second, seconds_per_operation))
        self.logger.info("")

    def _run_sync_loop(self, test, duration, id):
        start = time.time()
        runtime = 0
        while runtime < duration:
            test.run_sync()
            runtime = time.time() - start
            self._completed_operations[id] += 1
            self._last_completion_times[id] = runtime

    async def _run_async_loop(self, test, duration, id):
        start = time.time()
        runtime = 0
        while runtime < duration:
            await test.run_async()
            runtime = time.time() - start
            self._completed_operations[id] += 1
            self._last_completion_times[id] = runtime

    def _print_status(self, title):
        if self._last_total_operations == -1:
            self._last_total_operations = 0
            self.logger.info("=== {} ===\nCurrent\t\tTotal\t\tAverage".format(title))

        total_operations = self._get_completed_operations()
        current_operations = total_operations - self._last_total_operations
        average_operations = self._get_operations_per_second()

        self._last_total_operations = total_operations
        self.logger.info("{}\t\t{}\t\t{:.2f}".format(current_operations, total_operations, average_operations))
