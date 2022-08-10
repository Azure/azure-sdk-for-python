# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
from typing import Iterable

from azure.ai.ml._restclient.runhistory import AzureMachineLearningWorkspaces as RunHistoryServiceClient
from azure.ai.ml._restclient.runhistory.models import GetRunDataRequest, GetRunDataResult, Run, RunDetails
from azure.ai.ml._scope_dependent_operations import OperationScope, _ScopeDependentOperations
from azure.ai.ml.constants import AZUREML_RESOURCE_PROVIDER, NAMED_RESOURCE_ID_FORMAT, AzureMLResourceType
from azure.ai.ml.entities._job.base_job import _BaseJob
from azure.ai.ml.entities._job.job import Job
from azure.ai.ml.entities._job.job_errors import JobParsingError

module_logger = logging.getLogger(__name__)


class RunOperations(_ScopeDependentOperations):
    def __init__(self, operation_scope: OperationScope, service_client: RunHistoryServiceClient):
        super(RunOperations, self).__init__(operation_scope)
        self._operation = service_client.runs

    def get_run(self, run_id: str) -> Run:
        return self._operation.get(
            self._operation_scope.subscription_id,
            self._operation_scope.resource_group_name,
            self._workspace_name,
            run_id,
        )

    def get_run_details(self, run_id: str) -> RunDetails:
        return self._operation.get_details(
            self._operation_scope.subscription_id,
            self._operation_scope.resource_group_name,
            self._workspace_name,
            run_id,
        )

    def get_run_children(self, run_id: str) -> Iterable[_BaseJob]:
        return self._operation.get_child(
            self._subscription_id,
            self._resource_group_name,
            self._workspace_name,
            run_id,
            cls=lambda objs: [self._translate_from_rest_object(obj) for obj in objs],
        )

    def _translate_from_rest_object(self, job_object: Run) -> _BaseJob:
        """Handle errors during list operation."""
        try:
            from_rest_job = Job._from_rest_object(job_object)
            from_rest_job._id = NAMED_RESOURCE_ID_FORMAT.format(
                self._subscription_id,
                self._resource_group_name,
                AZUREML_RESOURCE_PROVIDER,
                self._workspace_name,
                AzureMLResourceType.JOB,
                from_rest_job.name,
            )
            return from_rest_job
        except JobParsingError:
            pass

    def get_run_data(self, run_id: str) -> GetRunDataResult:
        run_data_request = GetRunDataRequest(
            run_id=run_id,
            select_run_metadata=True,
            select_run_definition=True,
            select_job_specification=True,
        )
        return self._operation.get_run_data(
            self._subscription_id,
            self._resource_group_name,
            self._workspace_name,
            body=run_data_request,
        )
