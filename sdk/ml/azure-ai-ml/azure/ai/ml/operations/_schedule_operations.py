# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access
from datetime import datetime, timezone
from typing import Any, Iterable, List, Optional, Tuple, cast

from azure.ai.ml._restclient.v2023_06_01_preview import AzureMachineLearningWorkspaces as ServiceClient062023Preview
from azure.ai.ml._restclient.v2024_01_01_preview import AzureMachineLearningWorkspaces as ServiceClient012024Preview
from azure.ai.ml._scope_dependent_operations import (
    OperationConfig,
    OperationsContainer,
    OperationScope,
    _ScopeDependentOperations,
)
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity, monitor_with_telemetry_mixin
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.entities import Job, JobSchedule, Schedule
from azure.ai.ml.entities._inputs_outputs.input import Input
from azure.ai.ml.entities._monitoring.schedule import MonitorSchedule
from azure.ai.ml.entities._monitoring.signals import (
    BaselineDataRange,
    FADProductionData,
    ProductionData,
    ReferenceData,
    LlmData,
    GenerationTokenStatisticsSignal,
)
from azure.ai.ml.entities._monitoring.target import MonitoringTarget
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ScheduleException
from azure.core.credentials import TokenCredential
from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace

from .._restclient.v2022_10_01.models import ScheduleListViewType
from .._restclient.v2024_01_01_preview.models import TriggerOnceRequest
from .._utils._arm_id_utils import AMLNamedArmId, AMLVersionedArmId, is_ARM_id_for_parented_resource
from .._utils._azureml_polling import AzureMLPolling
from .._utils.utils import snake_to_camel
from ..constants._common import (
    ARM_ID_PREFIX,
    AZUREML_RESOURCE_PROVIDER,
    NAMED_RESOURCE_ID_FORMAT_WITH_PARENT,
    AzureMLResourceType,
    LROConfigurations,
)
from ..constants._monitoring import (
    DEPLOYMENT_MODEL_INPUTS_COLLECTION_KEY,
    DEPLOYMENT_MODEL_INPUTS_NAME_KEY,
    DEPLOYMENT_MODEL_INPUTS_VERSION_KEY,
    DEPLOYMENT_MODEL_OUTPUTS_COLLECTION_KEY,
    DEPLOYMENT_MODEL_OUTPUTS_NAME_KEY,
    DEPLOYMENT_MODEL_OUTPUTS_VERSION_KEY,
    MonitorDatasetContext,
    MonitorSignalType,
)
from ..entities._schedule.schedule import ScheduleTriggerResult
from . import DataOperations, JobOperations, OnlineDeploymentOperations
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
        service_client_06_2023_preview: ServiceClient062023Preview,
        service_client_01_2024_preview: ServiceClient012024Preview,
        all_operations: OperationsContainer,
        credential: TokenCredential,
        **kwargs: Any,
    ):
        super(ScheduleOperations, self).__init__(operation_scope, operation_config)
        ops_logger.update_info(kwargs)
        self.service_client = service_client_06_2023_preview.schedules
        # Note: Trigger once is supported since 24_01, we don't upgrade other operations' client because there are
        # some breaking changes, for example: AzMonMonitoringAlertNotificationSettings is removed.
        self.schedule_trigger_service_client = service_client_01_2024_preview.schedules
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
        return cast(
            JobOperations,
            self._all_operations.get_operation(  # type: ignore[misc]
                AzureMLResourceType.JOB, lambda x: isinstance(x, JobOperations)
            ),
        )

    @property
    def _online_deployment_operations(self) -> OnlineDeploymentOperations:
        return cast(
            OnlineDeploymentOperations,
            self._all_operations.get_operation(  # type: ignore[misc]
                AzureMLResourceType.ONLINE_DEPLOYMENT, lambda x: isinstance(x, OnlineDeploymentOperations)
            ),
        )

    @property
    def _data_operations(self) -> DataOperations:
        return cast(
            DataOperations,
            self._all_operations.get_operation(  # type: ignore[misc]
                AzureMLResourceType.DATA, lambda x: isinstance(x, DataOperations)
            ),
        )

    @distributed_trace
    @monitor_with_activity(ops_logger, "Schedule.List", ActivityType.PUBLICAPI)
    def list(
        self,
        *,
        list_view_type: ScheduleListViewType = ScheduleListViewType.ENABLED_ONLY,  # pylint: disable=unused-argument
        **kwargs: Any,
    ) -> Iterable[Schedule]:
        """List schedules in specified workspace.

        :keyword list_view_type: View type for including/excluding (for example)
            archived schedules. Default: ENABLED_ONLY.
        :type list_view_type: Optional[ScheduleListViewType]
        :return: An iterator to list Schedule.
        :rtype: Iterable[Schedule]
        """

        def safe_from_rest_object(objs: Any) -> List:
            result = []
            for obj in objs:
                try:
                    result.append(Schedule._from_rest_object(obj))
                except Exception as e:  # pylint: disable=W0718
                    print(f"Translate {obj.name} to Schedule failed with: {e}")
            return result

        return cast(
            Iterable[Schedule],
            self.service_client.list(
                resource_group_name=self._operation_scope.resource_group_name,
                workspace_name=self._workspace_name,
                list_view_type=list_view_type,
                cls=safe_from_rest_object,
                **self._kwargs,
                **kwargs,
            ),
        )

    def _get_polling(self, name: Optional[str]) -> AzureMLPolling:
        """Return the polling with custom poll interval.

        :param name: The schedule name
        :type name: str
        :return: The AzureMLPolling object
        :rtype: AzureMLPolling
        """
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
    @monitor_with_activity(ops_logger, "Schedule.Delete", ActivityType.PUBLICAPI)
    def begin_delete(
        self,
        name: str,
        **kwargs: Any,
    ) -> LROPoller[None]:
        """Delete schedule.

        :param name: Schedule name.
        :type name: str
        :return: A poller for deletion status
        :rtype: LROPoller[None]
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
    @monitor_with_telemetry_mixin(ops_logger, "Schedule.Get", ActivityType.PUBLICAPI)
    def get(
        self,
        name: str,
        **kwargs: Any,
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
    @monitor_with_telemetry_mixin(ops_logger, "Schedule.CreateOrUpdate", ActivityType.PUBLICAPI)
    def begin_create_or_update(
        self,
        schedule: Schedule,
        **kwargs: Any,
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
        schedule_data = schedule._to_rest_object()  # type: ignore
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
    @monitor_with_activity(ops_logger, "Schedule.Enable", ActivityType.PUBLICAPI)
    def begin_enable(
        self,
        name: str,
        **kwargs: Any,
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
    @monitor_with_activity(ops_logger, "Schedule.Disable", ActivityType.PUBLICAPI)
    def begin_disable(
        self,
        name: str,
        **kwargs: Any,
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

    @distributed_trace
    @monitor_with_activity(ops_logger, "Schedule.Trigger", ActivityType.PUBLICAPI)
    def trigger(
        self,
        name: str,
        **kwargs: Any,
    ) -> ScheduleTriggerResult:
        """Trigger a schedule once.

        :param name: Schedule name.
        :type name: str
        :return: TriggerRunSubmissionDto, or the result of cls(response)
        :rtype: ~azure.ai.ml.entities.ScheduleTriggerResult
        """
        schedule_time = kwargs.pop("schedule_time", datetime.now(timezone.utc).isoformat())
        return self.schedule_trigger_service_client.trigger(
            name=name,
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=self._workspace_name,
            body=TriggerOnceRequest(schedule_time=schedule_time),
            cls=lambda _, obj, __: ScheduleTriggerResult._from_rest_object(obj),
            **kwargs,
        )

    def _resolve_monitor_schedule_arm_id(  # pylint:disable=too-many-branches,too-many-statements,too-many-locals
        self, schedule: MonitorSchedule
    ) -> None:
        # resolve target ARM ID
        model_inputs_name, model_outputs_name = None, None
        app_traces_name, app_traces_version = None, None
        model_inputs_version, model_outputs_version = None, None
        mdc_input_enabled, mdc_output_enabled = False, False
        target = schedule.create_monitor.monitoring_target
        if target and target.endpoint_deployment_id:
            endpoint_name, deployment_name = self._process_and_get_endpoint_deployment_names_from_id(target)
            online_deployment = self._online_deployment_operations.get(deployment_name, endpoint_name)
            deployment_data_collector = online_deployment.data_collector
            if deployment_data_collector:
                in_reg = AMLVersionedArmId(deployment_data_collector.collections.get("model_inputs").data)
                out_reg = AMLVersionedArmId(deployment_data_collector.collections.get("model_outputs").data)
                if "app_traces" in deployment_data_collector.collections:
                    app_traces = AMLVersionedArmId(deployment_data_collector.collections.get("app_traces").data)
                    app_traces_name = app_traces.asset_name
                    app_traces_version = app_traces.asset_version
                model_inputs_name = in_reg.asset_name
                model_inputs_version = in_reg.asset_version
                model_outputs_name = out_reg.asset_name
                model_outputs_version = out_reg.asset_version
                mdc_input_enabled_str = deployment_data_collector.collections.get("model_inputs").enabled
                mdc_output_enabled_str = deployment_data_collector.collections.get("model_outputs").enabled
            else:
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
            target.model_id = self._orchestrators.get_asset_arm_id(  # type: ignore
                target.model_id,
                AzureMLResourceType.MODEL,
                register_asset=False,
            )

        if not schedule.create_monitor.monitoring_signals:
            if mdc_input_enabled and mdc_output_enabled:
                schedule._create_default_monitor_definition()
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
        for signal_name, signal in schedule.create_monitor.monitoring_signals.items():  # type: ignore
            if signal.type == MonitorSignalType.GENERATION_SAFETY_QUALITY:
                for llm_data in signal.production_data:  # type: ignore[union-attr]
                    self._job_operations._resolve_job_input(llm_data.input_data, schedule._base_path)
                continue
            if signal.type == MonitorSignalType.GENERATION_TOKEN_STATISTICS:
                if not signal.production_data:  # type: ignore[union-attr]
                    # if target dataset is absent and data collector for input is enabled,
                    # create a default target dataset with production app traces as target
                    if isinstance(signal, GenerationTokenStatisticsSignal):
                        signal.production_data = LlmData(  # type: ignore[union-attr]
                            input_data=Input(
                                path=f"{app_traces_name}:{app_traces_version}",
                                type=self._data_operations.get(app_traces_name, app_traces_version).type,
                            ),
                            data_window=BaselineDataRange(lookback_window_size="P7D", lookback_window_offset="P0D"),
                        )
                self._job_operations._resolve_job_input(
                    signal.production_data.input_data, schedule._base_path  # type: ignore[union-attr]
                )
                continue
            if signal.type == MonitorSignalType.CUSTOM:
                if signal.inputs:  # type: ignore[union-attr]
                    for inputs in signal.inputs.values():  # type: ignore[union-attr]
                        self._job_operations._resolve_job_input(inputs, schedule._base_path)
                for data in signal.input_data.values():  # type: ignore[union-attr]
                    if data.input_data is not None:
                        for inputs in data.input_data.values():
                            self._job_operations._resolve_job_input(inputs, schedule._base_path)
                    data.pre_processing_component = self._orchestrators.get_asset_arm_id(
                        asset=data.pre_processing_component if hasattr(data, "pre_processing_component") else None,
                        azureml_type=AzureMLResourceType.COMPONENT,
                    )
                continue
            error_messages = []
            if not signal.production_data or not signal.reference_data:  # type: ignore[union-attr]
                # if there is no target dataset, we check the type of signal
                if signal.type in {MonitorSignalType.DATA_DRIFT, MonitorSignalType.DATA_QUALITY}:
                    if mdc_input_enabled:
                        if not signal.production_data:  # type: ignore[union-attr]
                            # if target dataset is absent and data collector for input is enabled,
                            # create a default target dataset with production model inputs as target
                            signal.production_data = ProductionData(  # type: ignore[union-attr]
                                input_data=Input(
                                    path=f"{model_inputs_name}:{model_inputs_version}",
                                    type=self._data_operations.get(model_inputs_name, model_inputs_version).type,
                                ),
                                data_context=MonitorDatasetContext.MODEL_INPUTS,
                                data_window=BaselineDataRange(
                                    lookback_window_size="default", lookback_window_offset="P0D"
                                ),
                            )
                        if not signal.reference_data:  # type: ignore[union-attr]
                            signal.reference_data = ReferenceData(  # type: ignore[union-attr]
                                input_data=Input(
                                    path=f"{model_inputs_name}:{model_inputs_version}",
                                    type=self._data_operations.get(model_inputs_name, model_inputs_version).type,
                                ),
                                data_context=MonitorDatasetContext.MODEL_INPUTS,
                                data_window=BaselineDataRange(
                                    lookback_window_size="default", lookback_window_offset="default"
                                ),
                            )
                    elif not mdc_input_enabled and not (
                        signal.production_data and signal.reference_data  # type: ignore[union-attr]
                    ):
                        # if target or baseline dataset is absent and data collector for input is not enabled,
                        # collect exception message
                        msg = (
                            f"A target and baseline dataset must be provided for signal with name {signal_name}"
                            f"and type {signal.type} if the monitoring_target endpoint_deployment_id is empty"
                            "or refers to a deployment for which data collection for model inputs is not enabled."
                        )
                        error_messages.append(msg)
                elif signal.type == MonitorSignalType.PREDICTION_DRIFT:
                    if mdc_output_enabled:
                        if not signal.production_data:  # type: ignore[union-attr]
                            # if target dataset is absent and data collector for output is enabled,
                            # create a default target dataset with production model outputs as target
                            signal.production_data = ProductionData(  # type: ignore[union-attr]
                                input_data=Input(
                                    path=f"{model_outputs_name}:{model_outputs_version}",
                                    type=self._data_operations.get(model_outputs_name, model_outputs_version).type,
                                ),
                                data_context=MonitorDatasetContext.MODEL_OUTPUTS,
                                data_window=BaselineDataRange(
                                    lookback_window_size="default", lookback_window_offset="P0D"
                                ),
                            )
                        if not signal.reference_data:  # type: ignore[union-attr]
                            signal.reference_data = ReferenceData(  # type: ignore[union-attr]
                                input_data=Input(
                                    path=f"{model_outputs_name}:{model_outputs_version}",
                                    type=self._data_operations.get(model_outputs_name, model_outputs_version).type,
                                ),
                                data_context=MonitorDatasetContext.MODEL_OUTPUTS,
                                data_window=BaselineDataRange(
                                    lookback_window_size="default", lookback_window_offset="default"
                                ),
                            )
                    elif not mdc_output_enabled and not (
                        signal.production_data and signal.reference_data  # type: ignore[union-attr]
                    ):
                        # if target dataset is absent and data collector for output is not enabled,
                        # collect exception message
                        msg = (
                            f"A target and baseline dataset must be provided for signal with name {signal_name}"
                            f"and type {signal.type} if the monitoring_target endpoint_deployment_id is empty"
                            "or refers to a deployment for which data collection for model outputs is not enabled."
                        )
                        error_messages.append(msg)
                elif signal.type == MonitorSignalType.FEATURE_ATTRIBUTION_DRIFT:
                    if mdc_input_enabled:
                        if not signal.production_data:  # type: ignore[union-attr]
                            # if production dataset is absent and data collector for input is enabled,
                            # create a default prod dataset with production model inputs and outputs as target
                            signal.production_data = [  # type: ignore[union-attr]
                                FADProductionData(
                                    input_data=Input(
                                        path=f"{model_inputs_name}:{model_inputs_version}",
                                        type=self._data_operations.get(model_inputs_name, model_inputs_version).type,
                                    ),
                                    data_context=MonitorDatasetContext.MODEL_INPUTS,
                                    data_window=BaselineDataRange(
                                        lookback_window_size="default", lookback_window_offset="P0D"
                                    ),
                                ),
                                FADProductionData(
                                    input_data=Input(
                                        path=f"{model_outputs_name}:{model_outputs_version}",
                                        type=self._data_operations.get(model_outputs_name, model_outputs_version).type,
                                    ),
                                    data_context=MonitorDatasetContext.MODEL_OUTPUTS,
                                    data_window=BaselineDataRange(
                                        lookback_window_size="default", lookback_window_offset="P0D"
                                    ),
                                ),
                            ]
                    elif not mdc_output_enabled and not signal.production_data:  # type: ignore[union-attr]
                        # if target dataset is absent and data collector for output is not enabled,
                        # collect exception message
                        msg = (
                            f"A production data must be provided for signal with name {signal_name}"
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
            if signal.type == MonitorSignalType.FEATURE_ATTRIBUTION_DRIFT:
                for prod_data in signal.production_data:  # type: ignore[union-attr]
                    self._job_operations._resolve_job_input(prod_data.input_data, schedule._base_path)
                    prod_data.pre_processing_component = self._orchestrators.get_asset_arm_id(  # type: ignore
                        asset=prod_data.pre_processing_component,  # type: ignore[union-attr]
                        azureml_type=AzureMLResourceType.COMPONENT,
                    )
                self._job_operations._resolve_job_input(
                    signal.reference_data.input_data, schedule._base_path  # type: ignore[union-attr]
                )
                signal.reference_data.pre_processing_component = self._orchestrators.get_asset_arm_id(  # type: ignore
                    asset=signal.reference_data.pre_processing_component,  # type: ignore[union-attr]
                    azureml_type=AzureMLResourceType.COMPONENT,
                )
                continue

            self._job_operations._resolve_job_inputs(
                [signal.production_data.input_data, signal.reference_data.input_data],  # type: ignore[union-attr]
                schedule._base_path,
            )
            signal.production_data.pre_processing_component = self._orchestrators.get_asset_arm_id(  # type: ignore
                asset=signal.production_data.pre_processing_component,  # type: ignore[union-attr]
                azureml_type=AzureMLResourceType.COMPONENT,
            )
            signal.reference_data.pre_processing_component = self._orchestrators.get_asset_arm_id(  # type: ignore
                asset=signal.reference_data.pre_processing_component,  # type: ignore[union-attr]
                azureml_type=AzureMLResourceType.COMPONENT,
            )

    def _process_and_get_endpoint_deployment_names_from_id(self, target: MonitoringTarget) -> Tuple:
        target.endpoint_deployment_id = (
            target.endpoint_deployment_id[len(ARM_ID_PREFIX) :]  # type: ignore
            if target.endpoint_deployment_id is not None and target.endpoint_deployment_id.startswith(ARM_ID_PREFIX)
            else target.endpoint_deployment_id
        )

        # if it is an ARM ID, don't process it
        if not is_ARM_id_for_parented_resource(
            target.endpoint_deployment_id,
            snake_to_camel(AzureMLResourceType.ONLINE_ENDPOINT),
            AzureMLResourceType.DEPLOYMENT,
        ):
            endpoint_name, deployment_name = target.endpoint_deployment_id.split(":")  # type: ignore
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
