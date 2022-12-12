# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from functools import partial
from typing import cast, List, BinaryIO, IO, Optional, Any, Dict
import time
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    map_error,
)
from azure.core.rest import HttpRequest
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict
from azure.core.polling import PollingMethod, LROPoller, NoPolling

from ._operations import LoadTestAdministrationOperations as LoadTestAdministrationOperationsGenerated, JSON, ClsType
from .._polling import ValidationCheckPoller
from .._serialization import Serializer
from .._vendor import _format_url_section
from .._patch import TestFileValidationStatus
from .._patch import TestRunStatus
from ._operations import LoadTestRunOperations as LoadTestRunOperationsGenerated

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False


class LoadTestAdministrationOperations(LoadTestAdministrationOperationsGenerated):
    """
    for performing the operations on the LoadTestAdministration Subclient
    """

    def __init__(self, *args, **kwargs):
        super(LoadTestAdministrationOperations, self).__init__(*args, **kwargs)

    # def begin_get_test_script_validation_status(
    #         self, test_id: str, *, refresh_time: int = 10, timeout: int = 60
    # ) -> TestFileValidationStatus:
    #     """Check if JMX file is validated or not
    #
    #     :param test_id: Unique id for the test
    #     :type test_id: str`
    #     :param refresh_time: time to wait before checking the status of the JMX file (in seconds) (default is 10)
    #     :type refresh_time: int
    #     :param timeout: time to wait before timing out (in seconds) (default is 60)
    #     :type timeout: int
    #     :return: TestFileValidationStatus
    #     :rtype: TestFileValidationStatus
    #     :raises ~azure.core.exceptions.HttpResponseError:
    #     :raises ~azure.core.exceptions.ResourceNotFoundError:
    #     """
    #
    #     start_time = time.time()
    #
    #     while True:
    #         result = self.get_test(test_id=test_id)
    #
    #         try:
    #             status = result["inputArtifacts"]["testScriptFileInfo"]["validationStatus"]
    #
    #         except TypeError:
    #             raise ResourceNotFoundError(f"JMX file not found with TestId: {test_id}")
    #
    #         if status == "VALIDATION_SUCCESS":
    #             return TestFileValidationStatus.ValidationSuccess
    #
    #         if status == "VALIDATION_FAILED":
    #             return TestFileValidationStatus.ValidationFailed
    #
    #         if time.time() - start_time + refresh_time > timeout:
    #             return TestFileValidationStatus.ValidationCheckTimeout
    #
    #         time.sleep(refresh_time)

    @distributed_trace
    def begin_upload_test_file(self, test_id: str, file_name: str, body: IO, *, poll_for_validation_status: bool = True,
                               file_type: Optional[str] = None, **kwargs: Any) -> LROPoller:
        """Upload file to the test

        :param test_id: Unique id for the test
        :type test_id: str
        :param file_name: Name of the file to be uploaded
        :type file_name: str
        :param body: File content to be uploaded
        :type body: IO
        :param file_type: Type of the file to be uploaded
        :type file_type: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: An instance of LROPoller object to check the validation status of file
        :param poll_for_validation_status: If true, polls for validation status of the file, else does not
        :type poll_for_validation_status: bool
        :rtype: ~azure.core.polling.LROPoller
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError:
        """

        polling_interval = kwargs.pop('_polling_interval', None)
        if polling_interval is None:
            polling_interval = 5

        upload_test_file_operation = self.upload_test_file(test_id=test_id, file_name=file_name, body=body,
                                                           file_type=file_type, **kwargs)

        command = partial(self.get_test_file, test_id=test_id, file_name=file_name)

        if poll_for_validation_status:
            create_validation_status_polling = ValidationCheckPoller(interval=polling_interval)
            return LROPoller(command, upload_test_file_operation, lambda *_: None, create_validation_status_polling)

        else:
            return LROPoller(command, upload_test_file_operation, lambda *_: None, NoPolling())


class LoadTestRunOperations(LoadTestRunOperationsGenerated):
    """
    class to perform operations on LoadTestRun
    """

    def __init__(self, *args, **kwargs):
        super(LoadTestRunOperations, self).__init__(*args, **kwargs)

    def begin_test_run_status(self, test_run_id: str, *, refresh_time: int = 10, timeout: int = 60) -> TestRunStatus:
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
            result = self.get_test_run(test_run_id=test_run_id)

            status = result["status"]

            if status == "DONE":
                return TestRunStatus.Done

            if status == "FAILED":
                return TestRunStatus.Failed

            if status == "CANCELLED":
                return TestRunStatus.Cancelled

            if time.time() - start_time + refresh_time > timeout:
                return TestRunStatus.CheckTimeout

            time.sleep(refresh_time)


__all__: List[str] = ["LoadTestAdministrationOperations", "LoadTestRunOperations"]


# Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
