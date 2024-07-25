# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List

"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import logging
import time
from functools import partial
from typing import List, IO, Optional, Any, Union, overload, Generic, TypeVar

from azure.core.polling import PollingMethod
from azure.core.tracing.decorator import distributed_trace
from azure.core.polling import LROPoller

from ._operations import (
    LoadTestAdministrationClientOperationsMixin as AdministrationOperationsGenerated,
    JSON,
)
from ._operations import LoadTestRunClientOperationsMixin as TestRunOperationsGenerated
from .._serialization import Serializer
from .. import models as _models

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False

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
    """polling method for long-running validation check operation."""

    def __init__(self, interval=5) -> None:
        self._resource = None
        self._command = None
        self._initial_response = None
        self._polling_interval = interval
        self._status = None
        self._termination_statuses = [
            "VALIDATION_SUCCESS",
            "VALIDATION_FAILED",
            "VALIDATION_NOT_REQUIRED",
        ]

    def _update_status(self) -> None:
        self._status = self._resource["validationStatus"]


class TestRunStatusPoller(LoadTestingPollingMethod):
    def __init__(self, interval=5) -> None:
        self._resource = None
        self._command = None
        self._initial_response = None
        self._polling_interval = interval
        self._status = None
        self._termination_statuses = ["DONE", "FAILED", "CANCELLED"]

    def _update_status(self) -> None:
        self._status = self._resource["status"]


class LoadTestAdministrationClientOperationsMixin(AdministrationOperationsGenerated):
    """
    for performing the operations on the Administration Subclient
    """

    def __init__(self, *args, **kwargs):
        super(LoadTestAdministrationClientOperationsMixin, self).__init__(*args, **kwargs)

    @distributed_trace
    def begin_upload_test_file(
        self, test_id: str, file_name: str, body: IO, *, file_type: Optional[str] = None, **kwargs: Any
    ) -> LROPoller[JSON]:
        """Upload file to the test

        :param test_id: Unique id for the test
        :type test_id: str
        :param file_name: Name of the file to be uploaded
        :type file_name: str
        :param body: File content to be uploaded
        :type body: IO
        :param file_type: Type of the file to be uploaded
        :type file_type: str
        :return: An instance of LROPoller object to check the validation status of file
        :rtype: ~azure.developer.loadtesting._polling.LoadTestingLROPoller
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError:
        """

        polling_interval = kwargs.pop("_polling_interval", None)
        if polling_interval is None:
            polling_interval = 5
        upload_test_file_operation = super().begin_upload_test_file(
            test_id=test_id, file_name=file_name, body=body, file_type=file_type, **kwargs
        )

        command = partial(self.get_test_file, test_id=test_id, file_name=file_name)

        create_validation_status_polling = ValidationCheckPoller(interval=polling_interval)
        return LROPoller(
            command,
            upload_test_file_operation,
            lambda *_: None,
            create_validation_status_polling,
        )


class LoadTestRunClientOperationsMixin(TestRunOperationsGenerated):
    """
    class to perform operations on TestRun
    """

    def __init__(self, *args, **kwargs):
        super(LoadTestRunClientOperationsMixin, self).__init__(*args, **kwargs)

    @overload
    def begin_test_profile_run(
        self,
        test_profile_run_id: str,
        body: _models.TestProfileRun,
        *,
        content_type: Optional[str] = None,
        **kwargs: Any
    ) -> LROPoller[JSON]:
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

        :return: TestProfileRun. The TestProfileRun is compatible with MutableMapping
        :rtype: ~azure.developer.loadtesting.models.TestProfileRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        polling_interval = kwargs.pop("_polling_interval", None)
        if polling_interval is None:
            polling_interval = 5
        create_or_update_test_profile_run_operation = super().begin_test_profile_run(
            test_profile_run_id, body, content_type=content_type, **kwargs
        )
        command = partial(self.get_test_profile_run, test_profile_run_id=test_profile_run_id)

        create_test_profile_run_polling = TestRunStatusPoller(interval=polling_interval)
        return LROPoller(
            command,
            create_or_update_test_profile_run_operation,
            lambda *_: None,
            create_test_profile_run_polling,
        )

    @overload
    def begin_test_profile_run(
        self, test_profile_run_id: str, body: JSON, *, content_type: Optional[str] = None, **kwargs: Any
    ) -> LROPoller[JSON]:
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

        :return: TestProfileRun. The TestProfileRun is compatible with MutableMapping
        :rtype: ~azure.developer.loadtesting.models.TestProfileRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        polling_interval = kwargs.pop("_polling_interval", None)
        if polling_interval is None:
            polling_interval = 5
        create_or_update_test_profile_run_operation = super().begin_test_profile_run(
            test_profile_run_id, body, content_type=content_type, **kwargs
        )
        command = partial(self.get_test_profile_run, test_profile_run_id=test_profile_run_id)

        create_test_profile_run_polling = TestRunStatusPoller(interval=polling_interval)
        return LROPoller(
            command,
            create_or_update_test_profile_run_operation,
            lambda *_: None,
            create_test_profile_run_polling,
        )

    @overload
    def begin_test_profile_run(
        self, test_profile_run_id: str, body: IO[bytes], *, content_type: Optional[str] = None, **kwargs: Any
    ) -> LROPoller[JSON]:
        """Create and start a new test profile run.

        Create and start a new test profile run with the given test profile run Id.

        :param test_profile_run_id: Unique identifier for the test profile run, must contain only
         lower-case alphabetic, numeric, underscore or hyphen characters. Required.
        :type test_profile_run_id: str
        :param body: The resource instance. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/merge-patch+json".
        :paramtype content_type: str

        :return: TestProfileRun. The TestProfileRun is compatible with MutableMapping
        :rtype: ~azure.developer.loadtesting.models.TestProfileRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        polling_interval = kwargs.pop("_polling_interval", None)
        if polling_interval is None:
            polling_interval = 5
        create_or_update_test_profile_run_operation = super().begin_test_profile_run(
            test_profile_run_id, body, content_type=content_type, **kwargs
        )
        command = partial(self.get_test_profile_run, test_profile_run_id=test_profile_run_id)

        create_test_profile_run_polling = TestRunStatusPoller(interval=polling_interval)
        return LROPoller(
            command,
            create_or_update_test_profile_run_operation,
            lambda *_: None,
            create_test_profile_run_polling,
        )

    @distributed_trace
    def begin_test_profile_run(
        self,
        test_profile_run_id: str,
        body: Union[_models.TestProfileRun, JSON, IO[bytes]],
        *,
        content_type: Optional[str] = None,
        **kwargs: Any
    ) -> LROPoller[JSON]:
        """Create and start a new test profile run.

        Create and start a new test profile run with the given test profile run Id.

        :param test_profile_run_id: Unique identifier for the test profile run, must contain only
         lower-case alphabetic, numeric, underscore or hyphen characters. Required.
        :type test_profile_run_id: str
        :param body: The resource instance. Required.
        :type body: ~azure.developer.loadtesting.models.TestProfileRun or JSON or IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/merge-patch+json".
        :paramtype content_type: str

        :return: TestProfileRun. The TestProfileRun is compatible with MutableMapping
        :rtype: ~azure.developer.loadtesting.models.TestProfileRun
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        polling_interval = kwargs.pop("_polling_interval", None)
        if polling_interval is None:
            polling_interval = 5
        create_or_update_test_profile_run_operation = super().begin_test_profile_run(
            test_profile_run_id, body, content_type=content_type, **kwargs
        )
        command = partial(self.get_test_profile_run, test_profile_run_id=test_profile_run_id)

        create_test_profile_run_polling = TestRunStatusPoller(interval=polling_interval)
        return LROPoller(
            command,
            create_or_update_test_profile_run_operation,
            lambda *_: None,
            create_test_profile_run_polling,
        )

    @overload
    def begin_test_run(
        self, test_run_id: str, body: _models.TestRun, *, old_test_run_id: Optional[str] = None, **kwargs: Any
    ) -> LROPoller[JSON]:
        """Create and start a new test run with the given name.

        Create and start a new test run with the given name.

        :param test_run_id: Unique name for the load test run, must contain only lower-case alphabetic,
         numeric, underscore or hyphen characters. Required.
        :type test_run_id: str
        :param body: The resource instance. Required.
        :type body:  ~azure.developer.loadtesting.models.TestRun
        :keyword old_test_run_id: Existing test run identifier that should be rerun, if this is
         provided, the test will run with the JMX file, configuration and app components from the
         existing test run. You can override the configuration values for new test run in the request
         body. Default value is None.
        :paramtype old_test_run_id: str
        :keyword content_type: Body Parameter content-type. Known values are:
         'application/merge-patch+json'. Default value is None.
        :paramtype content_type: str

        :rtype: ~azure.developer.loadtesting._polling.LoadTestingLROPoller
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError:
        """

        polling_interval = kwargs.pop("_polling_interval", None)
        if polling_interval is None:
            polling_interval = 5
        create_or_update_test_run_operation = super().begin_test_run(
            test_run_id, body, old_test_run_id=old_test_run_id, **kwargs
        )
        command = partial(self.get_test_run, test_run_id=test_run_id)

        create_test_run_polling = TestRunStatusPoller(interval=polling_interval)
        return LROPoller(
            command,
            create_or_update_test_run_operation,
            lambda *_: None,
            create_test_run_polling,
        )

    @overload
    def begin_test_run(
        self, test_run_id: str, body: JSON, *, old_test_run_id: Optional[str] = None, **kwargs: Any
    ) -> LROPoller[JSON]:
        """Create and start a new test run with the given name.

        Create and start a new test run with the given name.

        :param test_run_id: Unique name for the load test run, must contain only lower-case alphabetic,
         numeric, underscore or hyphen characters. Required.
        :type test_run_id: str
        :param body: The resource instance. Required.
        :type body: JSON
        :keyword old_test_run_id: Existing test run identifier that should be rerun, if this is
         provided, the test will run with the JMX file, configuration and app components from the
         existing test run. You can override the configuration values for new test run in the request
         body. Default value is None.
        :paramtype old_test_run_id: str
        :keyword content_type: Body Parameter content-type. Known values are:
         'application/merge-patch+json'. Default value is None.
        :paramtype content_type: str

        :rtype: ~azure.developer.loadtesting._polling.LoadTestingLROPoller
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError:
        """

        polling_interval = kwargs.pop("_polling_interval", None)
        if polling_interval is None:
            polling_interval = 5
        create_or_update_test_run_operation = super().begin_test_run(
            test_run_id, body, old_test_run_id=old_test_run_id, **kwargs
        )
        command = partial(self.get_test_run, test_run_id=test_run_id)

        create_test_run_polling = TestRunStatusPoller(interval=polling_interval)
        return LROPoller(
            command,
            create_or_update_test_run_operation,
            lambda *_: None,
            create_test_run_polling,
        )

    @overload
    def begin_test_run(
        self, test_run_id: str, body: IO[bytes], *, old_test_run_id: Optional[str] = None, **kwargs: Any
    ) -> LROPoller[JSON]:
        """Create and start a new test run with the given name.

        Create and start a new test run with the given name.

        :param test_run_id: Unique name for the load test run, must contain only lower-case alphabetic,
         numeric, underscore or hyphen characters. Required.
        :type test_run_id: str
        :param body: The resource instance. Required.
        :type body: IO[bytes]
        :keyword old_test_run_id: Existing test run identifier that should be rerun, if this is
         provided, the test will run with the JMX file, configuration and app components from the
         existing test run. You can override the configuration values for new test run in the request
         body. Default value is None.
        :paramtype old_test_run_id: str
        :keyword content_type: Body Parameter content-type. Known values are:
         'application/merge-patch+json'. Default value is None.
        :paramtype content_type: str

        :rtype: ~azure.developer.loadtesting._polling.LoadTestingLROPoller
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError:
        """

        polling_interval = kwargs.pop("_polling_interval", None)
        if polling_interval is None:
            polling_interval = 5
        create_or_update_test_run_operation = super().begin_test_run(
            test_run_id, body, old_test_run_id=old_test_run_id, **kwargs
        )
        command = partial(self.get_test_run, test_run_id=test_run_id)

        create_test_run_polling = TestRunStatusPoller(interval=polling_interval)
        return LROPoller(
            command,
            create_or_update_test_run_operation,
            lambda *_: None,
            create_test_run_polling,
        )

    @distributed_trace
    def begin_test_run(
        self,
        test_run_id: str,
        body: Union[_models.TestRun, JSON, IO[bytes]],
        *,
        old_test_run_id: Optional[str] = None,
        **kwargs: Any
    ) -> LROPoller[JSON]:
        """Create and start a new test run with the given name.

        Create and start a new test run with the given name.

        :param test_run_id: Unique name for the load test run, must contain only lower-case alphabetic,
         numeric, underscore or hyphen characters. Required.
        :type test_run_id: str
        :param body: The resource instance. Is one of the following types: TestRun, JSON, IO[bytes]
         Required.
        :type body: ~azure.developer.loadtesting.models.TestRun or JSON or IO[bytes]
        :keyword old_test_run_id: Existing test run identifier that should be rerun, if this is
         provided, the test will run with the JMX file, configuration and app components from the
         existing test run. You can override the configuration values for new test run in the request
         body. Default value is None.
        :paramtype old_test_run_id: str
        :keyword content_type: Body Parameter content-type. Known values are:
         'application/merge-patch+json'. Default value is None.
        :paramtype content_type: str

        :rtype: ~azure.developer.loadtesting._polling.LoadTestingLROPoller
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError:
        """

        polling_interval = kwargs.pop("_polling_interval", None)
        if polling_interval is None:
            polling_interval = 5
        create_or_update_test_run_operation = super().begin_test_run(
            test_run_id, body, old_test_run_id=old_test_run_id, **kwargs
        )
        command = partial(self.get_test_run, test_run_id=test_run_id)

        create_test_run_polling = TestRunStatusPoller(interval=polling_interval)
        return LROPoller(
            command,
            create_or_update_test_run_operation,
            lambda *_: None,
            create_test_run_polling,
        )


__all__: List[str] = [
    "LoadTestAdministrationClientOperationsMixin",
    "LoadTestRunClientOperationsMixin",
]


# Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
