# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import asyncio
from typing import cast, List, BinaryIO
import time

from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    map_error,
)
from azure.core.utils import case_insensitive_dict

from ._operations import LoadTestAdministrationOperations as LoadTestAdministrationOperationsGenerated, JSON, ClsType
from ...operations._patch import build_upload_test_file_request
from ..._patch import TestFileValidationStatus
from ..._patch import TestRunStatus
from ._operations import LoadTestRunOperations as LoadTestRunOperationsGenerated


class LoadTestAdministrationOperations(LoadTestAdministrationOperationsGenerated):
    """
    for performing the operations on test
    """

    def __init__(self, *args, **kwargs):
        super(LoadTestAdministrationOperations, self).__init__(*args, **kwargs)


    async def begin_get_test_script_validation_status(
        self, test_id: str, *, refresh_time: int = 10, timeout: int = 60
    ) -> TestFileValidationStatus:
        """Check if JMX file is validated or not

        :param test_id: Unique id for the test
        :type test_id: str
        :param refresh_time: time to wait before checking the status of the JMX file (in seconds) (default is 10)
        :type refresh_time: int
        :param timeout: time to wait before timing out (in seconds) (default is 60)
        :type timeout: int
        :return: TestFileValidationStatus
        :rtype: TestFileValidationStatus
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError:
        """

        start_time = time.time()

        while True:
            result = await self.get_test(test_id=test_id)

            try:
                status = result["inputArtifacts"]["testScriptFileInfo"]["validationStatus"]

            except TypeError:
                raise ResourceNotFoundError(f"JMX file not found with TestId: {test_id}")

            if status == "VALIDATION_SUCCESS":
                return TestFileValidationStatus.ValidationSuccess

            if status == "VALIDATION_FAILED":
                return TestFileValidationStatus.ValidationFailed

            if time.time() - start_time + refresh_time > timeout:
                return TestFileValidationStatus.ValidationCheckTimeout

            await asyncio.sleep(refresh_time)


class LoadTestRunOperations(LoadTestRunOperationsGenerated):
    """
    class to perform operations on LoadTestRun
    """

    def __init__(self, *args, **kwargs):
        super(LoadTestRunOperations, self).__init__(*args, **kwargs)

    async def begin_test_run_status(
        self, test_run_id: str, *, refresh_time: int = 10, timeout: int = 60
    ) -> TestRunStatus:
        """Check if test run is completed

        :param test_run_id: Unique id for the test run
        :type test_run_id: str
        :param refresh_time: time to wait before checking the status of the test run (in seconds) (default is 10)
        :type refresh_time: int
        :param timeout: time to wait before timing out (in seconds) (default is 60)
        :type timeout: int
        :return: TestRunStatus
        :rtype: TestRunStatus
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError:
        """

        start_time = time.time()

        while True:
            result = await self.get_test_run(test_run_id=test_run_id)

            status = result["status"]

            if status == "DONE":
                return TestRunStatus.Done

            if status == "FAILED":
                return TestRunStatus.Failed

            if status == "CANCELLED":
                return TestRunStatus.Cancelled

            if time.time() - start_time + refresh_time > timeout:
                return TestRunStatus.CheckTimeout

            await asyncio.sleep(refresh_time)


__all__: List[str] = ["LoadTestAdministrationOperations"]


# Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
