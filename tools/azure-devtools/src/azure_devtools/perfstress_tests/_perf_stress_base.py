# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import abc
import threading
import argparse


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
    async def cleanup(self):
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
    def run_all_sync(self, duration: int) -> None:
        """
        Run all sync tests, including both warmup and duration.
        """

    @abc.abstractmethod
    async def run_all_async(self, duration: int) -> None:
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

    args = {}
    _global_parallel_index_lock = threading.Lock()
    _global_parallel_index = 0

    def __init__(self, arguments):
        self.args = arguments
        self._completed_operations = 0
        self._last_completion_time = 0.0

        with _PerfTestBase._global_parallel_index_lock:
            self._parallel_index = _PerfTestBase._global_parallel_index
            _PerfTestBase._global_parallel_index += 1

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
        Setup called once across all parallel test instances.
        Used to setup state that can be used by all test instances.
        """
        return

    async def global_cleanup(self) -> None:
        """
        Cleanup called once across all parallel test instances.
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

    def run_all_sync(self, duration: int) -> None:
        """
        Run all sync tests, including both warmup and duration.
        """
        raise NotImplementedError("run_all_sync must be implemented for {}".format(self.__class__.__name__))

    async def run_all_async(self, duration: int) -> None:
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
