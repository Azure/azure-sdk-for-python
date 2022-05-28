# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import Any, Iterable, Union

from azure.ai.ml._artifacts._artifact_utilities import _check_and_upload_env_build_context
from azure.ai.ml.constants import ARM_ID_PREFIX, AzureMLResourceType
from azure.ai.ml._scope_dependent_operations import _ScopeDependentOperations, OperationScope, OperationsContainer
from azure.ai.ml._restclient.v2022_02_01_preview.models import EnvironmentVersionData, ListViewType
from azure.ai.ml._restclient.v2022_05_01 import (
    AzureMachineLearningWorkspaces as ServiceClient052022,
)
from azure.ai.ml._restclient.v2021_10_01_dataplanepreview import (
    AzureMachineLearningWorkspaces as ServiceClient102021Dataplane,
)
from azure.ai.ml._utils._registry_utils import get_sas_uri_for_registry_asset, get_asset_body_for_registry_storage
from azure.ai.ml.entities._assets import Environment
from azure.ai.ml._utils._asset_utils import (
    _create_or_update_autoincrement,
    _get_latest,
    _resolve_label_to_asset,
    _archive_or_restore,
)
from azure.ai.ml._telemetry import AML_INTERNAL_LOGGER_NAMESPACE, ActivityType, monitor_with_activity
from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, ValidationException

logger = logging.getLogger(AML_INTERNAL_LOGGER_NAMESPACE + __name__)
logger.propagate = False
module_logger = logging.getLogger(__name__)


class EnvironmentOperations(_ScopeDependentOperations):
    def __init__(
        self,
        operation_scope: OperationScope,
        service_client: Union[ServiceClient052022, ServiceClient102021Dataplane],
        all_operations: OperationsContainer,
        **kwargs: Any
    ):
        super(EnvironmentOperations, self).__init__(operation_scope)
        if "app_insights_handler" in kwargs:
            logger.addHandler(kwargs.pop("app_insights_handler"))
        self._kwargs = kwargs
        self._containers_operations = service_client.environment_containers
        self._version_operations = service_client.environment_versions
        self._service_client = service_client
        self._all_operations = all_operations
        self._datastore_operation = all_operations.all_operations[AzureMLResourceType.DATASTORE]

        # Maps a label to a function which given an asset name,
        # returns the asset associated with the label
        self._managed_label_resolver = {"latest": self._get_latest_version}

    @monitor_with_activity(logger, "Environment.CreateOrUpdate", ActivityType.PUBLICAPI)
    def create_or_update(self, environment: Environment) -> Environment:
        """Returns created or updated environment asset.

        :param environment: Environment object
        :type environment: Environment
        :return: Created or updated Environment object
        """

        sas_uri = None
        blob_uri = None

        if self._registry_name:
            sas_uri, blob_uri = get_sas_uri_for_registry_asset(
                service_client=self._service_client,
                name=environment.name,
                version=environment.version,
                resource_group=self._resource_group_name,
                registry=self._registry_name,
                body=get_asset_body_for_registry_storage(
                    self._registry_name, "environments", environment.name, environment.version
                ),
            )

        environment = _check_and_upload_env_build_context(environment=environment, operations=self, sas_uri=sas_uri)

        env_version_resource = environment._to_rest_object()

        if environment._auto_increment_version:
            env_rest_obj = _create_or_update_autoincrement(
                name=environment.name,
                body=env_version_resource,
                version_operation=self._version_operations,
                container_operation=self._containers_operations,
                workspace_name=self._workspace_name,
                **self._scope_kwargs,
                **self._kwargs,
            )
        else:
            env_rest_obj = (
                self._version_operations.begin_create_or_update(
                    name=environment.name,
                    version=environment.version,
                    registry_name=self._registry_name,
                    body=env_version_resource,
                    **self._scope_kwargs,
                    **self._kwargs,
                ).result()
                if self._registry_name
                else self._version_operations.create_or_update(
                    name=environment.name,
                    version=environment.version,
                    workspace_name=self._workspace_name,
                    body=env_version_resource,
                    **self._scope_kwargs,
                    **self._kwargs,
                )
            )

        if not env_rest_obj and self._registry_name:
            env_rest_obj = self._get(name=environment.name, version=environment.version)
        return Environment._from_rest_object(env_rest_obj)

    def _get(self, name: str, version: str = None) -> EnvironmentVersionData:
        if version:
            return (
                self._version_operations.get(
                    name=name,
                    version=version,
                    registry_name=self._registry_name,
                    **self._scope_kwargs,
                    **self._kwargs,
                )
                if self._registry_name
                else self._version_operations.get(
                    name=name,
                    version=version,
                    workspace_name=self._workspace_name,
                    **self._scope_kwargs,
                    **self._kwargs,
                )
            )
        else:
            return (
                self._containers_operations.get(
                    name=name,
                    registry_name=self._registry_name,
                    **self._scope_kwargs,
                    **self._kwargs,
                )
                if self._registry_name
                else self._containers_operations.get(
                    name=name,
                    workspace_name=self._workspace_name,
                    **self._scope_kwargs,
                    **self._kwargs,
                )
            )

    @monitor_with_activity(logger, "Environment.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, version: str = None, label: str = None) -> Environment:
        """Returns the specified environment asset.

        :param name: Name of the environment.
        :type name: str
        :param version: Version of the environment.
        :type version: str
        :param label: Label of the environment. (mutually exclusive with version)
        :type label: str
        :return: Environment object
        """
        if version and label:
            msg = "Cannot specify both version and label."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.ENVIRONMENT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )

        if label:
            return _resolve_label_to_asset(self, name, label)

        if not version:
            msg = "Must provide either version or label."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.ENVIRONMENT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        name = _preprocess_environment_name(name)
        env_version_resource = self._get(name, version)

        return Environment._from_rest_object(env_version_resource)

    @monitor_with_activity(logger, "Environment.List", ActivityType.PUBLICAPI)
    def list(
        self, name: str = None, *, list_view_type: ListViewType = ListViewType.ACTIVE_ONLY
    ) -> Iterable[Environment]:
        """List all environment assets in workspace.

        :param name: Name of the environment.
        :type name: Optional[str]
        :param list_view_type: View type for including/excluding (for example) archived environments. Default: ACTIVE_ONLY.
        :type list_view_type: Optional[ListViewType]
        :return: An iterator like instance of Environment objects.
        :rtype: ~azure.core.paging.ItemPaged[Environment]
        """
        if name:
            return (
                self._version_operations.list(
                    name=name,
                    registry_name=self._registry_name,
                    cls=lambda objs: [Environment._from_rest_object(obj) for obj in objs],
                    **self._scope_kwargs,
                    **self._kwargs,
                )
                if self._registry_name
                else self._version_operations.list(
                    name=name,
                    workspace_name=self._workspace_name,
                    cls=lambda objs: [Environment._from_rest_object(obj) for obj in objs],
                    list_view_type=list_view_type,
                    **self._scope_kwargs,
                    **self._kwargs,
                )
            )
        else:
            return (
                self._containers_operations.list(
                    registry_name=self._registry_name,
                    cls=lambda objs: [Environment._from_container_rest_object(obj) for obj in objs],
                    **self._scope_kwargs,
                    **self._kwargs,
                )
                if self._registry_name
                else self._containers_operations.list(
                    workspace_name=self._workspace_name,
                    cls=lambda objs: [Environment._from_container_rest_object(obj) for obj in objs],
                    list_view_type=list_view_type,
                    **self._scope_kwargs,
                    **self._kwargs,
                )
            )

    @monitor_with_activity(logger, "Environment.Delete", ActivityType.PUBLICAPI)
    def archive(self, name: str, version: str = None, label: str = None) -> None:
        """
        Archive an environment or an environment version.
        :param name: Name of the environment.
        :type name: str
        :param version: Version of the environment.
        :type version: str
        :param label: Label of the environment. (mutually exclusive with version)
        :type label: str
        """
        name = _preprocess_environment_name(name)
        _archive_or_restore(
            asset_operations=self,
            version_operation=self._version_operations,
            container_operation=self._containers_operations,
            is_archived=True,
            name=name,
            version=version,
            label=label,
        )

    @monitor_with_activity(logger, "Environment.Restore", ActivityType.PUBLICAPI)
    def restore(self, name: str, version: str = None, label: str = None, **kwargs) -> None:
        """
        Restore an archived environment version.
        :param name: Name of the environment.
        :type name: str
        :param version: Version of the environment.
        :type version: str
        :param label: Label of the environment. (mutually exclusive with version)
        :type label: str
        """
        name = _preprocess_environment_name(name)
        _archive_or_restore(
            asset_operations=self,
            version_operation=self._version_operations,
            container_operation=self._containers_operations,
            is_archived=False,
            name=name,
            version=version,
            label=label,
        )

    def _get_latest_version(self, name: str) -> Environment:
        """Returns the latest version of the asset with the given name.

        Latest is defined as the most recently created, not the most recently updated.
        """
        result = _get_latest(name, self._version_operations, self._resource_group_name, self._workspace_name)
        return Environment._from_rest_object(result)


def _preprocess_environment_name(environment_name: str) -> str:
    if environment_name.startswith(ARM_ID_PREFIX):
        return environment_name[len(ARM_ID_PREFIX) :]
    return environment_name
