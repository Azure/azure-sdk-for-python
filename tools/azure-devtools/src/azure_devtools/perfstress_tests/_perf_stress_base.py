# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import abc
import multiprocessing
import argparse
import pstats
import cProfile
from typing import Optional


PSTATS_PRINT_DEFAULT_SORT_KEY = pstats.SortKey.TIME
PSTATS_PRINT_DEFAULT_LINE_COUNT = 36


class _PerfTestABC(abc.ABC):

    @property
    @abc.abstractmethod
    def completed_operations(self) -> int:
        """
        Total number of operations completed by run_all().
        Reset after warmup.
        """

    @property
    @abc.abstractmethod
    def last_completion_time(self) -> float:
        """
        Elapsed time between start of warmup/run and last completed operation.
        Reset after warmup.
        """

    @abc.abstractmethod
    async def global_setup(self) -> None:
        """
        Setup called once across all parallel test instances.
        Used to setup state that can be used by all test instances.
        """

    @abc.abstractmethod
    async def global_cleanup(self) -> None:
        """
        Cleanup called once across all parallel test instances.
        Used to cleanup state that can be used by all test instances.
        """

    @abc.abstractmethod
    async def setup(self) -> None:
        """
        Setup called once per parallel test instance.
        Used to setup state specific to this test instance.
        """

    @abc.abstractmethod
    async def cleanup(self) -> None:
        """
        Cleanup called once per parallel test instance.
        Used to cleanup state specific to this test instance.
        """

    @abc.abstractmethod
    async def post_setup(self) -> None:
        """
        Post-setup called once per parallel test instance.
        Used by base classes to setup state (like test-proxy) after all derived class setup is complete.
        """

    @abc.abstractmethod
    async def pre_cleanup(self) -> None:
        """
        Pre-cleanup called once per parallel test instance.
        Used by base classes to cleanup state (like test-proxy) before all derived class cleanup runs.
        """

    @abc.abstractmethod
    async def close(self) -> None:
        """
        Close any open client resources/connections per parallel test instance.
        """

    @abc.abstractmethod
    def run_all_sync(self, duration: int, *, run_profiler: bool = False, **kwargs) -> None:
        """
        Run all sync tests, including both warmup and duration.
        """

    @abc.abstractmethod
    async def run_all_async(self, duration: int, *, run_profiler: bool = False, **kwargs) -> None:
        """
        Run all async tests, including both warmup and duration.
        """
    
    @staticmethod
    @abc.abstractmethod
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        """
        Add test class specific command line arguments.
        """

    @staticmethod
    @abc.abstractmethod
    def get_from_env(variable: str) -> str:
        """
        Get the value of an env var. If empty or not found, a ValueError will be raised.
        """


class _PerfTestBase(_PerfTestABC):
    """Base class for implementing a python perf test."""

    args: argparse.Namespace
    _global_parallel_index_lock = multiprocessing.Lock()
    _global_parallel_index: int = 0

    def __init__(self, arguments: argparse.Namespace):
        self.args = arguments
        self._completed_operations: int = 0
        self._last_completion_time: float = 0.0
        self._parallel_index: int = _PerfTestBase._global_parallel_index
        _PerfTestBase._global_parallel_index += 1
        self._profile: Optional[cProfile.Profile] = None
        if self.args.profile:
            self._profile = cProfile.Profile()

    @property
    def completed_operations(self) -> int:
        """
        Total number of operations completed by run_all().
        Reset after warmup.
        """
        return self._completed_operations

    @property
    def last_completion_time(self) -> float:
        """
        Elapsed time between start of warmup/run and last completed operation.
        Reset after warmup.
        """
        return self._last_completion_time

    async def global_setup(self) -> None:
        """
        Setup called once per process across all threaded test instances.
        Used to setup state that can be used by all test instances.
        """
        return

    async def global_cleanup(self) -> None:
        """
        Cleanup called once per process across all threaded test instances.
        Used to cleanup state that can be used by all test instances.
        """
        return

    async def setup(self) -> None:
        """
        Setup called once per parallel test instance.
        Used to setup state specific to this test instance.
        """
        return

    async def cleanup(self) -> None:
        """
        Cleanup called once per parallel test instance.
        Used to cleanup state specific to this test instance.
        """
        return

    async def post_setup(self) -> None:
        """
        Post-setup called once per parallel test instance.
        Used by base classes to setup state (like test-proxy) after all derived class setup is complete.
        """
        return

    async def pre_cleanup(self) -> None:
        """
        Pre-cleanup called once per parallel test instance.
        Used by base classes to cleanup state (like test-proxy) before all derived class cleanup runs.
        """
        return

    async def close(self):
        """
        Close any open client resources/connections per parallel test instance.
        """
        return

    def run_all_sync(self, duration: int, *, run_profiler: bool = False, **kwargs) -> None:
        """
        Run all sync tests, including both warmup and duration.
        """
        raise NotImplementedError("run_all_sync must be implemented for {}".format(self.__class__.__name__))

    async def run_all_async(self, duration: int, *, run_profiler: bool = False, **kwargs) -> None:
        """
        Run all async tests, including both warmup and duration.
        """
        raise NotImplementedError("run_all_async must be implemented for {}".format(self.__class__.__name__))

    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        """
        Add test class specific command line arguments.
        """
        return

    @staticmethod
    def get_from_env(variable: str) -> str:
        """
        Get the value of an env var. If empty or not found, a ValueError will be raised.
        """
        value = os.environ.get(variable)
        if not value:
            raise ValueError("Undefined environment variable {}".format(variable))
        return value

    def _save_profile(self, sync: str, output_path: Optional[str] = None) -> None:
        """
        Dump the profiler data to the file path specified. If no path is specified, use the current working directory.
        """
        if self._profile:
            profile_name = output_path or "{}/cProfile-{}-{}-{}.pstats".format(
                os.getcwd(),
                self.__class__.__name__,
                self._parallel_index,
                sync)
            print("Dumping profile data to {}".format(profile_name))
            self._profile.dump_stats(profile_name)
        else:
            print("No profile generated.")

    def _print_profile_stats(
        self,
        *,
        sort_key: pstats.SortKey = PSTATS_PRINT_DEFAULT_SORT_KEY,
        count: int = PSTATS_PRINT_DEFAULT_LINE_COUNT
    ) -> None:
        """Print the profile stats to stdout.

        A sort key can be specified to establish how stats should be sorted, and a line count can also be
        specified to limit the number of lines printed.
        """
        if self._profile:
            # Increase the precision of the pstats output
            pstats.f8 = lambda x: f"{x:8.5f}"

            stats = pstats.Stats(self._profile).sort_stats(sort_key)
            stats.print_stats(count)
