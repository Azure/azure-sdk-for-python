# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import tempfile
import types
from pathlib import Path
from typing import Dict, Iterable, Union

from azure.ai.ml.operations import EnvironmentOperations
from ._operation_orchestrator import OperationOrchestrator
from ._code_operations import CodeOperations
from azure.ai.ml._restclient.v2022_05_01 import AzureMachineLearningWorkspaces as ServiceClient052022
from azure.ai.ml._restclient.v2022_05_01.models import ComponentContainerDetails, ListViewType
from azure.ai.ml._scope_dependent_operations import _ScopeDependentOperations, OperationScope, OperationsContainer
from azure.ai.ml._restclient.v2021_10_01_dataplanepreview import (
    AzureMachineLearningWorkspaces as ServiceClient102021Dataplane,
)

from azure.ai.ml._utils.utils import hash_dict

from azure.ai.ml.constants import AzureMLResourceType, ANONYMOUS_COMPONENT_NAME
from azure.ai.ml.entities import Component, CommandComponent, ParallelComponent, Environment, Asset

from azure.ai.ml.entities._assets import Code
from azure.ai.ml._utils._asset_utils import (
    _create_or_update_autoincrement,
    _resolve_label_to_asset,
    _get_latest,
    _archive_or_restore,
)
from azure.ai.ml._utils._arm_id_utils import (
    is_ARM_id_for_resource,
    is_registry_id_for_resource,
)

from azure.ai.ml._telemetry import (
    AML_INTERNAL_LOGGER_NAMESPACE,
    ActivityType,
    monitor_with_activity,
    monitor_with_telemetry_mixin,
)

from azure.ai.ml._ml_exceptions import (
    ComponentException,
    ErrorCategory,
    ErrorTarget,
    ValidationException,
)
from azure.ai.ml.entities._validation import ValidationResult

logger = logging.getLogger(AML_INTERNAL_LOGGER_NAMESPACE + __name__)
logger.propagate = False
module_logger = logging.getLogger(__name__)
COMPONENT_PLACEHOLDER = "COMPONENT_PLACEHOLDER"
COMPONENT_CODE_PLACEHOLDER = "command_component: code_placeholder"


class ComponentOperations(_ScopeDependentOperations):
    """
    ComponentOperations

    You should not instantiate this class directly. Instead, you should create an MLClient instance that instantiates it for you and attaches it as an attribute.
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

    @property
    def _code_operations(self) -> CodeOperations:
        return self._all_operations.get_operation(AzureMLResourceType.CODE, lambda x: isinstance(x, CodeOperations))

    @property
    def _environment_operations(self) -> EnvironmentOperations:
        return self._all_operations.get_operation(
            AzureMLResourceType.ENVIRONMENT, lambda x: isinstance(x, EnvironmentOperations)
        )

    @monitor_with_activity(logger, "Component.List", ActivityType.PUBLICAPI)
    def list(
        self, name: Union[str, None] = None, *, list_view_type: ListViewType = ListViewType.ACTIVE_ONLY
    ) -> Iterable[Union[Component, ComponentContainerDetails]]:
        """List specific component or components of the workspace.

        :param name: Component name, if not set, list all components of the workspace
        :type name: Optional[str]
        :param list_view_type: View type for including/excluding (for example) archived components. Default: ACTIVE_ONLY.
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

    @monitor_with_telemetry_mixin(logger, "Component.Validate", ActivityType.PUBLICAPI)
    def validate(
        self, component: Union[Component, types.FunctionType], raise_on_failure: bool = False, **kwargs
    ) -> ValidationResult:
        """validate a specified component.
        if there are inline defined entities, e.g. Environment, Code, they won't be created.

        :param component: The component object or a mldesigner component function that generates component object
        :type component: Union[Component, types.FunctionType]
        :param raise_on_failure: whether to raise exception on validation error
        :type raise_on_failure: bool
        :return: All validation errors
        :type: ValidationResult
        """
        # Update component when the input is a component function
        if isinstance(component, types.FunctionType):
            component = self._refine_component(component)

        # local validation only for now
        return component._validate(raise_error=raise_on_failure)

    @monitor_with_telemetry_mixin(logger, "Component.CreateOrUpdate", ActivityType.PUBLICAPI)
    def create_or_update(self, component: Union[Component, types.FunctionType], **kwargs) -> Component:
        """Create or update a specified component. if there're inline defined entities, e.g. Environment, Code, they'll be created together with the component.

        :param component: The component object or a mldesigner component function that generates component object
        :type component: Union[Component, types.FunctionType]
        """
        # Update component when the input is a component function
        if isinstance(component, types.FunctionType):
            component = self._refine_component(component)

        component._set_is_anonymous(kwargs.pop("is_anonymous", False))
        self.validate(component, raise_on_failure=True)

        # Create all dependent resources
        self._upload_dependencies(component)

        component._update_anonymous_hash()
        rest_component_resource = component._to_rest_object()
        try:
            if self._registry_name:
                result = self._version_operation.begin_create_or_update(
                    name=component.name,
                    version=component.version,
                    resource_group_name=self._operation_scope.resource_group_name,
                    registry_name=self._registry_name,
                    body=rest_component_resource,
                ).result()
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
            return self.get(name=component.name, version=component.version)
        else:
            return Component._from_rest_object(result)

    @monitor_with_telemetry_mixin(logger, "Component.Archive", ActivityType.PUBLICAPI)
    def archive(self, name: str, version: str = None, label: str = None) -> None:
        """
        Archive a component.
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
        """
        Restore an archived component.
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

        Latest is defined as the most recently created, not the most recently updated.
        """
        result = _get_latest(
            component_name,
            self._version_operation,
            self._resource_group_name,
            self._workspace_name,
        )
        return Component._from_rest_object(result)

    def _upload_dependencies(self, component: Component) -> None:
        get_arm_id_and_fill_back = OperationOrchestrator(self._all_operations, self._operation_scope).get_asset_arm_id

        if isinstance(component, Component):
            if component.code is not None:
                if isinstance(component.code, Code) or is_registry_id_for_resource(component.code):
                    component.code = get_arm_id_and_fill_back(component.code, azureml_type=AzureMLResourceType.CODE)
                elif not is_ARM_id_for_resource(component.code, AzureMLResourceType.CODE):
                    component.code = get_arm_id_and_fill_back(
                        Code(base_path=component._base_path, path=component.code),
                        azureml_type=AzureMLResourceType.CODE,
                    )
            else:
                # Hack: when code not specified, we generated a file which contains COMPONENT_PLACEHOLDER as code
                # This hack was introduced because job does not allow running component without a code, and we need to
                # make sure when component updated some field(eg: description), the code remains the same.
                # Benefit of using a constant code for all components without code is this will generate same code for
                # anonymous components which enables component reuse
                with tempfile.TemporaryDirectory() as tmp_dir:
                    code_file_path = Path(tmp_dir) / COMPONENT_PLACEHOLDER
                    with open(code_file_path, "w") as f:
                        f.write(COMPONENT_CODE_PLACEHOLDER)
                    component.code = get_arm_id_and_fill_back(
                        Code(base_path=component._base_path, path=code_file_path),
                        azureml_type=AzureMLResourceType.CODE,
                    )
            if component.environment:
                component.environment = get_arm_id_and_fill_back(
                    component.environment, azureml_type=AzureMLResourceType.ENVIRONMENT
                )
        # elif isinstance(component, ParallelComponent):
        #     # TODO: need to clarify if there is azureMLResource in ParallelComponent
        #     pass
        else:
            msg = f"Non supported component type: {type(component)}"
            raise ValidationException(
                message=msg,
                target=ErrorTarget.COMPONENT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )

    def _refine_component(self, component_func: types.FunctionType) -> Component:
        """
        Return the component of function that is decorated by command component decorator.
        :param component_func: Function that is decorated by command component decorator
        :type component_func: types.FunctionType
        :return: Component entity of target function
        :rtype: Component
        """
        if not hasattr(component_func, "_is_mldesigner_component") or not component_func._is_mldesigner_component:
            msg = "Function must be a mldesigner component function： {!r}"
            raise ValidationException(
                message=msg.format(component_func),
                no_personal_data_message=msg.format("component"),
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.COMPONENT,
            )
        component = component_func.component
        return component
