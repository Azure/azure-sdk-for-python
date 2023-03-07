# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access
from typing import Any, Iterable

from azure.ai.ml._restclient.v2023_02_01_preview import AzureMachineLearningWorkspaces as ServiceClient022023Preview
from azure.ai.ml._scope_dependent_operations import (
    OperationConfig,
    OperationsContainer,
    OperationScope,
    _ScopeDependentOperations,
)

# from azure.ai.ml._telemetry import ActivityType, monitor_with_activity, monitor_with_telemetry_mixin
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.entities import Job, JobSchedule
from azure.core.credentials import TokenCredential
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace

from .._restclient.v2022_10_01.models import ScheduleListViewType
from .._utils._azureml_polling import AzureMLPolling
from ..constants._common import AzureMLResourceType, LROConfigurations
from . import JobOperations
from ._job_ops_helper import stream_logs_until_completion
from ._operation_orchestrator import OperationOrchestrator

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


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
        operation_config: OperationConfig,
        service_client_02_2023_preview: ServiceClient022023Preview,
        all_operations: OperationsContainer,
        credential: TokenCredential,
        **kwargs: Any,
    ):
        super(ScheduleOperations, self).__init__(operation_scope, operation_config)
        # ops_logger.update_info(kwargs)
        self.service_client = service_client_02_2023_preview.schedules
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
        self._orchestrators = OperationOrchestrator(self._all_operations, self._operation_scope, self._operation_config)

        self._kwargs = kwargs

    @property
    def _job_operations(self) -> JobOperations:
        return self._all_operations.get_operation(AzureMLResourceType.JOB, lambda x: isinstance(x, JobOperations))

    @distributed_trace
    # @monitor_with_activity(logger, "Schedule.List", ActivityType.PUBLICAPI)
    def list(
        self,
        *,
        list_view_type: ScheduleListViewType = ScheduleListViewType.ENABLED_ONLY,  # pylint: disable=unused-argument
    ) -> Iterable[JobSchedule]:
        """List schedules in specified workspace.

        :param list_view_type: View type for including/excluding (for example)
            archived schedules. Default: ENABLED_ONLY.
        :type list_view_type: Optional[ScheduleListViewType]
        :return: An iterator to list JobSchedule.
        :rtype: Iterable[JobSchedule]
        """

        def safe_from_rest_object(objs):
            result = []
            for obj in objs:
                try:
                    result.append(JobSchedule._from_rest_object(obj))
                except Exception as e:  # pylint: disable=broad-except
                    print(f"Translate {obj.name} to JobSchedule failed with: {e}")
            return result

        return self.service_client.list(
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            list_view_type=list_view_type,
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

    @distributed_trace
    # @monitor_with_activity(logger, "Schedule.Delete", ActivityType.PUBLICAPI)
    def begin_delete(
        self,
        name,
    ) -> LROPoller[None]:
        """Delete schedule.

        :param name: Schedule name.
        :type name: str
        """
        poller = self.service_client.begin_delete(
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            name=name,
            polling=self._get_polling(name),
            **self._kwargs,
        )
        return poller

    @distributed_trace
    # @monitor_with_telemetry_mixin(logger, "Schedule.Get", ActivityType.PUBLICAPI)
    def get(
        self,
        name,
    ) -> JobSchedule:
        """Get a schedule.

        :param name: Schedule name.
        :type name: str
        :return: The schedule object.
        :rtype: JobSchedule
        """
        return self.service_client.get(
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            name=name,
            cls=lambda _, obj, __: JobSchedule._from_rest_object(obj),
            **self._kwargs,
        )

    @distributed_trace
    # @monitor_with_telemetry_mixin(logger, "Schedule.CreateOrUpdate", ActivityType.PUBLICAPI)
    def begin_create_or_update(
        self,
        schedule,
    ) -> LROPoller[JobSchedule]:
        """Create or update schedule.

        :param schedule: Schedule definition.
        :type schedule: JobSchedule
        :return: An instance of LROPoller that returns JobSchedule if no_wait=True, or JobSchedule if no_wait=False
        :rtype: Union[LROPoller, JobSchedule]
        :rtype: Union[LROPoller, ~azure.ai.ml.entities.JobSchedule]
        """

        schedule._validate(raise_error=True)
        if isinstance(schedule.create_job, Job):
            # Create all dependent resources for job inside schedule
            self._job_operations._resolve_arm_id_or_upload_dependencies(schedule.create_job)
        # Create schedule
        schedule_data = schedule._to_rest_object()
        poller = self.service_client.begin_create_or_update(
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            name=schedule.name,
            cls=lambda _, obj, __: JobSchedule._from_rest_object(obj),
            body=schedule_data,
            polling=self._get_polling(schedule.name),
            **self._kwargs,
        )
        return poller

    @distributed_trace
    # @monitor_with_activity(logger, "Schedule.Enable", ActivityType.PUBLICAPI)
    def begin_enable(
        self,
        name,
    ) -> LROPoller[JobSchedule]:
        """Enable a schedule.

        :param name: Schedule name.
        :type name: str
        :return: An instance of LROPoller that returns JobSchedule
        :rtype: LROPoller
        """
        schedule = self.get(name=name)
        schedule._is_enabled = True
        return self.begin_create_or_update(schedule)

    @distributed_trace
    # @monitor_with_activity(logger, "Schedule.Disable", ActivityType.PUBLICAPI)
    def begin_disable(
        self,
        name,
    ) -> LROPoller[JobSchedule]:
        """Disable a schedule.

        :param name: Schedule name.
        :type name: str
        :return: An instance of LROPoller that returns JobSchedule if no_wait=True, or JobSchedule if no_wait=False
        :rtype:  LROPoller
        """
        schedule = self.get(name=name)
        schedule._is_enabled = False
        return self.begin_create_or_update(schedule)
