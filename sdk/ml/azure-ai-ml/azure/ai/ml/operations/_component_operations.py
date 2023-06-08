# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import time
import types
from functools import partial
from inspect import Parameter, signature
from typing import Any, Callable, Dict, Iterable, List, Optional, Union

from azure.ai.ml._restclient.v2021_10_01_dataplanepreview import (
    AzureMachineLearningWorkspaces as ServiceClient102021Dataplane,
)
from azure.ai.ml._restclient.v2022_10_01 import AzureMachineLearningWorkspaces as ServiceClient102022
from azure.ai.ml._restclient.v2022_10_01.models import ListViewType
from azure.ai.ml._scope_dependent_operations import (
    OperationConfig,
    OperationsContainer,
    OperationScope,
    _ScopeDependentOperations,
)
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity, monitor_with_telemetry_mixin
from azure.ai.ml._utils._asset_utils import (
    _archive_or_restore,
    _create_or_update_autoincrement,
    _get_latest,
    _get_next_version_from_container,
    _resolve_label_to_asset,
)
from azure.ai.ml._utils._azureml_polling import AzureMLPolling
from azure.ai.ml._utils._endpoint_utils import polling_wait
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml._vendor.azure_resources.operations import DeploymentsOperations
from azure.ai.ml.constants._common import (
    DEFAULT_COMPONENT_VERSION,
    DEFAULT_LABEL_NAME,
    AzureMLResourceType,
    LROConfigurations,
)
from azure.ai.ml.entities import Component, ValidationResult
from azure.ai.ml.exceptions import ComponentException, ErrorCategory, ErrorTarget, ValidationException

from .._utils._cache_utils import CachedNodeResolver
from .._utils._experimental import experimental
from .._utils.utils import is_data_binding_expression
from ..entities._builders import BaseNode
from ..entities._builders.condition_node import ConditionNode
from ..entities._builders.control_flow_node import LoopNode
from ..entities._component.automl_component import AutoMLComponent
from ..entities._component.pipeline_component import PipelineComponent
from ..entities._job.pipeline._attr_dict import has_attr_safe
from ._code_operations import CodeOperations
from ._environment_operations import EnvironmentOperations
from ._operation_orchestrator import OperationOrchestrator
from ._workspace_operations import WorkspaceOperations

ops_logger = OpsLogger(__name__)
logger, module_logger = ops_logger.package_logger, ops_logger.module_logger


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
        service_client: Union[ServiceClient102022, ServiceClient102021Dataplane],
        all_operations: OperationsContainer,
        preflight_operation: Optional[DeploymentsOperations] = None,
        **kwargs: Dict,
    ):
        super(ComponentOperations, self).__init__(operation_scope, operation_config)
        ops_logger.update_info(kwargs)
        self._version_operation = service_client.component_versions
        self._preflight_operation = preflight_operation
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
    def _workspace_operations(self) -> WorkspaceOperations:
        return self._all_operations.get_operation(
            AzureMLResourceType.WORKSPACE,
            lambda x: isinstance(x, WorkspaceOperations),
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

    @monitor_with_telemetry_mixin(logger, "Component.Get", ActivityType.PUBLICAPI)
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

        if not version and not label:
            label = DEFAULT_LABEL_NAME

        if label == DEFAULT_LABEL_NAME:
            label = None
            version = DEFAULT_COMPONENT_VERSION

        if label:
            return _resolve_label_to_asset(self, name, label)

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
        self._resolve_dependencies_for_pipeline_component_jobs(
            component,
            resolver=self._orchestrators.resolve_azureml_id,
            resolve_inputs=False,
        )
        return component

    @experimental
    @monitor_with_telemetry_mixin(logger, "Component.Validate", ActivityType.PUBLICAPI)
    # pylint: disable=no-self-use
    def validate(
        self,
        component: Union[Component, types.FunctionType],
        raise_on_failure: bool = False,
        **kwargs,
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
        return self._validate(
            component,
            raise_on_failure=raise_on_failure,
            # TODO 2330505: change this to True after remote validation is ready
            skip_remote_validation=kwargs.pop("skip_remote_validation", True),
        )

    @monitor_with_telemetry_mixin(logger, "Component.Validate", ActivityType.INTERNALCALL)
    def _validate(  # pylint: disable=no-self-use
        self,
        component: Union[Component, types.FunctionType],
        raise_on_failure: bool,
        skip_remote_validation: bool,
    ) -> ValidationResult:
        """Implementation of validate. Add this function to avoid calling validate() directly in create_or_update(),
        which will impact telemetry statistics & bring experimental warning in create_or_update().
        """
        # Update component when the input is a component function
        if isinstance(component, types.FunctionType):
            component = _refine_component(component)

        # local validation
        result = component._validate(raise_error=raise_on_failure)
        # remote validation, note that preflight_operation is not available for registry client
        if not skip_remote_validation and self._preflight_operation:
            workspace = self._workspace_operations.get()
            remote_validation_result = self._preflight_operation.begin_validate(
                resource_group_name=self._resource_group_name,
                deployment_name=self._workspace_name,
                parameters=component._build_rest_object_for_remote_validation(
                    location=workspace.location,
                    workspace_name=self._workspace_name,
                ),
                **self._init_args,
            )
            result.merge_with(remote_validation_result.result(), overwrite=True)
        # resolve location for diagnostics from remote validation
        result.resolve_location_for_diagnostics(component._source_path)
        return result.try_raise(
            error_target=ErrorTarget.COMPONENT,
            raise_error=raise_on_failure,
        )

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
        # In non-registry scenario, if component does not have version, no need to get next version here.
        # As Component property version has setter that updates `_auto_increment_version` in-place, then
        # a component will get a version after its creation, and it will always use this version in its
        # future creation operations, which breaks version auto increment mechanism.
        if self._registry_name and not component.version and component._auto_increment_version:
            component.version = _get_next_version_from_container(
                name=component.name,
                container_operation=self._container_operation,
                resource_group_name=self._operation_scope.resource_group_name,
                workspace_name=self._workspace_name,
                registry_name=self._registry_name,
                **self._init_args,
            )

        if not component._is_anonymous:
            component._is_anonymous = kwargs.pop("is_anonymous", False)

        if not skip_validation:
            self._validate(component, raise_on_failure=True, skip_remote_validation=True)

        # Create all dependent resources
        # Only upload dependencies if component is NOT IPP
        if not component._intellectual_property:
            self._resolve_arm_id_or_upload_dependencies(component)

        name, version = component._get_rest_name_version()
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
                    name=name,
                    version=version,
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
                # _auto_increment_version can be True for non-registry component creation operation;
                # and anonymous component should use hash as version
                if not component._is_anonymous and component._auto_increment_version:
                    result = _create_or_update_autoincrement(
                        name=name,
                        body=rest_component_resource,
                        version_operation=self._version_operation,
                        container_operation=self._container_operation,
                        resource_group_name=self._operation_scope.resource_group_name,
                        workspace_name=self._workspace_name,
                        **self._init_args,
                    )
                else:
                    result = self._version_operation.create_or_update(
                        name=name,
                        version=version,
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

        self._resolve_dependencies_for_pipeline_component_jobs(
            component,
            resolver=self._orchestrators.resolve_azureml_id,
            resolve_inputs=False,
        )
        return component

    @monitor_with_telemetry_mixin(logger, "Component.Archive", ActivityType.PUBLICAPI)
    def archive(
        self,
        name: str,
        version: Optional[str] = None,
        label: Optional[str] = None,
        **kwargs,  # pylint:disable=unused-argument
    ) -> None:
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
    def restore(
        self,
        name: str,
        version: Optional[str] = None,
        label: Optional[str] = None,
        **kwargs,  # pylint:disable=unused-argument
    ) -> None:
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

    @classmethod
    def _try_resolve_environment_for_component(cls, component, _: str, resolver: Callable):
        if isinstance(component, BaseNode):
            component = component._component  # pylint: disable=protected-access

        if isinstance(component, str):
            return
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
                component.environment = resolver(component.environment, azureml_type=AzureMLResourceType.ENVIRONMENT)

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
        self._try_resolve_environment_for_component(
            component=component,
            resolver=get_arm_id_and_fill_back,
            _="",
        )

        self._resolve_dependencies_for_pipeline_component_jobs(
            component,
            resolver=get_arm_id_and_fill_back,
        )

    def _resolve_inputs_for_pipeline_component_jobs(self, jobs: Dict[str, Any], base_path: str):
        """Resolve inputs for jobs in a pipeline component.

        :param jobs: A dict of nodes in a pipeline component.
        :type jobs: Dict[str, Any]
        :param base_path: The base path used to resolve inputs. Usually it's
        the base path of the pipeline component.
        :type base_path: str
        """
        from azure.ai.ml.entities._builders import Pipeline
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

    @classmethod
    def _resolve_binding_on_supported_fields_for_node(cls, node):
        """Resolve all PipelineInput(binding from sdk) on supported fields to string."""
        from azure.ai.ml.entities._job.pipeline._attr_dict import try_get_non_arbitrary_attr_for_potential_attr_dict
        from azure.ai.ml.entities._job.pipeline._io import PipelineInput

        # compute binding to pipeline input is supported on node.
        supported_fields = ["compute", "compute_name"]
        for field_name in supported_fields:
            val = try_get_non_arbitrary_attr_for_potential_attr_dict(node, field_name)
            if isinstance(val, PipelineInput):
                # Put binding string to field
                setattr(node, field_name, val._data_binding())

    @classmethod
    def _try_resolve_node_level_task_for_parallel_node(cls, node: BaseNode, _: str, resolver: Callable):
        """Resolve node.task.code for parallel node if it's a reference to node.component.task.code.

        This is a hack operation.

        parallel_node.task.code won't be resolved directly for now, but it will be resolved if
        parallel_node.task is a reference to parallel_node.component.task. Then when filling back
        parallel_node.component.task.code, parallel_node.task.code will be changed as well.

        However, if we enable in-memory/on-disk cache for component resolution, such change
        won't happen, so we resolve node level task code manually here.

        Note that we will always use resolved node.component.code to fill back node.task.code
        given code overwrite on parallel node won't take effect for now. This is to make behaviors
        consistent across os and python versions.

        The ideal solution should be done after PRS team decides how to handle parallel.task.code
        """
        from azure.ai.ml.entities import Parallel, ParallelComponent

        if not isinstance(node, Parallel):
            return
        component = node._component  # pylint: disable=protected-access
        if not isinstance(component, ParallelComponent):
            return
        if not node.task:
            return

        if node.task.code:
            _try_resolve_code_for_component(
                component,
                get_arm_id_and_fill_back=resolver,
            )
            node.task.code = component.code
        if node.task.environment:
            node.task.environment = resolver(component.environment, azureml_type=AzureMLResourceType.ENVIRONMENT)

    @classmethod
    def _set_default_display_name_for_anonymous_component_in_node(cls, node: BaseNode, default_name: str):
        """Set default display name for anonymous component in a node.
        If node._component is an anonymous component and without display name, set the default display name.
        """
        if not isinstance(node, BaseNode):
            return
        component = node._component
        if isinstance(component, PipelineComponent):
            return
        # Set display name as node name
        # TODO: the same anonymous component with different node name will have different anonymous hash
        # as their display name will be different.
        if (
            isinstance(component, Component)
            # check if component is anonymous and not created based on its id. We can't directly check
            # node._component._is_anonymous as it will be set to True on component creation,
            # which is later than this check
            and not component.id
            and not component.display_name
        ):
            component.display_name = default_name

    @classmethod
    def _try_resolve_compute_for_node(cls, node: BaseNode, _: str, resolver):
        """Resolve compute for base node."""
        if not isinstance(node, BaseNode):
            return
        if not isinstance(node._component, PipelineComponent):
            # Resolve compute for other type
            # Keep data binding expression as they are
            if not is_data_binding_expression(node.compute):
                # Get compute for each job
                node.compute = resolver(node.compute, azureml_type=AzureMLResourceType.COMPUTE)
            if has_attr_safe(node, "compute_name") and not is_data_binding_expression(node.compute_name):
                node.compute_name = resolver(node.compute_name, azureml_type=AzureMLResourceType.COMPUTE)

    @classmethod
    def _divide_nodes_to_resolve_into_layers(cls, component: PipelineComponent, extra_operations: List[Callable]):
        """Traverse the pipeline component and divide nodes to resolve into layers. Note that all leaf nodes will be
        put in the last layer.
        For example, for below pipeline component, assuming that all nodes need to be resolved:
          A
         /|\
        B C D
        | |
        E F
        |
        G
        return value will be:
        [
          [("B", B), ("C", C)],
          [("E", E)],
          [("D", D), ("F", F), ("G", G)],
        ]

        :param component: The pipeline component to resolve.
        :type component: PipelineComponent
        :param extra_operations: Extra operations to apply on nodes during the traversing.
        :type extra_operations: List[Callable]
        :return: A list of layers of nodes to resolve.
        :rtype: List[List[Tuple[str, BaseNode]]]
        """
        nodes_to_process = list(component.jobs.items())
        layers = []
        leaf_nodes = []

        while nodes_to_process:
            layers.append([])
            new_nodes_to_process = []
            for key, job_instance in nodes_to_process:
                cls._resolve_binding_on_supported_fields_for_node(job_instance)
                if isinstance(job_instance, LoopNode):
                    job_instance = job_instance.body

                for extra_operation in extra_operations:
                    extra_operation(job_instance, key)

                if isinstance(job_instance, BaseNode) and isinstance(job_instance._component, PipelineComponent):
                    # candidates for next layer
                    new_nodes_to_process.extend(job_instance.component.jobs.items())
                    # use layers to store pipeline nodes in each layer for now
                    layers[-1].append((key, job_instance))
                else:
                    # note that LoopNode has already been replaced by its body here
                    leaf_nodes.append((key, job_instance))
            nodes_to_process = new_nodes_to_process

        # if there is subgraph, the last item in layers will be empty for now as all leaf nodes are stored in leaf_nodes
        if len(layers) != 0:
            layers.pop()
            layers.append(leaf_nodes)

        return layers

    def _resolve_dependencies_for_pipeline_component_jobs(
        self, component: Union[Component, str], resolver: Callable, *, resolve_inputs: bool = True
    ):
        """Resolve dependencies for pipeline component jobs.
        Will directly return if component is not a pipeline component.

        :param component: The pipeline component to resolve.
        :type component: Union[Component, str]
        :param resolver: The resolver to resolve the dependencies.
        :type resolver: Callable
        :param resolve_inputs: Whether to resolve inputs.
        :type resolve_inputs: bool
        """
        if not isinstance(component, PipelineComponent) or not component.jobs:
            return

        from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob

        if resolve_inputs:
            self._resolve_inputs_for_pipeline_component_jobs(component.jobs, component._base_path)

        # This is a preparation for concurrent resolution. Nodes will be resolved later layer by layer
        # from bottom to top, as hash calculation of a parent node will be impacted by resolution
        # of its child nodes.
        layers = self._divide_nodes_to_resolve_into_layers(
            component,
            extra_operations=[
                # no need to do this as we now keep the original component name for anonymous components
                # self._set_default_display_name_for_anonymous_component_in_node,
                partial(self._try_resolve_node_level_task_for_parallel_node, resolver=resolver),
                partial(self._try_resolve_environment_for_component, resolver=resolver),
                partial(self._try_resolve_compute_for_node, resolver=resolver),
                # should we resolve code here after we do extra operations concurrently?
            ],
        )

        # cache anonymous component only for now
        # request level in-memory cache can be a better solution for other type of assets as they are
        # relatively simple and of small number of distinct instances
        component_cache = CachedNodeResolver(
            resolver=resolver,
            subscription_id=self._subscription_id,
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            registry_name=self._registry_name,
        )

        for layer in reversed(layers):
            for _, job_instance in layer:
                if isinstance(job_instance, AutoMLJob):
                    # only compute is resolved here
                    self._job_operations._resolve_arm_id_for_automl_job(job_instance, resolver, inside_pipeline=True)
                elif isinstance(job_instance, BaseNode):
                    component_cache.register_node_for_lazy_resolution(job_instance)
                elif isinstance(job_instance, ConditionNode):
                    pass
                else:
                    msg = f"Non supported job type in Pipeline: {type(job_instance)}"
                    raise ComponentException(
                        message=msg,
                        target=ErrorTarget.COMPONENT,
                        no_personal_data_message=msg,
                        error_category=ErrorCategory.USER_ERROR,
                    )

            component_cache.resolve_nodes()


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
        func_parameters = signature(f).parameters
        defaults_dict = {key: val.default for key, val in func_parameters.items()}
        variable_inputs = [
            key for key, val in func_parameters.items() if val.kind in [val.VAR_POSITIONAL, val.VAR_KEYWORD]
        ]
        if variable_inputs:
            msg = "Cannot register the component {} with variable inputs {!r}."
            raise ValidationException(
                message=msg.format(f.__name__, variable_inputs),
                no_personal_data_message=msg.format("[keys]", "[name]"),
                target=ErrorTarget.COMPONENT,
                error_category=ErrorCategory.USER_ERROR,
            )
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

    def check_non_pipeline_inputs(f):
        """Check whether non_pipeline_inputs exist in pipeline builder."""
        if f._pipeline_builder.non_pipeline_parameter_names:
            msg = "Cannot register pipeline component {!r} with non_pipeline_inputs."
            raise ValidationException(
                message=msg.format(f.__name__),
                no_personal_data_message=msg.format(""),
                target=ErrorTarget.COMPONENT,
                error_category=ErrorCategory.USER_ERROR,
            )

    if hasattr(component_func, "_is_mldesigner_component") and component_func._is_mldesigner_component:
        return component_func.component
    if hasattr(component_func, "_is_dsl_func") and component_func._is_dsl_func:
        check_non_pipeline_inputs(component_func)
        check_parameter_type(component_func)
        if component_func._job_settings:
            module_logger.warning(
                "Job settings %s on pipeline function '%s' are ignored when creating PipelineComponent.",
                component_func._job_settings,
                component_func.__name__,
            )
        # Normally pipeline component are created when dsl.pipeline inputs are provided
        # so pipeline input .result() can resolve to correct value.
        # When pipeline component created without dsl.pipeline inputs, pipeline input .result() won't work.
        return component_func._pipeline_builder.build(user_provided_kwargs={})
    msg = "Function must be a dsl or mldesigner component function： {!r}"
    raise ValidationException(
        message=msg.format(component_func),
        no_personal_data_message=msg.format("component"),
        error_category=ErrorCategory.USER_ERROR,
        target=ErrorTarget.COMPONENT,
    )


def _try_resolve_code_for_component(component: Component, get_arm_id_and_fill_back: Callable) -> None:
    with component._resolve_local_code() as code:
        if code is None:
            return
        component.code = get_arm_id_and_fill_back(code, azureml_type=AzureMLResourceType.CODE)
