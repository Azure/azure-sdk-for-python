# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
import time
import types
from inspect import Parameter, signature
from typing import Callable, Dict, Iterable, Union

from azure.ai.ml._ml_exceptions import ComponentException, ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml._restclient.v2021_10_01_dataplanepreview import (
    AzureMachineLearningWorkspaces as ServiceClient102021Dataplane,
)
from azure.ai.ml._restclient.v2022_05_01 import AzureMachineLearningWorkspaces as ServiceClient052022
from azure.ai.ml._restclient.v2022_05_01.models import ComponentContainerDetails, ListViewType
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope, _ScopeDependentOperations
from azure.ai.ml._telemetry import (
    AML_INTERNAL_LOGGER_NAMESPACE,
    ActivityType,
    monitor_with_activity,
    monitor_with_telemetry_mixin,
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
from azure.ai.ml.constants import AzureMLResourceType, LROConfigurations
from azure.ai.ml.entities import Component
from azure.ai.ml.entities._assets import Code
from azure.ai.ml.entities._validation import ValidationResult

from .._utils._experimental import experimental
from ..entities._component.automl_component import AutoMLComponent
from ..entities._component.pipeline_component import PipelineComponent
from ._code_operations import CodeOperations
from ._environment_operations import EnvironmentOperations
from ._operation_orchestrator import OperationOrchestrator

logger = logging.getLogger(AML_INTERNAL_LOGGER_NAMESPACE + __name__)
logger.propagate = False
module_logger = logging.getLogger(__name__)


class ComponentOperations(_ScopeDependentOperations):
    """ComponentOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        service_client: Union[ServiceClient052022, ServiceClient102021Dataplane],
        all_operations: OperationsContainer,
        **kwargs: Dict,
    ):
        super(ComponentOperations, self).__init__(operation_scope)
        if "app_insights_handler" in kwargs:
            logger.addHandler(kwargs.pop("app_insights_handler"))
        self._version_operation = service_client.component_versions
        self._container_operation = service_client.component_containers
        self._all_operations = all_operations
        self._init_args = kwargs
        # Maps a label to a function which given an asset name,
        # returns the asset associated with the label
        self._managed_label_resolver = {"latest": self._get_latest_version}
        self._orchestrators = OperationOrchestrator(self._all_operations, self._operation_scope)

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

    @monitor_with_activity(logger, "Component.List", ActivityType.PUBLICAPI)
    def list(
        self,
        name: Union[str, None] = None,
        *,
        list_view_type: ListViewType = ListViewType.ACTIVE_ONLY,
    ) -> Iterable[Union[Component, ComponentContainerDetails]]:
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
            )
            if self._registry_name
            else self._container_operation.list(
                resource_group_name=self._resource_group_name,
                workspace_name=self._workspace_name,
                list_view_type=list_view_type,
                **self._init_args,
            )
        )

    @monitor_with_telemetry_mixin(logger, "Component.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, version: str = None, label: str = None) -> Component:
        """Returns information about the specified component.

        :param name: Name of the code component.
        :type name: str
        :param version: Version of the component.
        :type version: str
        :param label: Label of the component. (mutually exclusive with version)
        :type label: str
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
    @monitor_with_telemetry_mixin(logger, "Component.Validate", ActivityType.PUBLICAPI)
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

    @monitor_with_telemetry_mixin(logger, "Component.Validate", ActivityType.INTERNALCALL)
    def _validate(
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

    @monitor_with_telemetry_mixin(
        logger,
        "Component.CreateOrUpdate",
        ActivityType.PUBLICAPI,
        extra_keys=["is_anonymous"],
    )
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

    @monitor_with_telemetry_mixin(logger, "Component.Archive", ActivityType.PUBLICAPI)
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

    @monitor_with_telemetry_mixin(logger, "Component.Restore", ActivityType.PUBLICAPI)
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

        get_arm_id_and_fill_back = OperationOrchestrator(self._all_operations, self._operation_scope).get_asset_arm_id

        if hasattr(component, "code"):
            if is_ARM_id_for_resource(component.code, AzureMLResourceType.CODE):
                # arm id can be passed directly
                pass
            elif isinstance(component.code, Code) or is_registry_id_for_resource(component.code):
                # Code object & registry id need to be resolved into arm id
                component.code = get_arm_id_and_fill_back(component.code, azureml_type=AzureMLResourceType.CODE)
            else:
                # local path & None (will be transformed into temp local path) will be used to create a code object
                # before resolving
                component._resolve_local_code(
                    lambda code: get_arm_id_and_fill_back(code, azureml_type=AzureMLResourceType.CODE)
                )

        if hasattr(component, "environment") and not isinstance(component.environment, dict):
            component.environment = get_arm_id_and_fill_back(
                component.environment, azureml_type=AzureMLResourceType.ENVIRONMENT
            )

        self._resolve_arm_id_and_inputs(component)

    def _resolve_inputs_for_pipeline_component_jobs(self, jobs, base_path):
        from azure.ai.ml.entities._builders import BaseNode
        from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob

        for _, job_instance in jobs.items():
            # resolve inputs for each job's component
            if isinstance(job_instance, BaseNode):
                node: BaseNode = job_instance
                self._job_operations._resolve_job_inputs(
                    map(lambda x: x._data, node.inputs.values()),
                    base_path,
                )
            elif isinstance(job_instance, AutoMLJob):
                self._job_operations._resolve_automl_job_inputs(job_instance, base_path, inside_pipeline=True)

    def _resolve_arm_id_for_pipeline_component_jobs(self, jobs, resolver: Callable):

        from azure.ai.ml.entities import CommandComponent, ParallelComponent
        from azure.ai.ml.entities._builders import BaseNode, Sweep
        from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob

        for key, job_instance in jobs.items():
            if isinstance(job_instance, AutoMLJob):
                self._job_operations._resolve_arm_id_for_automl_job(job_instance, resolver, inside_pipeline=True)
            elif isinstance(job_instance, BaseNode):
                # Get the default for the specific job type
                if (
                    isinstance(
                        job_instance.component,
                        (CommandComponent, ParallelComponent, PipelineComponent),
                    )
                    and job_instance.component._is_anonymous
                    and not job_instance.component.display_name
                ):
                    job_instance.component.display_name = key

                if isinstance(job_instance.component, PipelineComponent):
                    self._resolve_arm_id_and_inputs(job_instance.component)
                else:
                    # Get compute for each job
                    job_instance.compute = resolver(job_instance.compute, azureml_type=AzureMLResourceType.COMPUTE)

                # Get the component id for each job's component
                job_instance._component = resolver(
                    job_instance.trial if isinstance(job_instance, Sweep) else job_instance.component,
                    azureml_type=AzureMLResourceType.COMPONENT,
                )
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
                "Job settings %s on pipeline function " "%s are ignored when creating PipelineComponent.",
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
