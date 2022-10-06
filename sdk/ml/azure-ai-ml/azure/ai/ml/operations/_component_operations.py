# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import time
import types
from inspect import Parameter, signature
from typing import Callable, Dict, Iterable, Optional, Union

from azure.ai.ml._restclient.v2021_10_01_dataplanepreview import (
    AzureMachineLearningWorkspaces as ServiceClient102021Dataplane,
)
from azure.ai.ml._restclient.v2022_05_01 import AzureMachineLearningWorkspaces as ServiceClient052022
from azure.ai.ml._restclient.v2022_05_01.models import ListViewType
from azure.ai.ml._scope_dependent_operations import (
    OperationConfig,
    OperationsContainer,
    OperationScope,
    _ScopeDependentOperations,
)
from azure.ai.ml._utils._arm_id_utils import is_ARM_id_for_resource, is_registry_id_for_resource
from azure.ai.ml._utils._asset_utils import (
    _archive_or_restore,
    _create_or_update_autoincrement,
    _get_latest,
    _resolve_label_to_asset,
)
from azure.ai.ml._utils._azureml_polling import AzureMLPolling
from azure.ai.ml._utils._endpoint_utils import polling_wait
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.constants._common import AzureMLResourceType, LROConfigurations
from azure.ai.ml.entities import Component
from azure.ai.ml.entities._assets import Code
from azure.ai.ml.entities._validation import ValidationResult
from azure.ai.ml.exceptions import ComponentException, ErrorCategory, ErrorTarget, ValidationException

from .._utils._experimental import experimental
from .._utils.utils import is_data_binding_expression
from ..entities._component.automl_component import AutoMLComponent
from ..entities._component.pipeline_component import PipelineComponent
from ._code_operations import CodeOperations
from ._environment_operations import EnvironmentOperations
from ._operation_orchestrator import OperationOrchestrator

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class ComponentOperations(_ScopeDependentOperations):
    """ComponentOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: Union[ServiceClient052022, ServiceClient102021Dataplane],
        all_operations: OperationsContainer,
        **kwargs: Dict,
    ):
        super(ComponentOperations, self).__init__(operation_scope, operation_config)
        # if "app_insights_handler" in kwargs:
        #     logger.addHandler(kwargs.pop("app_insights_handler"))
        self._version_operation = service_client.component_versions
        self._container_operation = service_client.component_containers
        self._all_operations = all_operations
        self._init_args = kwargs
        # Maps a label to a function which given an asset name,
        # returns the asset associated with the label
        self._managed_label_resolver = {"latest": self._get_latest_version}
        self._orchestrators = OperationOrchestrator(self._all_operations, self._operation_scope, self._operation_config)

    @property
    def _code_operations(self) -> CodeOperations:
        return self._all_operations.get_operation(AzureMLResourceType.CODE, lambda x: isinstance(x, CodeOperations))

    @property
    def _environment_operations(self) -> EnvironmentOperations:
        return self._all_operations.get_operation(
            AzureMLResourceType.ENVIRONMENT,
            lambda x: isinstance(x, EnvironmentOperations),
        )

    @property
    def _job_operations(self):
        from ._job_operations import JobOperations

        return self._all_operations.get_operation(AzureMLResourceType.JOB, lambda x: isinstance(x, JobOperations))

    # @monitor_with_activity(logger, "Component.List", ActivityType.PUBLICAPI)
    def list(
        self,
        name: Union[str, None] = None,
        *,
        list_view_type: ListViewType = ListViewType.ACTIVE_ONLY,
    ) -> Iterable[Component]:
        """List specific component or components of the workspace.

        :param name: Component name, if not set, list all components of the workspace
        :type name: Optional[str]
        :param list_view_type: View type for including/excluding (for example) archived components.
            Default: ACTIVE_ONLY.
        :type list_view_type: Optional[ListViewType]
        :return: An iterator like instance of component objects
        :rtype: ~azure.core.paging.ItemPaged[Component]
        """

        if name:
            return (
                self._version_operation.list(
                    name=name,
                    resource_group_name=self._resource_group_name,
                    registry_name=self._registry_name,
                    **self._init_args,
                    cls=lambda objs: [Component._from_rest_object(obj) for obj in objs],
                )
                if self._registry_name
                else self._version_operation.list(
                    name=name,
                    resource_group_name=self._resource_group_name,
                    workspace_name=self._workspace_name,
                    list_view_type=list_view_type,
                    **self._init_args,
                    cls=lambda objs: [Component._from_rest_object(obj) for obj in objs],
                )
            )
        return (
            self._container_operation.list(
                resource_group_name=self._resource_group_name,
                registry_name=self._registry_name,
                **self._init_args,
                cls=lambda objs: [Component._from_container_rest_object(obj) for obj in objs],
            )
            if self._registry_name
            else self._container_operation.list(
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                list_view_type=list_view_type,
                **self._init_args,
                cls=lambda objs: [Component._from_container_rest_object(obj) for obj in objs],
            )
        )

    # @monitor_with_telemetry_mixin(logger, "Component.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, version: Optional[str] = None, label: Optional[str] = None) -> Component:
        """Returns information about the specified component.

        :param name: Name of the code component.
        :type name: str
        :param version: Version of the component.
        :type version: Optional[str]
        :param label: Label of the component. (mutually exclusive with version)
        :type label: Optional[str]
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Component cannot be successfully
            identified and retrieved. Details will be provided in the error message.
        :return: The specified component object.
        :rtype: ~azure.ai.ml.entities.Component
        """
        if version and label:
            msg = "Cannot specify both version and label."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.COMPONENT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )

        if label:
            return _resolve_label_to_asset(self, name, label)

        if not version:
            msg = "Must provide either version or label."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.COMPONENT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        result = (
            self._version_operation.get(
                name=name,
                version=version,
                resource_group_name=self._resource_group_name,
                registry_name=self._registry_name,
                **self._init_args,
            )
            if self._registry_name
            else self._version_operation.get(
                name=name,
                version=version,
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                **self._init_args,
            )
        )
        component = Component._from_rest_object(result)
        return component

    @experimental
    # @monitor_with_telemetry_mixin(logger, "Component.Validate", ActivityType.PUBLICAPI)
    # pylint: disable=no-self-use
    def validate(
        self,
        component: Union[Component, types.FunctionType],
        raise_on_failure: bool = False,
    ) -> ValidationResult:
        """validate a specified component. if there are inline defined
        entities, e.g. Environment, Code, they won't be created.

        :param component: The component object or a mldesigner component function that generates component object
        :type component: Union[Component, types.FunctionType]
        :param raise_on_failure: whether to raise exception on validation error
        :type raise_on_failure: bool
        :return: All validation errors
        :type: ValidationResult
        """
        return self._validate(component, raise_on_failure=raise_on_failure)

    # @monitor_with_telemetry_mixin(logger, "Component.Validate", ActivityType.INTERNALCALL)
    def _validate(  # pylint: disable=no-self-use
        self,
        component: Union[Component, types.FunctionType],
        raise_on_failure: bool = False,
    ) -> ValidationResult:
        """Implementation of validate. Add this function to avoid calling validate() directly in create_or_update(),
        which will impact telemetry statistics & bring experimental warning in create_or_update().
        """
        # Update component when the input is a component function
        if isinstance(component, types.FunctionType):
            component = _refine_component(component)

        # local validation only for now
        # TODO: use remote call to validate the entire component after MFE API is ready
        result = component._validate(raise_error=raise_on_failure)
        result.resolve_location_for_diagnostics(component._source_path)
        return result

    # @monitor_with_telemetry_mixin(
    #     logger,
    #     "Component.CreateOrUpdate",
    #     ActivityType.PUBLICAPI,
    #     extra_keys=["is_anonymous"],
    # )
    def create_or_update(
        self, component: Union[Component, types.FunctionType], version=None, *, skip_validation: bool = False, **kwargs
    ) -> Component:
        """Create or update a specified component. if there're inline defined
        entities, e.g. Environment, Code, they'll be created together with the
        component.

        :param component: The component object or a mldesigner component function that generates component object
        :type component: Union[Component, types.FunctionType]
        :param version: The component version to override.
        :type version: str
        :param skip_validation: whether to skip validation before creating/updating the component
        :type skip_validation: bool
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Component cannot be successfully validated.
            Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.AssetException: Raised if Component assets
            (e.g. Data, Code, Model, Environment) cannot be successfully validated.
            Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.ComponentException: Raised if Component type is unsupported.
            Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.ModelException: Raised if Component model cannot be successfully validated.
            Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.EmptyDirectoryError: Raised if local path provided points to an empty directory.
        :return: The specified component object.
        :rtype: ~azure.ai.ml.entities.Component
        """
        # Update component when the input is a component function
        if isinstance(component, types.FunctionType):
            component = _refine_component(component)
        if version is not None:
            component.version = version
        if not component.version and self._registry_name:
            # version is required only when create into registry as
            # we have _auto_increment_version for workspace component.
            msg = "Component version is required for create_or_update."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.COMPONENT,
                error_category=ErrorCategory.USER_ERROR,
            )

        component._set_is_anonymous(kwargs.pop("is_anonymous", False))
        if not skip_validation:
            self._validate(component, raise_on_failure=True)

        # Create all dependent resources
        self._resolve_arm_id_or_upload_dependencies(component)

        component._update_anonymous_hash()
        rest_component_resource = component._to_rest_object()
        result = None
        try:
            if self._registry_name:
                start_time = time.time()
                path_format_arguments = {
                    "componentName": component.name,
                    "resourceGroupName": self._resource_group_name,
                    "registryName": self._registry_name,
                }
                poller = self._version_operation.begin_create_or_update(
                    name=component.name,
                    version=component.version,
                    resource_group_name=self._operation_scope.resource_group_name,
                    registry_name=self._registry_name,
                    body=rest_component_resource,
                    polling=AzureMLPolling(
                        LROConfigurations.POLL_INTERVAL,
                        path_format_arguments=path_format_arguments,
                    ),
                )
                message = f"Creating/updating registry component {component.name} with version {component.version} "
                polling_wait(poller=poller, start_time=start_time, message=message, timeout=None)

            else:
                if component._auto_increment_version:
                    result = _create_or_update_autoincrement(
                        name=component.name,
                        body=rest_component_resource,
                        version_operation=self._version_operation,
                        container_operation=self._container_operation,
                        resource_group_name=self._operation_scope.resource_group_name,
                        workspace_name=self._workspace_name,
                        **self._init_args,
                    )
                else:
                    result = self._version_operation.create_or_update(
                        name=rest_component_resource.name,
                        version=component.version,
                        resource_group_name=self._resource_group_name,
                        workspace_name=self._workspace_name,
                        body=rest_component_resource,
                        **self._init_args,
                    )
        except Exception as e:
            raise e

        if not result:
            component = self.get(name=component.name, version=component.version)
        else:
            component = Component._from_rest_object(result)
        if isinstance(component, PipelineComponent):
            self._resolve_arm_id_for_pipeline_component_jobs(component.jobs, self._orchestrators.resolve_azureml_id)
        return component

    # @monitor_with_telemetry_mixin(logger, "Component.Archive", ActivityType.PUBLICAPI)
    def archive(self, name: str, version: str = None, label: str = None) -> None:
        """Archive a component.

        :param name: Name of the component.
        :type name: str
        :param version: Version of the component.
        :type version: str
        :param label: Label of the component. (mutually exclusive with version)
        :type label: str
        """
        _archive_or_restore(
            asset_operations=self,
            version_operation=self._version_operation,
            container_operation=self._container_operation,
            is_archived=True,
            name=name,
            version=version,
            label=label,
        )

    # @monitor_with_telemetry_mixin(logger, "Component.Restore", ActivityType.PUBLICAPI)
    def restore(self, name: str, version: str = None, label: str = None) -> None:
        """Restore an archived component.

        :param name: Name of the component.
        :type name: str
        :param version: Version of the component.
        :type version: str
        :param label: Label of the component. (mutually exclusive with version)
        :type label: str
        """
        _archive_or_restore(
            asset_operations=self,
            version_operation=self._version_operation,
            container_operation=self._container_operation,
            is_archived=False,
            name=name,
            version=version,
            label=label,
        )

    def _get_latest_version(self, component_name: str) -> Component:
        """Returns the latest version of the asset with the given name.

        Latest is defined as the most recently created, not the most
        recently updated.
        """

        result = (
            _get_latest(
                component_name,
                self._version_operation,
                self._resource_group_name,
                workspace_name=None,
                registry_name=self._registry_name,
            )
            if self._registry_name
            else _get_latest(
                component_name,
                self._version_operation,
                self._resource_group_name,
                self._workspace_name,
            )
        )
        return Component._from_rest_object(result)

    def _resolve_arm_id_or_upload_dependencies(self, component: Component) -> None:
        if isinstance(component, AutoMLComponent):
            # no extra dependency for automl component
            return

        # type check for potential Job type, which is unexpected here.
        if not isinstance(component, Component):
            msg = f"Non supported component type: {type(component)}"
            raise ValidationException(
                message=msg,
                target=ErrorTarget.COMPONENT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )

        get_arm_id_and_fill_back = OperationOrchestrator(
            self._all_operations, self._operation_scope, self._operation_config
        ).get_asset_arm_id

        # resolve component's code
        _try_resolve_code_for_component(component=component, get_arm_id_and_fill_back=get_arm_id_and_fill_back)
        # resolve component's environment
        if hasattr(component, "environment"):
            # for internal component, environment may be a dict or InternalEnvironment object
            # in these two scenarios, we don't need to resolve the environment;
            # Note for not directly importing InternalEnvironment and check with `isinstance`:
            #   import from azure.ai.ml._internal will enable internal component feature for all users,
            #   therefore, use type().__name__ to avoid import and execute type check
            if (
                not isinstance(component.environment, dict)
                and not type(component.environment).__name__ == "InternalEnvironment"
            ):
                component.environment = get_arm_id_and_fill_back(
                    component.environment, azureml_type=AzureMLResourceType.ENVIRONMENT
                )

        self._resolve_arm_id_and_inputs(component)

    def _resolve_inputs_for_pipeline_component_jobs(self, jobs, base_path):
        from azure.ai.ml.entities._builders import BaseNode, Pipeline
        from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob

        for _, job_instance in jobs.items():
            # resolve inputs for each job's component
            if isinstance(job_instance, Pipeline):
                node: Pipeline = job_instance
                self._job_operations._resolve_pipeline_job_inputs(
                    node,
                    base_path,
                )
            elif isinstance(job_instance, BaseNode):
                node: BaseNode = job_instance
                self._job_operations._resolve_job_inputs(
                    map(lambda x: x._data, node.inputs.values()),
                    base_path,
                )
            elif isinstance(job_instance, AutoMLJob):
                self._job_operations._resolve_automl_job_inputs(job_instance)

    def _resolve_arm_id_for_pipeline_component_jobs(self, jobs, resolver: Callable):

        from azure.ai.ml.entities._builders import BaseNode
        from azure.ai.ml.entities._builders.control_flow_node import LoopNode
        from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
        from azure.ai.ml.entities._job.pipeline._attr_dict import try_get_non_arbitrary_attr_for_potential_attr_dict
        from azure.ai.ml.entities._job.pipeline._io import PipelineInput

        def preprocess_job(node):
            """Resolve all PipelineInput(binding from sdk) on supported fields to string."""
            # compute binding to pipeline input is supported on node.
            supported_fields = ["compute"]
            for field_name in supported_fields:
                val = try_get_non_arbitrary_attr_for_potential_attr_dict(node, field_name)
                if isinstance(val, PipelineInput):
                    # Put binding string to field
                    setattr(node, field_name, val._data_binding())

        def resolve_base_node(name, node):
            """Resolve node name, compute and component for base node."""
            # Set display name as node name
            if (
                isinstance(node.component, Component)
                and node.component._is_anonymous
                and not node.component.display_name
            ):
                node.component.display_name = name
            if isinstance(node.component, PipelineComponent):
                # Resolve nested arm id for pipeline component
                self._resolve_arm_id_and_inputs(node.component)
            else:
                # Resolve compute for other type
                # Keep data binding expression as they are
                if not is_data_binding_expression(node.compute):
                    # Get compute for each job
                    node.compute = resolver(node.compute, azureml_type=AzureMLResourceType.COMPUTE)
            # Get the component id for each job's component
            # Note: do not use node.component as Sweep don't have that
            node._component = resolver(
                node._component,
                azureml_type=AzureMLResourceType.COMPONENT,
            )

        for key, job_instance in jobs.items():
            preprocess_job(job_instance)
            if isinstance(job_instance, LoopNode):
                job_instance = job_instance.body
            if isinstance(job_instance, AutoMLJob):
                self._job_operations._resolve_arm_id_for_automl_job(job_instance, resolver, inside_pipeline=True)
            elif isinstance(job_instance, BaseNode):
                resolve_base_node(key, job_instance)
            else:
                msg = f"Non supported job type in Pipeline: {type(job_instance)}"
                raise ComponentException(
                    message=msg,
                    target=ErrorTarget.COMPONENT,
                    no_personal_data_message=msg,
                    error_category=ErrorCategory.USER_ERROR,
                )

    def _resolve_arm_id_and_inputs(self, component):
        if not isinstance(component, PipelineComponent) or not component.jobs:
            return
        self._resolve_inputs_for_pipeline_component_jobs(component.jobs, component._base_path)
        self._resolve_arm_id_for_pipeline_component_jobs(component.jobs, self._orchestrators.get_asset_arm_id)


def _refine_component(component_func: types.FunctionType) -> Component:
    """Return the component of function that is decorated by command
    component decorator.

    :param component_func: Function that is decorated by command component decorator
    :type component_func: types.FunctionType
    :return: Component entity of target function
    :rtype: Component
    """

    def check_parameter_type(f):
        """Check all parameter is annotated or has a default value with
        clear type(not None)."""
        annotations = getattr(f, "__annotations__", {})
        defaults_dict = {key: val.default for key, val in signature(f).parameters.items()}
        unknown_type_keys = [
            key for key, val in defaults_dict.items() if key not in annotations and val is Parameter.empty
        ]
        if unknown_type_keys:
            msg = "Unknown type of parameter {} in pipeline func {!r}, please add type annotation."
            raise ValidationException(
                message=msg.format(unknown_type_keys, f.__name__),
                no_personal_data_message=msg.format("[keys]", "[name]"),
                target=ErrorTarget.COMPONENT,
                error_category=ErrorCategory.USER_ERROR,
            )

    if hasattr(component_func, "_is_mldesigner_component") and component_func._is_mldesigner_component:
        return component_func.component
    if hasattr(component_func, "_is_dsl_func") and component_func._is_dsl_func:
        check_parameter_type(component_func)
        if component_func._job_settings:
            module_logger.warning(
                "Job settings %s on pipeline function '%s' are ignored when creating PipelineComponent.",
                component_func._job_settings,
                component_func.__name__,
            )
        return component_func._pipeline_builder.build()
    msg = "Function must be a dsl or mldesigner component function： {!r}"
    raise ValidationException(
        message=msg.format(component_func),
        no_personal_data_message=msg.format("component"),
        error_category=ErrorCategory.USER_ERROR,
        target=ErrorTarget.COMPONENT,
    )


def _try_resolve_code_for_component(component: Component, get_arm_id_and_fill_back: Callable) -> None:
    if hasattr(component, "code"):
        if is_ARM_id_for_resource(component.code, AzureMLResourceType.CODE):
            # arm id can be passed directly
            pass
        elif isinstance(component.code, Code) or is_registry_id_for_resource(component.code):
            # Code object & registry id need to be resolved into arm id
            component.code = get_arm_id_and_fill_back(component.code, azureml_type=AzureMLResourceType.CODE)
        else:
            with component._resolve_local_code() as code_path:
                component.code = get_arm_id_and_fill_back(
                    Code(base_path=component._base_path, path=code_path), azureml_type=AzureMLResourceType.CODE
                )
