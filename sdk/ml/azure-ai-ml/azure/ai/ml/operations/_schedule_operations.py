# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access
from typing import Any, Iterable, Union

from azure.ai.ml._restclient.v2022_06_01_preview import AzureMachineLearningWorkspaces as ServiceClient062022Preview
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope, _ScopeDependentOperations
from azure.ai.ml._telemetry import (
    AML_INTERNAL_LOGGER_NAMESPACE,
    ActivityType,
    monitor_with_activity,
    monitor_with_telemetry_mixin,
)
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.entities import Job, JobSchedule
from azure.core.credentials import TokenCredential
from azure.core.polling import LROPoller

from .._utils._azureml_polling import AzureMLPolling
from ..constants._common import AzureMLResourceType, LROConfigurations
from . import JobOperations
from ._job_ops_helper import stream_logs_until_completion
from ._operation_orchestrator import OperationOrchestrator

ops_logger = OpsLogger(__name__)
logger, module_logger = ops_logger.logger, ops_logger.module_logger


class ScheduleOperations(_ScopeDependentOperations):
    # pylint: disable=too-many-instance-attributes
    """
    ScheduleOperations

    You should not instantiate this class directly.
    Instead, you should create an MLClient instance that instantiates it for you and attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        service_client_06_2022_preview: ServiceClient062022Preview,
        all_operations: OperationsContainer,
        credential: TokenCredential,
        **kwargs: Any,
    ):
        super(ScheduleOperations, self).__init__(operation_scope)
        ops_logger.update_info(kwargs)
        self.service_client_06_2022_preview = service_client_06_2022_preview.schedules
        self._all_operations = all_operations
        self._stream_logs_until_completion = stream_logs_until_completion
        # Dataplane service clients are lazily created as they are needed
        self._runs_operations_client = None
        self._dataset_dataplane_operations_client = None
        self._model_dataplane_operations_client = None
        # Kwargs to propagate to dataplane service clients
        self._service_client_kwargs = kwargs.pop("_service_client_kwargs", {})
        self._api_base_url = None
        self._container = "azureml"
        self._credential = credential
        self._orchestrators = OperationOrchestrator(self._all_operations, self._operation_scope)

        self._kwargs = kwargs

    @property
    def _job_operations(self) -> JobOperations:
        return self._all_operations.get_operation(AzureMLResourceType.JOB, lambda x: isinstance(x, JobOperations))

    @monitor_with_activity(logger, "Schedule.List", ActivityType.PUBLICAPI)
    def list(self) -> Iterable[JobSchedule]:
        """List schedules in specified workspace.

        :return: An iterator to list JobSchedule.
        :rtype: Iterable[JobSchedule]
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        def safe_from_rest_object(objs):
            result = []
            for obj in objs:
                try:
                    result.append(JobSchedule._from_rest_object(obj))
                except Exception as e:  # pylint: disable=broad-except
                    print(f"Translate {obj.name} to JobSchedule failed with: {e}")
            return result

        return self.service_client_06_2022_preview.list(
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            cls=safe_from_rest_object,
            **self._kwargs,
        )

    def _get_polling(self, name):
        """Return the polling with custom poll interval."""
        path_format_arguments = {
            "scheduleName": name,
            "resourceGroupName": self._resource_group_name,
            "workspaceName": self._workspace_name,
        }
        return AzureMLPolling(
            LROConfigurations.POLL_INTERVAL,
            path_format_arguments=path_format_arguments,
        )

    @monitor_with_activity(logger, "Schedule.Delete", ActivityType.PUBLICAPI)
    def begin_delete(
        self,
        name,
        *,
        no_wait=False,
    ) -> None:
        """Delete schedule.

        :param name: Schedule name.
        :type name: str
        :param no_wait: Wait for operation completion or not, default to False.
        :type no_wait: bool
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        poller = self.service_client_06_2022_preview.begin_delete(
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            name=name,
            polling=self._get_polling(name),
            **self._kwargs,
        )
        if no_wait:
            module_logger.info("Schedule %r delete request initiated.\n", name)
            return
        poller.result()

    @monitor_with_telemetry_mixin(logger, "Schedule.Get", ActivityType.PUBLICAPI)
    def get(
        self,
        name,
    ) -> JobSchedule:
        """Get a schedule.

        :param name: Schedule name.
        :type name: str
        :return: The schedule object.
        :rtype: JobSchedule
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self.service_client_06_2022_preview.get(
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            name=name,
            cls=lambda _, obj, __: JobSchedule._from_rest_object(obj),
            **self._kwargs,
        )

    @monitor_with_telemetry_mixin(logger, "Schedule.CreateOrUpdate", ActivityType.PUBLICAPI)
    def begin_create_or_update(
        self,
        schedule,
        *,
        no_wait=False,
    ) -> Union[LROPoller, JobSchedule]:
        """Create or update schedule.

        :param schedule: Schedule definition.
        :type schedule: JobSchedule
        :param no_wait: Wait for operation completion or not, default to False.
        :type no_wait: bool
        :return: An instance of LROPoller that returns JobSchedule if no_wait=True, or JobSchedule if no_wait=False
        :rtype: Union[LROPoller, JobSchedule]
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        schedule._validate(raise_error=True)
        if isinstance(schedule.create_job, Job):
            # Create all dependent resources for job inside schedule
            self._job_operations._resolve_arm_id_or_upload_dependencies(schedule.create_job)
        # Create schedule
        schedule_data = schedule._to_rest_object()
        poller = self.service_client_06_2022_preview.begin_create_or_update(
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            name=schedule.name,
            cls=lambda _, obj, __: JobSchedule._from_rest_object(obj),
            body=schedule_data,
            polling=self._get_polling(schedule.name),
            **self._kwargs,
        )
        if no_wait:
            module_logger.info(
                "Schedule create/update request initiated. "
                "Status can be checked using `az ml schedule show -n %s`\n",
                schedule.name,
            )
            return poller
        return poller.result()

    @monitor_with_activity(logger, "Schedule.Enable", ActivityType.PUBLICAPI)
    def begin_enable(
        self,
        name,
        *,
        no_wait=False,
    ) -> Union[LROPoller, JobSchedule]:
        """Enable a schedule.

        :param name: Schedule name.
        :type name: str
        :return: An instance of LROPoller that returns JobSchedule if no_wait=True, or JobSchedule if no_wait=False
        :param no_wait: Wait for operation completion or not, default to False.
        :type no_wait: bool
        :rtype: Union[LROPoller, JobSchedule]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        schedule = self.get(name=name)
        schedule._is_enabled = True
        return self.begin_create_or_update(schedule, no_wait=no_wait)

    @monitor_with_activity(logger, "Schedule.Disable", ActivityType.PUBLICAPI)
    def begin_disable(
        self,
        name,
        *,
        no_wait=False,
    ) -> Union[LROPoller, JobSchedule]:
        """Disable a schedule.

        :param name: Schedule name.
        :type name: str
        :param no_wait: Wait for operation completion or not, default to False.
        :type no_wait: bool
        :return: An instance of LROPoller that returns JobSchedule if no_wait=True, or JobSchedule if no_wait=False
        :rtype:  Union[LROPoller, JobSchedule]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        schedule = self.get(name=name)
        schedule._is_enabled = False
        return self.begin_create_or_update(schedule, no_wait=no_wait)
