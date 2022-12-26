# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from functools import partial
from typing import List, IO, Optional, Any, Union

from azure.core.polling import NoPolling
from azure.core.tracing.decorator import distributed_trace

from ._operations import LoadTestAdministrationOperations as LoadTestAdministrationOperationsGenerated, JSON
from ._operations import LoadTestRunOperations as LoadTestRunOperationsGenerated
from .._polling import ValidationCheckPoller, LoadTestingLROPoller, TestRunStatusPoller
from .._serialization import Serializer

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False


class LoadTestAdministrationOperations(LoadTestAdministrationOperationsGenerated):
    """
    for performing the operations on the LoadTestAdministration Subclient
    """

    def __init__(self, *args, **kwargs):
        super(LoadTestAdministrationOperations, self).__init__(*args, **kwargs)

    @distributed_trace
    def begin_upload_test_file(
        self,
        test_id: str,
        file_name: str,
        body: IO,
        *,
        poll_for_validation_status: bool = True,
        file_type: Optional[str] = None,
        **kwargs: Any
    ) -> LoadTestingLROPoller:
        """Upload file to the test

        :param test_id: Unique id for the test
        :type test_id: str
        :param file_name: Name of the file to be uploaded
        :type file_name: str
        :param body: File content to be uploaded
        :type body: IO
        :param file_type: Type of the file to be uploaded
        :type file_type: str
        :param poll_for_validation_status: If true, polls for validation status of the file, else does not
        :type poll_for_validation_status: bool
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: An instance of LROPoller object to check the validation status of file
        :rtype: ~azure.developer.loadtesting._polling.LoadTestingLROPoller
        :raises ~azure.core.exceptions.HttpResponseError:
        :raises ~azure.core.exceptions.ResourceNotFoundError:
        """

        polling_interval = kwargs.pop("_polling_interval", None)
        if polling_interval is None:
            polling_interval = 5

        upload_test_file_operation = self.upload_test_file(
            test_id=test_id, file_name=file_name, body=body, file_type=file_type, **kwargs
        )

        command = partial(self.get_test_file, test_id=test_id, file_name=file_name)

        if poll_for_validation_status:
            create_validation_status_polling = ValidationCheckPoller(interval=polling_interval)
            return LoadTestingLROPoller(
                command, upload_test_file_operation, lambda *_: None, create_validation_status_polling
            )

        else:
            return LoadTestingLROPoller(command, upload_test_file_operation, lambda *_: None, NoPolling())


class LoadTestRunOperations(LoadTestRunOperationsGenerated):
    """
    class to perform operations on LoadTestRun
    """

    def __init__(self, *args, **kwargs):
        super(LoadTestRunOperations, self).__init__(*args, **kwargs)

    @distributed_trace
    def begin_create_or_update_test_run(
        self,
        test_run_id: str,
        body: Union[JSON, IO],
        *,
        poll_for_test_run_status=True,
        old_test_run_id: Optional[str] = None,
        **kwargs: Any
    ) -> LoadTestingLROPoller:
        """Create and start a new test run with the given name.

        Create and start a new test run with the given name.

        :param test_run_id: Unique name for the load test run, must contain only lower-case alphabetic,
         numeric, underscore or hyphen characters. Required.
        :type test_run_id: str
        :param body: Load test run model. Is either a model type or a IO type. Required.
        :type body: JSON or IO
        :keyword old_test_run_id: Existing test run identifier that should be rerun, if this is
         provided, the test will run with the JMX file, configuration and app components from the
         existing test run. You can override the configuration values for new test run in the request
         body. Default value is None.
        :param poll_for_test_run_status: If true, polls for test run status, else does not
        :type poll_for_test_run_status: bool
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

        create_or_update_test_run_operation = self.create_or_update_test_run(
            test_run_id,
            body,
            old_test_run_id=old_test_run_id,
            **kwargs
        )

        command = partial(self.get_test_run, test_run_id=test_run_id)

        if poll_for_test_run_status:
            create_test_run_polling = TestRunStatusPoller(interval=polling_interval)
            return LoadTestingLROPoller(
                command, create_or_update_test_run_operation, lambda *_: None, create_test_run_polling
            )
        else:
            return LoadTestingLROPoller(command, create_or_update_test_run_operation, lambda *_: None, NoPolling())


__all__: List[str] = ["LoadTestAdministrationOperations", "LoadTestRunOperations"]


# Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
