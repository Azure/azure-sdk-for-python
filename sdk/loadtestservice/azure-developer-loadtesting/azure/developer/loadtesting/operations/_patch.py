# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import cast, List, BinaryIO
import time
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    map_error,
)
from azure.core.rest import HttpRequest
from azure.core.utils import case_insensitive_dict

from ._operations import LoadTestAdministrationOperations as LoadTestAdministrationOperationsGenerated, JSON, ClsType
from .._serialization import Serializer
from .._vendor import _format_url_section
from .._patch import TestFileValidationStatus
from .._patch import TestRunStatus
from ._operations import LoadTestRunOperations as LoadTestRunOperationsGenerated

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False


def build_upload_test_file_request(
    test_id: str,
    file_id: str,
    file: BinaryIO,
    **kwargs,
) -> HttpRequest:
    """
    Core logic for uploading a file
    """
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    # content_type = kwargs.pop('content_type', _headers.pop('Content-Type', None))  # type: Optional[str]
    api_version = kwargs.pop("api_version", _params.pop("api-version", "2022-06-01-preview"))  # type: str
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/loadtests/{testId}/files/{fileId}"
    path_format_arguments = {
        "testId": _SERIALIZER.url("test_id", test_id, "str", max_length=50, min_length=2, pattern=r"^[a-z0-9_-]*$"),
        "fileId": _SERIALIZER.url("file_id", file_id, "str", max_length=50, min_length=2, pattern=r"^[a-z0-9_-]*$"),
    }

    _url = _format_url_section(_url, **path_format_arguments)

    # Construct parameters
    _params["api-version"] = _SERIALIZER.query("api_version", api_version, "str")

    # Construct headers
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    files_json = {"file": file}

    return HttpRequest(method="PUT", url=_url, files=files_json, params=_params, headers=_headers, **kwargs)


class LoadTestAdministrationOperations(LoadTestAdministrationOperationsGenerated):
    """
    for performing the operations on the LoadTestAdministration Subclient
    """

    def __init__(self, *args, **kwargs):
        super(LoadTestAdministrationOperations, self).__init__(*args, **kwargs)

    def upload_test_file(self, test_id: str, file_id: str, file: BinaryIO, **kwargs) -> JSON:
        """Upload test file and link it to a test.

        Upload a test file to an existing test.

        :param test_id: Unique id for the test
        :type test_id: str
        :param file_id: Unique id for the file
        :type file_id: str
        :param file_content: dictionary containing file contet
        :type file: BinaryIO (file opened in Binary read mode)
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        cls = kwargs.pop("cls", None)  # type: ClsType[JSON]

        _content = file

        request = build_upload_test_file_request(
            test_id=test_id,
            file_id=file_id,
            file=file,
            api_version=self._config.api_version,
            headers=_headers,
            params=_params,
        )

        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)  # type: ignore

        request.method = "PUT"

        pipeline_response = self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
            request, stream=False, **kwargs
        )
        response = pipeline_response.http_response

        if response.status_code not in [201]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)
        if response.content:
            deserialized = response.json()
        else:
            deserialized = None
        if cls:
            return cls(pipeline_response, cast(JSON, deserialized), {})
        return cast(JSON, deserialized)

    def check_test_file_validation_status(
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
            result = self.get_load_test(test_id=test_id)

            try:
                status = result["inputArtifacts"]["testScriptUrl"]["validationStatus"]

            except TypeError:
                raise ResourceNotFoundError(f"JMX file not found with TestId: {test_id}")

            if status == "VALIDATION_SUCCESS":
                return TestFileValidationStatus.ValidationSuccess

            if status == "VALIDATION_FAILED":
                return TestFileValidationStatus.ValidationFailed

            if time.time() - start_time + refresh_time > timeout:
                return TestFileValidationStatus.ValidationCheckTimeout

            time.sleep(refresh_time)


class LoadTestRunOperations(LoadTestRunOperationsGenerated):
    """
    class to perform operations on LoadTestRun
    """

    def __init__(self, *args, **kwargs):
        super(LoadTestRunOperations, self).__init__(*args, **kwargs)

    def check_test_run_completed(self, test_run_id: str, *, refresh_time: int = 10, timeout: int = 60) -> TestRunStatus:
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

            try:
                status = result["status"]

            except TypeError:
                raise ResourceNotFoundError(f"Test Run not found with TestRunId: {test_run_id}")

            if status == "COMPLETED":
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
