# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access

from typing import Any, Iterable

from azure.ai.ml._restclient.v2023_04_01_preview import AzureMachineLearningWorkspaces as ServiceClient042023Preview
from azure.ai.ml._scope_dependent_operations import (
    OperationConfig,
    OperationsContainer,
    OperationScope,
    _ScopeDependentOperations,
)

from azure.ai.ml._telemetry import ActivityType, monitor_with_activity, monitor_with_telemetry_mixin
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.entities import Job, JobSchedule, Schedule
from azure.ai.ml.entities._monitoring.schedule import MonitorSchedule
from azure.ai.ml.entities._monitoring.target import MonitoringTarget
from azure.ai.ml.entities._monitoring.signals import TargetDataset
from azure.ai.ml.entities._monitoring.input_data import MonitorInputData
from azure.ai.ml.entities._inputs_outputs.input import Input
from azure.ai.ml.exceptions import ScheduleException, ErrorCategory, ErrorTarget
from azure.core.credentials import TokenCredential
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace

from .._restclient.v2022_10_01.models import ScheduleListViewType
from .._utils._arm_id_utils import is_ARM_id_for_parented_resource, AMLNamedArmId
from .._utils.utils import snake_to_camel
from .._utils._azureml_polling import AzureMLPolling
from ..constants._common import (
    ARM_ID_PREFIX,
    AzureMLResourceType,
    LROConfigurations,
    NAMED_RESOURCE_ID_FORMAT_WITH_PARENT,
    AZUREML_RESOURCE_PROVIDER,
)
from ..constants._monitoring import (
    MonitorSignalType,
    DEPLOYMENT_MODEL_INPUTS_NAME_KEY,
    DEPLOYMENT_MODEL_INPUTS_VERSION_KEY,
    DEPLOYMENT_MODEL_OUTPUTS_NAME_KEY,
    DEPLOYMENT_MODEL_OUTPUTS_VERSION_KEY,
    DEPLOYMENT_MODEL_INPUTS_COLLECTION_KEY,
    DEPLOYMENT_MODEL_OUTPUTS_COLLECTION_KEY,
    MonitorDatasetContext,
)
from . import JobOperations, OnlineDeploymentOperations, DataOperations
from ._job_ops_helper import stream_logs_until_completion
from ._operation_orchestrator import OperationOrchestrator

ops_logger = OpsLogger(__name__)
logger, module_logger = ops_logger.package_logger, ops_logger.module_logger


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
        service_client_04_2023_preview: ServiceClient042023Preview,
        all_operations: OperationsContainer,
        credential: TokenCredential,
        **kwargs: Any,
    ):
        super(ScheduleOperations, self).__init__(operation_scope, operation_config)
        ops_logger.update_info(kwargs)
        self.service_client = service_client_04_2023_preview.schedules
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

    @property
    def _online_deployment_operations(self) -> OnlineDeploymentOperations:
        return self._all_operations.get_operation(
            AzureMLResourceType.ONLINE_DEPLOYMENT, lambda x: isinstance(x, OnlineDeploymentOperations)
        )

    @property
    def _data_operations(self) -> DataOperations:
        return self._all_operations.get_operation(AzureMLResourceType.DATA, lambda x: isinstance(x, DataOperations))

    @distributed_trace
    @monitor_with_activity(logger, "Schedule.List", ActivityType.PUBLICAPI)
    def list(
        self,
        *,
        list_view_type: ScheduleListViewType = ScheduleListViewType.ENABLED_ONLY,  # pylint: disable=unused-argument
        **kwargs,
    ) -> Iterable[Schedule]:
        """List schedules in specified workspace.

        :param list_view_type: View type for including/excluding (for example)
            archived schedules. Default: ENABLED_ONLY.
        :type list_view_type: Optional[ScheduleListViewType]
        :return: An iterator to list Schedule.
        :rtype: Iterable[Schedule]
        """

        def safe_from_rest_object(objs):
            result = []
            for obj in objs:
                try:
                    result.append(Schedule._from_rest_object(obj))
                except Exception as e:  # pylint: disable=broad-except
                    print(f"Translate {obj.name} to Schedule failed with: {e}")
            return result

        return self.service_client.list(
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            list_view_type=list_view_type,
            cls=safe_from_rest_object,
            **self._kwargs,
            **kwargs,
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
    @monitor_with_activity(logger, "Schedule.Delete", ActivityType.PUBLICAPI)
    def begin_delete(
        self,
        name: str,
        **kwargs,
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
            **kwargs,
        )
        return poller

    @distributed_trace
    @monitor_with_telemetry_mixin(logger, "Schedule.Get", ActivityType.PUBLICAPI)
    def get(
        self,
        name: str,
        **kwargs,
    ) -> Schedule:
        """Get a schedule.

        :param name: Schedule name.
        :type name: str
        :return: The schedule object.
        :rtype: Schedule
        """
        return self.service_client.get(
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            name=name,
            cls=lambda _, obj, __: Schedule._from_rest_object(obj),
            **self._kwargs,
            **kwargs,
        )

    @distributed_trace
    @monitor_with_telemetry_mixin(logger, "Schedule.CreateOrUpdate", ActivityType.PUBLICAPI)
    def begin_create_or_update(
        self,
        schedule: Schedule,
        **kwargs,
    ) -> LROPoller[Schedule]:
        """Create or update schedule.

        :param schedule: Schedule definition.
        :type schedule: Schedule
        :return: An instance of LROPoller that returns Schedule if no_wait=True, or Schedule if no_wait=False
        :rtype: Union[LROPoller, Schedule]
        :rtype: Union[LROPoller, ~azure.ai.ml.entities.Schedule]
        """

        if isinstance(schedule, JobSchedule):
            schedule._validate(raise_error=True)
            if isinstance(schedule.create_job, Job):
                # Create all dependent resources for job inside schedule
                self._job_operations._resolve_arm_id_or_upload_dependencies(schedule.create_job)
        elif isinstance(schedule, MonitorSchedule):
            # resolve ARM id for target, compute, and input datasets for each signal
            self._resolve_monitor_schedule_arm_id(schedule)
        # Create schedule
        schedule_data = schedule._to_rest_object()
        poller = self.service_client.begin_create_or_update(
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            name=schedule.name,
            cls=lambda _, obj, __: Schedule._from_rest_object(obj),
            body=schedule_data,
            polling=self._get_polling(schedule.name),
            **self._kwargs,
            **kwargs,
        )
        return poller

    @distributed_trace
    @monitor_with_activity(logger, "Schedule.Enable", ActivityType.PUBLICAPI)
    def begin_enable(
        self,
        name: str,
        **kwargs,
    ) -> LROPoller[Schedule]:
        """Enable a schedule.

        :param name: Schedule name.
        :type name: str
        :return: An instance of LROPoller that returns Schedule
        :rtype: LROPoller
        """
        schedule = self.get(name=name)
        schedule._is_enabled = True
        return self.begin_create_or_update(schedule, **kwargs)

    @distributed_trace
    @monitor_with_activity(logger, "Schedule.Disable", ActivityType.PUBLICAPI)
    def begin_disable(
        self,
        name: str,
        **kwargs,
    ) -> LROPoller[Schedule]:
        """Disable a schedule.

        :param name: Schedule name.
        :type name: str
        :return: An instance of LROPoller that returns Schedule if no_wait=True, or Schedule if no_wait=False
        :rtype:  LROPoller
        """
        schedule = self.get(name=name)
        schedule._is_enabled = False
        return self.begin_create_or_update(schedule, **kwargs)

    def _resolve_monitor_schedule_arm_id(self, schedule: MonitorSchedule) -> None:
        # resolve target ARM ID
        model_inputs_name, model_outputs_name = None, None
        model_inputs_version, model_outputs_version = None, None
        mdc_input_enabled, mdc_output_enabled = False, False
        target = schedule.create_monitor.monitoring_target
        if target and target.endpoint_deployment_id:
            endpoint_name, deployment_name = self._process_and_get_endpoint_deployment_names_from_id(target)
            online_deployment = self._online_deployment_operations.get(deployment_name, endpoint_name)
            model_inputs_name = online_deployment.tags.get(DEPLOYMENT_MODEL_INPUTS_NAME_KEY)
            model_inputs_version = online_deployment.tags.get(DEPLOYMENT_MODEL_INPUTS_VERSION_KEY)
            model_outputs_name = online_deployment.tags.get(DEPLOYMENT_MODEL_OUTPUTS_NAME_KEY)
            model_outputs_version = online_deployment.tags.get(DEPLOYMENT_MODEL_OUTPUTS_VERSION_KEY)
            mdc_input_enabled_str = online_deployment.tags.get(DEPLOYMENT_MODEL_INPUTS_COLLECTION_KEY)
            mdc_output_enabled_str = online_deployment.tags.get(DEPLOYMENT_MODEL_OUTPUTS_COLLECTION_KEY)
            if mdc_input_enabled_str and mdc_input_enabled_str.lower() == "true":
                mdc_input_enabled = True
            if mdc_output_enabled_str and mdc_output_enabled_str.lower() == "true":
                mdc_output_enabled = True
        elif target and target.model_id:
            target.model_id = self._orchestrators.get_asset_arm_id(
                target.model_id,
                AzureMLResourceType.MODEL,
                register_asset=False,
            )

        if not schedule.create_monitor.monitoring_signals:
            if mdc_input_enabled and mdc_output_enabled:
                schedule._create_default_monitor_definition(
                    f"{model_inputs_name}:{model_inputs_version}",
                    self._data_operations.get(model_inputs_name, model_inputs_version).type,
                    f"{model_outputs_name}:{model_outputs_version}",
                    self._data_operations.get(model_outputs_name, model_outputs_version).type,
                )
            else:
                msg = (
                    "An ARM id for a deployment with data collector enabled for model inputs and outputs must be "
                    "given if monitoring_signals is None"
                )
                raise ScheduleException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.SCHEDULE,
                    error_category=ErrorCategory.USER_ERROR,
                )

        # resolve ARM id for each signal and populate any defaults if needed
        for signal_name, signal in schedule.create_monitor.monitoring_signals.items():
            if signal.type == MonitorSignalType.CUSTOM:
                for input_value in signal.input_datasets.values():
                    self._job_operations._resolve_job_input(input_value.input_dataset, schedule._base_path)
                    input_value.pre_processing_component = self._orchestrators.get_asset_arm_id(
                        asset=input_value.pre_processing_component, azureml_type=AzureMLResourceType.COMPONENT
                    )
                continue
            error_messages = []
            if not signal.target_dataset:
                # if there is no target dataset, we check the type of signal
                if signal.type == MonitorSignalType.DATA_DRIFT or signal.type == MonitorSignalType.DATA_QUALITY:
                    if mdc_input_enabled:
                        # if target dataset is absent and data collector for input is enabled,
                        # create a default target dataset with production model inputs as target
                        signal.target_dataset = TargetDataset(
                            dataset=MonitorInputData(
                                input_dataset=Input(
                                    path=f"{model_inputs_name}:{model_inputs_version}",
                                    type=self._data_operations.get(model_inputs_name, model_inputs_version).type,
                                ),
                                dataset_context=MonitorDatasetContext.MODEL_INPUTS,
                            ),
                        )
                    else:
                        # if target dataset is absent and data collector for input is not enabled,
                        # collect exception message
                        msg = (
                            f"A target dataset must be provided for signal with name {signal_name}"
                            f"and type {signal.type} if the monitoring_target endpoint_deployment_id is empty"
                            "or refers to a deployment for which data collection for model inputs is not enabled."
                        )
                        error_messages.append(msg)
                elif signal.type == MonitorSignalType.PREDICTION_DRIFT:
                    if mdc_output_enabled:
                        # if target dataset is absent and data collector for output is enabled,
                        # create a default target dataset with production model outputs as target
                        signal.target_dataset = TargetDataset(
                            dataset=MonitorInputData(
                                input_dataset=Input(
                                    path=f"{model_outputs_name}:{model_outputs_version}",
                                    type=self._data_operations.get(model_outputs_name, model_outputs_version).type,
                                ),
                                dataset_context=MonitorDatasetContext.MODEL_OUTPUTS,
                            ),
                        )
                    else:
                        # if target dataset is absent and data collector for output is not enabled,
                        # collect exception message
                        msg = (
                            f"A target dataset must be provided for signal with name {signal_name}"
                            f"and type {signal.type} if the monitoring_target endpoint_deployment_id is empty"
                            "or refers to a deployment for which data collection for model outputs is not enabled."
                        )
                        error_messages.append(msg)
            if error_messages:
                # if any error messages, raise an exception with all of them so user knows which signals
                # need to be fixed
                msg = "\n".join(error_messages)
                raise ScheduleException(
                    message=msg,
                    no_personal_data_message=msg,
                    ErrorTarget=ErrorTarget.SCHEDULE,
                    ErrorCategory=ErrorCategory.USER_ERROR,
                )
            self._job_operations._resolve_job_inputs(
                [signal.target_dataset.dataset.input_dataset, signal.baseline_dataset.input_dataset],
                schedule._base_path,
            )
            signal.target_dataset.dataset.pre_processing_component = self._orchestrators.get_asset_arm_id(
                asset=signal.target_dataset.dataset.pre_processing_component,
                azureml_type=AzureMLResourceType.COMPONENT,
            )
            signal.baseline_dataset.pre_processing_component = self._orchestrators.get_asset_arm_id(
                asset=signal.baseline_dataset.pre_processing_component, azureml_type=AzureMLResourceType.COMPONENT
            )

    def _process_and_get_endpoint_deployment_names_from_id(self, target: MonitoringTarget):
        target.endpoint_deployment_id = (
            target.endpoint_deployment_id[len(ARM_ID_PREFIX) :]
            if target.endpoint_deployment_id.startswith(ARM_ID_PREFIX)
            else target.endpoint_deployment_id
        )

        # if it is an ARM ID, don't process it
        if not is_ARM_id_for_parented_resource(
            target.endpoint_deployment_id,
            snake_to_camel(AzureMLResourceType.ONLINE_ENDPOINT),
            AzureMLResourceType.DEPLOYMENT,
        ):
            endpoint_name, deployment_name = target.endpoint_deployment_id.split(":")
            target.endpoint_deployment_id = NAMED_RESOURCE_ID_FORMAT_WITH_PARENT.format(
                self._subscription_id,
                self._resource_group_name,
                AZUREML_RESOURCE_PROVIDER,
                self._workspace_name,
                snake_to_camel(AzureMLResourceType.ONLINE_ENDPOINT),
                endpoint_name,
                AzureMLResourceType.DEPLOYMENT,
                deployment_name,
            )
        else:
            deployment_arm_id_entity = AMLNamedArmId(target.endpoint_deployment_id)
            endpoint_name = deployment_arm_id_entity.parent_asset_name
            deployment_name = deployment_arm_id_entity.asset_name

        return endpoint_name, deployment_name
