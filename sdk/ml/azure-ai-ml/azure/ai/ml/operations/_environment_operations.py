# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Any, Iterable, Optional, Union
from contextlib import contextmanager

from marshmallow.exceptions import ValidationError as SchemaValidationError
from azure.ai.ml._utils._registry_utils import get_registry_client

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._artifacts._artifact_utilities import _check_and_upload_env_build_context
from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._restclient.v2021_10_01_dataplanepreview import (
    AzureMachineLearningWorkspaces as ServiceClient102021Dataplane,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import EnvironmentVersion, ListViewType
from azure.ai.ml._restclient.v2023_04_01_preview import AzureMachineLearningWorkspaces as ServiceClient042023Preview
from azure.ai.ml._scope_dependent_operations import (
    OperationConfig,
    OperationsContainer,
    OperationScope,
    _ScopeDependentOperations,
)
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._asset_utils import (
    _archive_or_restore,
    _get_latest,
    _get_next_version_from_container,
    _resolve_label_to_asset,
)
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml._utils._registry_utils import get_asset_body_for_registry_storage, get_sas_uri_for_registry_asset
from azure.ai.ml.constants._common import ARM_ID_PREFIX, AzureMLResourceType, ASSET_ID_FORMAT
from azure.ai.ml.entities._assets import Environment, WorkspaceAssetReference
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

ops_logger = OpsLogger(__name__)
logger, module_logger = ops_logger.package_logger, ops_logger.module_logger


class EnvironmentOperations(_ScopeDependentOperations):
    """EnvironmentOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: Union[ServiceClient042023Preview, ServiceClient102021Dataplane],
        all_operations: OperationsContainer,
        **kwargs: Any,
    ):
        super(EnvironmentOperations, self).__init__(operation_scope, operation_config)
        ops_logger.update_info(kwargs)
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
        :type environment: ~azure.ai.ml.entities._assets.Environment
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Environment cannot be successfully validated.
            Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.EmptyDirectoryError: Raised if local path provided points to an empty directory.
        :return: Created or updated Environment object
        :rtype: ~azure.ai.ml.entities.Environment
        """
        try:
            if not environment.version and environment._auto_increment_version:
                environment.version = _get_next_version_from_container(
                    name=environment.name,
                    container_operation=self._containers_operations,
                    resource_group_name=self._operation_scope.resource_group_name,
                    workspace_name=self._workspace_name,
                    registry_name=self._registry_name,
                    **self._kwargs,
                )
            sas_uri = None
            if self._registry_name:
                if isinstance(environment, WorkspaceAssetReference):
                    # verify that environment is not already in registry
                    try:
                        self._version_operations.get(
                            name=environment.name,
                            version=environment.version,
                            resource_group_name=self._resource_group_name,
                            registry_name=self._registry_name,
                        )
                    except Exception as err:  # pylint: disable=broad-except
                        if isinstance(err, ResourceNotFoundError):
                            pass
                        else:
                            raise err
                    else:
                        msg = "A environment with this name and version already exists in registry"
                        raise ValidationException(
                            message=msg,
                            no_personal_data_message=msg,
                            target=ErrorTarget.ENVIRONMENT,
                            error_category=ErrorCategory.USER_ERROR,
                        )

                    environment_rest = environment._to_rest_object()
                    result = self._service_client.resource_management_asset_reference.begin_import_method(
                        resource_group_name=self._resource_group_name,
                        registry_name=self._registry_name,
                        body=environment_rest,
                        **self._kwargs,
                    ).result()

                    if not result:
                        env_rest_obj = self._get(name=environment.name, version=environment.version)
                        return Environment._from_rest_object(env_rest_obj)

                sas_uri = get_sas_uri_for_registry_asset(
                    service_client=self._service_client,
                    name=environment.name,
                    version=environment.version,
                    resource_group=self._resource_group_name,
                    registry=self._registry_name,
                    body=get_asset_body_for_registry_storage(
                        self._registry_name,
                        "environments",
                        environment.name,
                        environment.version,
                    ),
                )

            environment = _check_and_upload_env_build_context(
                environment=environment, operations=self, sas_uri=sas_uri, show_progress=self._show_progress
            )
            env_version_resource = environment._to_rest_object()
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
        except Exception as ex:  # pylint: disable=broad-except
            if isinstance(ex, SchemaValidationError):
                log_and_raise_error(ex)
            else:
                raise ex

    def _get(self, name: str, version: Optional[str] = None) -> EnvironmentVersion:
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
    def get(self, name: str, version: Optional[str] = None, label: Optional[str] = None) -> Environment:
        """Returns the specified environment asset.

        :param name: Name of the environment.
        :type name: str
        :param version: Version of the environment.
        :type version: str
        :param label: Label of the environment. (mutually exclusive with version)
        :type label: str
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Environment cannot be successfully validated.
            Details will be provided in the error message.
        :return: Environment object
        :rtype: ~azure.ai.ml.entities.Environment
        """
        if version and label:
            msg = "Cannot specify both version and label."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.ENVIRONMENT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
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
                error_type=ValidationErrorType.MISSING_FIELD,
            )
        name = _preprocess_environment_name(name)
        env_version_resource = self._get(name, version)

        return Environment._from_rest_object(env_version_resource)

    @monitor_with_activity(logger, "Environment.List", ActivityType.PUBLICAPI)
    def list(
        self,
        name: Optional[str] = None,
        *,
        list_view_type: ListViewType = ListViewType.ACTIVE_ONLY,
    ) -> Iterable[Environment]:
        """List all environment assets in workspace.

        :param name: Name of the environment.
        :type name: Optional[str]
        :param list_view_type: View type for including/excluding (for example) archived environments.
            Default: ACTIVE_ONLY.
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
    def archive(
        self,
        name: str,
        version: Optional[str] = None,
        label: Optional[str] = None,
        **kwargs,  # pylint:disable=unused-argument
    ) -> None:
        """Archive an environment or an environment version.

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
    def restore(
        self,
        name: str,
        version: Optional[str] = None,
        label: Optional[str] = None,
        **kwargs,  # pylint:disable=unused-argument
    ) -> None:
        """Restore an archived environment version.

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

        Latest is defined as the most recently created, not the most
        recently updated.
        """
        result = _get_latest(
            name,
            self._version_operations,
            self._resource_group_name,
            self._workspace_name,
            self._registry_name,
        )
        return Environment._from_rest_object(result)

    @monitor_with_activity(logger, "Environment.Share", ActivityType.PUBLICAPI)
    @experimental
    def share(self, name, version, *, share_with_name, share_with_version, registry_name) -> Environment:
        """Share a environment asset from workspace to registry.

        :param name: Name of environment asset.
        :type name: str
        :param version: Version of environment asset.
        :type version: str
        :param share_with_name: Name of environment asset to share with.
        :type share_with_name: str
        :param share_with_version: Version of environment asset to share with.
        :type share_with_version: str
        :param registry_name: Name of the destination registry.
        :type registry_name: str
        :return: Environment asset object.
        :rtype: ~azure.ai.ml.entities.Environment
        """

        #  Get workspace info to get workspace GUID
        workspace = self._service_client.workspaces.get(
            resource_group_name=self._resource_group_name, workspace_name=self._workspace_name
        )
        workspace_guid = workspace.workspace_id
        workspace_location = workspace.location

        # Get environment asset ID
        asset_id = ASSET_ID_FORMAT.format(
            workspace_location,
            workspace_guid,
            AzureMLResourceType.ENVIRONMENT,
            name,
            version,
        )

        environment_ref = WorkspaceAssetReference(
            name=share_with_name if share_with_name else name,
            version=share_with_version if share_with_version else version,
            asset_id=asset_id,
        )

        with self._set_registry_client(registry_name):
            return self.create_or_update(environment_ref)

    @contextmanager
    def _set_registry_client(self, registry_name: str) -> None:
        """Sets the registry client for the environment operations.

        :param registry_name: Name of the registry.
        :type registry_name: str
        """
        rg_ = self._operation_scope._resource_group_name
        sub_ = self._operation_scope._subscription_id
        registry_ = self._operation_scope.registry_name
        client_ = self._service_client
        environment_versions_operation_ = self._version_operations

        try:
            _client, _rg, _sub = get_registry_client(self._service_client._config.credential, registry_name)
            self._operation_scope.registry_name = registry_name
            self._operation_scope._resource_group_name = _rg
            self._operation_scope._subscription_id = _sub
            self._service_client = _client
            self._version_operations = _client.environment_versions
            yield
        finally:
            self._operation_scope.registry_name = registry_
            self._operation_scope._resource_group_name = rg_
            self._operation_scope._subscription_id = sub_
            self._service_client = client_
            self._version_operations = environment_versions_operation_


def _preprocess_environment_name(environment_name: str) -> str:
    if environment_name.startswith(ARM_ID_PREFIX):
        return environment_name[len(ARM_ID_PREFIX) :]
    return environment_name
