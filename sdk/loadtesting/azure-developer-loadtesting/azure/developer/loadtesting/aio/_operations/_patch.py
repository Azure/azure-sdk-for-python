# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import asyncio
import logging
import time
from functools import partial
from typing import Any, IO, List, Optional, overload, Union

from azure.core.polling import AsyncPollingMethod, AsyncLROPoller
from azure.core.tracing.decorator_async import distributed_trace_async

from ._operations import JSON
from ._operations import LoadTestAdministrationClientOperationsMixin as GeneratedAdministrationClientOperations
from ._operations import LoadTestRunClientOperationsMixin as GeneratedRunClientOperations

from ... import models as _models

logger = logging.getLogger(__name__)


class AsyncLoadTestingPollingMethod(AsyncPollingMethod):
    """Base class for custom async polling methods."""

    def _update_status(self) -> None:
        raise NotImplementedError("This method needs to be implemented")

    async def _update_resource(self) -> None:
        self._resource = await self._command()

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

    async def run(self) -> None:
        try:
            while not self.finished():
                await self._update_resource()
                self._update_status()

                if not self.finished():
                    await asyncio.sleep(self._polling_interval)
        except Exception as e:
            logger.error(e)
            raise e


class AsyncValidationCheckPoller(AsyncLoadTestingPollingMethod):
    def __init__(self, interval=5) -> None:
        self._resource = None
        self._command = None
        self._initial_response = None
        self._polling_interval = interval
        self._status = None
        self._termination_statuses = [
            "VALIDATION_SUCCESS",
            "VALIDATION_FAILURE",
            "NOT_VALIDATED",
            "VALIDATION_NOT_REQUIRED",
        ]

    def _update_status(self) -> None:
        self._status = self._resource["validationStatus"]


class AsyncTestRunStatusPoller(AsyncLoadTestingPollingMethod):
    def __init__(self, interval=5) -> None:
        self._resource = None
        self._command = None
        self._initial_response = None
        self._polling_interval = interval
        self._status = None
        self._termination_statuses = ["DONE", "FAILED", "CANCELLED"]

    def _update_status(self) -> None:
        self._status = self._resource["status"]


class AsyncTestProfileRunStatusPoller(AsyncLoadTestingPollingMethod):
    def __init__(self, interval=5) -> None:
        self._resource = None
        self._command = None
        self._initial_response = None
        self._polling_interval = interval
        self._status = None
        self._termination_statuses = ["DONE", "FAILED", "CANCELLED"]

    def _update_status(self) -> None:
        self._status = self._resource["status"]


class LoadTestAdministrationClientOperationsMixin(GeneratedAdministrationClientOperations):

    def __init__(self, *args, **kwargs):
        super(LoadTestAdministrationClientOperationsMixin, self).__init__(*args, **kwargs)

    @overload
    async def begin_upload_test_file(
        self,
        test_id: str,
        file_name: str,
        body: IO,
        *,
        file_type: Optional[Union[str, _models.FileType]] = None,
        **kwargs: Any
    ) -> AsyncLROPoller[_models.TestFileInfo]:
        """Upload input file for a given test Id. File size can't be more than 50 MB.
        Existing file with same name for the given test will be overwritten. File
        should be provided in the request body as application/octet-stream.

        Upload input file for a given test Id. File size can't be more than 50 MB.
        Existing file with same name for the given test will be overwritten. File
        should be provided in the request body as application/octet-stream.

        :param test_id: Unique name for the load test, must contain only lower-case alphabetic,
         numeric, underscore or hyphen characters. Required.
        :type test_id: str
        :param file_name: Unique name for test file with file extension like : App.jmx. Required.
        :type file_name: str
        :param body: The file content as application/octet-stream. Required.
        :type body: IO
        :keyword file_type: File type. Known values are: "JMX_FILE", "USER_PROPERTIES",
         "ADDITIONAL_ARTIFACTS", "ZIPPED_ARTIFACTS", "URL_TEST_CONFIG", and "TEST_SCRIPT". Default value
         is None.
        :paramtype file_type: str or ~azure.developer.loadtesting.models.FileType
        :return: An instance of AsyncLROPoller. Call `result()` on the poller object to return a :class:`~azure.developer.loadtesting.models.TestFileInfo`.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.developer.loadtesting.models.TestFileInfo]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_upload_test_file(
        self,
        test_id: str,
        file_name: str,
        body: bytes,
        *,
        file_type: Optional[Union[str, _models.FileType]] = None,
        **kwargs: Any
    ) -> AsyncLROPoller[_models.TestFileInfo]:
        """Upload input file for a given test Id. File size can't be more than 50 MB.
        Existing file with same name for the given test will be overwritten. File
        should be provided in the request body as application/octet-stream.

        Upload input file for a given test Id. File size can't be more than 50 MB.
        Existing file with same name for the given test will be overwritten. File
        should be provided in the request body as application/octet-stream.

        :param test_id: Unique name for the load test, must contain only lower-case alphabetic,
         numeric, underscore or hyphen characters. Required.
        :type test_id: str
        :param file_name: Unique name for test file with file extension like : App.jmx. Required.
        :type file_name: str
        :param body: The file content as application/octet-stream. Required.
        :type body: bytes
        :keyword file_type: File type. Known values are: "JMX_FILE", "USER_PROPERTIES",
         "ADDITIONAL_ARTIFACTS", "ZIPPED_ARTIFACTS", "URL_TEST_CONFIG", and "TEST_SCRIPT". Default value
         is None.
        :paramtype file_type: str or ~azure.developer.loadtesting.models.FileType
        :return: An instance of AsyncLROPoller. Call `result()` on the poller object to return a :class:`~azure.developer.loadtesting.models.TestFileInfo`.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.developer.loadtesting.models.TestFileInfo]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def begin_upload_test_file(
        self,
        test_id: str,
        file_name: str,
        body: Union[IO, bytes],
        *,
        file_type: Optional[Union[str, _models.FileType]] = None,
        **kwargs: Any
    ) -> AsyncLROPoller[_models.TestFileInfo]:
        """Upload input file for a given test Id. File size can't be more than 50 MB.
        Existing file with same name for the given test will be overwritten. File
        should be provided in the request body as application/octet-stream.

        Upload input file for a given test Id. File size can't be more than 50 MB.
        Existing file with same name for the given test will be overwritten. File
        should be provided in the request body as application/octet-stream.

        :param test_id: Unique name for the load test, must contain only lower-case alphabetic,
         numeric, underscore or hyphen characters. Required.
        :type test_id: str
        :param file_name: Unique name for test file with file extension like : App.jmx. Required.
        :type file_name: str
        :param body: The file content as application/octet-stream. Required.
        :type body: Is one of the following types: IO, bytes
        :keyword file_type: File type. Known values are: "JMX_FILE", "USER_PROPERTIES",
         "ADDITIONAL_ARTIFACTS", "ZIPPED_ARTIFACTS", "URL_TEST_CONFIG", and "TEST_SCRIPT". Default value
         is None.
        :paramtype file_type: str or ~azure.developer.loadtesting.models.FileType
        :return: An instance of AsyncLROPoller. Call `result()` on the poller object to return a :class:`~azure.developer.loadtesting.models.TestFileInfo`.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.developer.loadtesting.models.TestFileInfo]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        polling_interval = kwargs.pop("_polling_interval", None)
        if polling_interval is None:
            polling_interval = 5
        upload_test_file_operation = await super()._begin_upload_test_file(
            test_id=test_id, file_name=file_name, body=body, file_type=file_type, **kwargs
        )

        command = partial(self.get_test_file, test_id=test_id, file_name=file_name)

        file_validation_status_polling = AsyncValidationCheckPoller(interval=polling_interval)
        return AsyncLROPoller(
            command,
            upload_test_file_operation,
            lambda *_: None,
            file_validation_status_polling,
        )


class LoadTestRunClientOperationsMixin(GeneratedRunClientOperations):

    def __init__(self, *args, **kwargs):
        super(LoadTestRunClientOperationsMixin).__init__(*args, **kwargs)

    @overload
    async def begin_test_run(
        self,
        test_run_id: str,
        body: _models.TestRun,
        *,
        content_type: str = "application/merge-patch+json",
        old_test_run_id: Optional[str] = None,
        **kwargs: Any
    ) -> AsyncLROPoller[_models.TestRun]:
        """Create and start a new test run with the given test run Id.

        Create and start a new test run with the given test run Id.

        :param test_run_id: Unique test run identifier for the load test run, must contain only
         lower-case alphabetic, numeric, underscore or hyphen characters. Required.
        :type test_run_id: str
        :param body: The resource instance. Required.
        :type body: ~azure.developer.loadtesting.models.TestRun
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/merge-patch+json".
        :paramtype content_type: str
        :keyword old_test_run_id: Existing test run identifier that should be rerun, if this is
         provided, the
         test will run with the JMX file, configuration and app components from the
         existing test run. You can override the configuration values for new test run
         in the request body. Default value is None.
        :paramtype old_test_run_id: str
        :return: An instance of AsyncLROPoller. Call `result()` on the poller object to return a :class:`~azure.developer.loadtesting.models.TestRun`.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.developer.loadtesting.models.TestRun]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_test_run(
        self,
        test_run_id: str,
        body: JSON,
        *,
        content_type: str = "application/merge-patch+json",
        old_test_run_id: Optional[str] = None,
        **kwargs: Any
    ) -> AsyncLROPoller[_models.TestRun]:
        """Create and start a new test run with the given test run Id.

        Create and start a new test run with the given test run Id.

        :param test_run_id: Unique test run identifier for the load test run, must contain only
         lower-case alphabetic, numeric, underscore or hyphen characters. Required.
        :type test_run_id: str
        :param body: The resource instance. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/merge-patch+json".
        :paramtype content_type: str
        :keyword old_test_run_id: Existing test run identifier that should be rerun, if this is
         provided, the
         test will run with the JMX file, configuration and app components from the
         existing test run. You can override the configuration values for new test run
         in the request body. Default value is None.
        :paramtype old_test_run_id: str
        :return: An instance of AsyncLROPoller. Call `result()` on the poller object to return a :class:`~azure.developer.loadtesting.models.TestRun`.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.developer.loadtesting.models.TestRun]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_test_run(
        self,
        test_run_id: str,
        body: IO[bytes],
        *,
        content_type: str = "application/merge-patch+json",
        old_test_run_id: Optional[str] = None,
        **kwargs: Any
    ) -> AsyncLROPoller[_models.TestRun]:
        """Create and start a new test run with the given test run Id.

        Create and start a new test run with the given test run Id.

        :param test_run_id: Unique test run identifier for the load test run, must contain only
         lower-case alphabetic, numeric, underscore or hyphen characters. Required.
        :type test_run_id: str
        :param body: The resource instance. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/merge-patch+json".
        :paramtype content_type: str
        :keyword old_test_run_id: Existing test run identifier that should be rerun, if this is
         provided, the
         test will run with the JMX file, configuration and app components from the
         existing test run. You can override the configuration values for new test run
         in the request body. Default value is None.
        :paramtype old_test_run_id: str
        :return: An instance of AsyncLROPoller. Call `result()` on the poller object to return a :class:`~azure.developer.loadtesting.models.TestRun`.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.developer.loadtesting.models.TestRun]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def begin_test_run(
        self,
        test_run_id: str,
        body: Union[_models.TestRun, JSON, IO[bytes]],
        *,
        old_test_run_id: Optional[str] = None,
        **kwargs: Any
    ) -> AsyncLROPoller[_models.TestRun]:
        """Create and start a new test run with the given test run Id.

        Create and start a new test run with the given test run Id.

        :param test_run_id: Unique test run identifier for the load test run, must contain only
         lower-case alphabetic, numeric, underscore or hyphen characters. Required.
        :type test_run_id: str
        :param body: The resource instance. Is one of the following types: TestRun, JSON, IO[bytes]
         Required.
        :type body: ~azure.developer.loadtesting.models.TestRun or JSON or IO[bytes]
        :keyword old_test_run_id: Existing test run identifier that should be rerun, if this is
         provided, the
         test will run with the JMX file, configuration and app components from the
         existing test run. You can override the configuration values for new test run
         in the request body. Default value is None.
        :paramtype old_test_run_id: str
        :return: An instance of AsyncLROPoller. Call `result()` on the poller object to return a :class:`~azure.developer.loadtesting.models.TestRun`.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.developer.loadtesting.models.TestRun]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        polling_interval = kwargs.pop("_polling_interval", None)
        if polling_interval is None:
            polling_interval = 5

        create_or_update_test_run_operation = await super()._begin_test_run(
            test_run_id, body, old_test_run_id=old_test_run_id, **kwargs
        )

        command = partial(self.get_test_run, test_run_id=test_run_id)

        test_run_status_polling = AsyncTestRunStatusPoller(interval=polling_interval)

        return AsyncLROPoller(
            command,
            create_or_update_test_run_operation,
            lambda *_: None,
            test_run_status_polling,
        )

    @overload
    async def begin_test_profile_run(
        self,
        test_profile_run_id: str,
        body: _models.TestProfileRun,
        *,
        content_type: str = "application/merge-patch+json",
        **kwargs: Any
    ) -> AsyncLROPoller[_models.TestProfileRun]:
        """Create and start a new test profile run.

        Create and start a new test profile run with the given test profile run Id.

        :param test_profile_run_id: Unique identifier for the test profile run, must contain only
         lower-case alphabetic, numeric, underscore or hyphen characters. Required.
        :type test_profile_run_id: str
        :param body: The resource instance. Required.
        :type body: ~azure.developer.loadtesting.models.TestProfileRun
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/merge-patch+json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller. Call `result()` on the poller object to return a :class:`~azure.developer.loadtesting.models.TestProfileRun`.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.developer.loadtesting.models.TestProfileRun]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_test_profile_run(
        self, test_profile_run_id: str, body: JSON, *, content_type: str = "application/merge-patch+json", **kwargs: Any
    ) -> AsyncLROPoller[_models.TestProfileRun]:
        """Create and start a new test profile run.

        Create and start a new test profile run with the given test profile run Id.

        :param test_profile_run_id: Unique identifier for the test profile run, must contain only
         lower-case alphabetic, numeric, underscore or hyphen characters. Required.
        :type test_profile_run_id: str
        :param body: The resource instance. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/merge-patch+json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller. Call `result()` on the poller object to return a :class:`~azure.developer.loadtesting.models.TestProfileRun`.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.developer.loadtesting.models.TestProfileRun]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_test_profile_run(
        self,
        test_profile_run_id: str,
        body: IO[bytes],
        *,
        content_type: str = "application/merge-patch+json",
        **kwargs: Any
    ) -> AsyncLROPoller[_models.TestProfileRun]:
        """Create and start a new test profile run.

        Create and start a new test profile run with the given test profile run Id.

        :param test_profile_run_id: Unique identifier for the test profile run, must contain only
         lower-case alphabetic, numeric, underscore or hyphen characters. Required.
        :type test_profile_run_id: str
        :param body: The resource instance. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/merge-patch+json".
        :paramtype content_type: str
        :return: An instance of AsyncLROPoller. Call `result()` on the poller object to return a :class:`~azure.developer.loadtesting.models.TestProfileRun`.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.developer.loadtesting.models.TestProfileRun]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def begin_test_profile_run(
        self, test_profile_run_id: str, body: Union[_models.TestProfileRun, JSON, IO[bytes]], **kwargs: Any
    ) -> AsyncLROPoller[_models.TestProfileRun]:
        """Create and start a new test profile run.

        Create and start a new test profile run with the given test profile run Id.

        :param test_profile_run_id: Unique identifier for the test profile run, must contain only
         lower-case alphabetic, numeric, underscore or hyphen characters. Required.
        :type test_profile_run_id: str
        :param body: The resource instance. Is one of the following types: TestProfileRun, JSON,
         IO[bytes] Required.
        :type body: ~azure.developer.loadtesting.models.TestProfileRun or JSON or IO[bytes]
        :return: An instance of AsyncLROPoller. Call `result()` on the poller object to return a :class:`~azure.developer.loadtesting.models.TestProfileRun`.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.developer.loadtesting.models.TestProfileRun]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        polling_interval = kwargs.pop("_polling_interval", None)

        if polling_interval is None:
            polling_interval = 5

        create_or_update_test_profile_run_operation = await super()._begin_test_profile_run(
            test_profile_run_id, body, **kwargs
        )

        command = partial(self.get_test_profile_run, test_profile_run_id=test_profile_run_id)

        test_profile_run_status_polling = AsyncTestProfileRunStatusPoller(interval=polling_interval)
        return AsyncLROPoller(
            command,
            create_or_update_test_profile_run_operation,
            lambda *_: None,
            test_profile_run_status_polling,
        )


# Add all objects you want publicly available to users at this package level
__all__: List[str] = ["LoadTestAdministrationClientOperationsMixin", "LoadTestRunClientOperationsMixin"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
