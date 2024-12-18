# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import logging
import time
from typing import List

from azure.core.polling import PollingMethod
from azure.core.tracing.decorator import distributed_trace
from azure.core.polling import LROPoller

from ._operations import JSON
from ._operations import LoadTestAdministrationClientOperationsMixin as GeneratedAdministrationClientOperations
from ._operations import LoadTestRunClientOperationsMixin as GeneratedRunClientOperations

logger = logging.getLogger(__name__)

class LoadTestingPollingMethod(PollingMethod):
    """Base class for custom sync polling methods."""

    def _update_status(self) -> None:
        raise NotImplementedError("This method needs to be implemented")

    def _update_resource(self) -> None:
        self._resource = self._command()

    def initialize(self, client, initial_response, deserialization_callback) -> None:
        self._command = client
        self._initial_response = initial_response
        self._resource = initial_response

    def status(self) -> str:
        return self._status

    def finished(self) -> bool:
        return self._status in self._termination_statuses

    def resource(self) -> JSON:
        return self._resource

    def run(self) -> None:
        try:
            while not self.finished():
                self._update_resource()
                self._update_status()

                if not self.finished():
                    time.sleep(self._polling_interval)
        except Exception as e:
            logger.error(e)
            raise e


class ValidationCheckPoller(LoadTestingPollingMethod):
    """Polling method for long-running file validation operation."""

    def __init__(self, interval=5) -> None:
        self._resource = None
        self._command = None
        self._initial_response = None
        self._polling_interval = interval
        self._status = None
        self._termination_statuses = ["VALIDATION_SUCCESS", "VALIDATION_FAILED", "VALIDATION_NOT_REQUIRED"]

    def _update_status(self) -> None:
        self._status = self._resource["validationStatus"]


class TestRunStatusPoller(LoadTestingPollingMethod):
    """Polling method for polling a Test Run."""

    def __init__(self, interval=5) -> None:
        self._resource = None
        self._command = None
        self._initial_response = None
        self._polling_interval = interval
        self._status = None
        self._termination_statuses = ["DONE", "FAILED", "CANCELLED"]

    def _update_status(self) -> None:
        self._status = self._resource["status"]

class TestProfileRunStatusPoller(LoadTestingPollingMethod):
    """Polling method for polling a Test Profile Run."""

    def __init__(self, interval=5) -> None:
        self._resource = None
        self._command = None
        self._initial_response = None
        self._polling_interval = interval
        self._status = None
        self._termination_statuses = ["DONE", "FAILED", "CANCELLED"]

    def _update_status(self):
        self._status = self._resource["status"]

class LoadTestAdministrationClientOperationsMixin(GeneratedAdministrationClientOperations):
    
    def __init__(self, *args, **kwargs):
        super(LoadTestAdministrationClientOperationsMixin, self).__init__(*args, **kwargs)

class LoadTestRunClientOperationsMixin(GeneratedRunClientOperations):
    
    def __init__(self, *args, **kwargs):
        super(LoadTestRunClientOperationsMixin, self).__init__(*args, **kwargs)

# Add all objects you want publicly available to users at this package level
__all__: List[str] = [
    "LoadTestAdministrationClientOperationsMixin",
    "LoadTestRunClientOperationsMixin"
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
