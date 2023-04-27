# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict, Union
from marshmallow.exceptions import ValidationError as SchemaValidationError

from azure.core.exceptions import HttpResponseError
from azure.ai.ml._artifacts._artifact_utilities import _check_and_upload_path, _get_snapshot_path_info
from azure.ai.ml._artifacts._constants import (
    ASSET_PATH_ERROR,
    CHANGED_ASSET_PATH_MSG,
    CHANGED_ASSET_PATH_MSG_NO_PERSONAL_DATA,
)
from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._restclient.v2021_10_01_dataplanepreview import (
    AzureMachineLearningWorkspaces as ServiceClient102021Dataplane,
)
from azure.ai.ml._restclient.v2022_10_01_preview import AzureMachineLearningWorkspaces as ServiceClient102022
from azure.ai.ml._restclient.v2023_04_01 import AzureMachineLearningWorkspaces as ServiceClient042023
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope, _ScopeDependentOperations
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._asset_utils import (
    _get_existing_asset_name_and_version,
    get_content_hash_version,
    get_storage_info_for_non_registry_asset,
)
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml._utils._registry_utils import get_asset_body_for_registry_storage, get_sas_uri_for_registry_asset
from azure.ai.ml.entities._assets import Code
from azure.ai.ml.exceptions import (
    AssetPathException,
    ErrorCategory,
    ErrorTarget,
    ValidationErrorType,
    ValidationException,
)
from azure.ai.ml.operations._datastore_operations import DatastoreOperations

ops_logger = OpsLogger(__name__)
logger, module_logger = ops_logger.package_logger, ops_logger.module_logger


class CodeOperations(_ScopeDependentOperations):
    """Represents a client for performing operations on code assets.

    You should not instantiate this class directly. Instead, you should create MLClient and use this client via the
    property MLClient.code
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: Union[ServiceClient102022, ServiceClient102021Dataplane, ServiceClient042023],
        datastore_operations: DatastoreOperations,
        **kwargs: Dict,
    ):
        super(CodeOperations, self).__init__(operation_scope, operation_config)
        ops_logger.update_info(kwargs)
        self._service_client = service_client
        self._version_operation = service_client.code_versions
        self._container_operation = service_client.code_containers
        self._datastore_operation = datastore_operations
        self._init_kwargs = kwargs

    @monitor_with_activity(logger, "Code.CreateOrUpdate", ActivityType.PUBLICAPI)
    def create_or_update(self, code: Code) -> Code:
        """Returns created or updated code asset.

        If not already in storage, asset will be uploaded to the workspace's default datastore.

        :param code: Code asset object.
        :type code: Code
        :raises ~azure.ai.ml.exceptions.AssetPathException: Raised when the Code artifact path is
            already linked to another asset
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Code cannot be successfully validated.
            Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.EmptyDirectoryError: Raised if local path provided points to an empty directory.
        :return: Code asset object.
        :rtype: ~azure.ai.ml.entities.Code
        """
        try:
            name = code.name
            version = code.version
            sas_uri = None
            blob_uri = None

            if self._registry_name:
                sas_uri = get_sas_uri_for_registry_asset(
                    service_client=self._service_client,
                    name=name,
                    version=version,
                    resource_group=self._resource_group_name,
                    registry=self._registry_name,
                    body=get_asset_body_for_registry_storage(self._registry_name, "codes", name, version),
                )
            else:
                snapshot_path_info = _get_snapshot_path_info(code)
                if snapshot_path_info:
                    _, _, asset_hash = snapshot_path_info
                    existing_assets = list(
                        self._version_operation.list(
                            resource_group_name=self._resource_group_name,
                            workspace_name=self._workspace_name,
                            name=name,
                            hash=asset_hash,
                            hash_version=str(get_content_hash_version()),
                        )
                    )

                    if len(existing_assets) > 0:
                        existing_asset = existing_assets[0]
                        name, version = _get_existing_asset_name_and_version(existing_asset)
                        return self.get(name=name, version=version)
                    sas_info = get_storage_info_for_non_registry_asset(
                        service_client=self._service_client,
                        workspace_name=self._workspace_name,
                        name=name,
                        version=version,
                        resource_group=self._resource_group_name,
                    )
                    sas_uri = sas_info["sas_uri"]
                    blob_uri = sas_info["blob_uri"]

            code, _ = _check_and_upload_path(
                artifact=code,
                asset_operations=self,
                sas_uri=sas_uri,
                artifact_type=ErrorTarget.CODE,
                show_progress=self._show_progress,
                blob_uri=blob_uri,
            )

            # For anonymous code, if the code already exists in storage, we reuse the name,
            # version stored in the storage metadata so the same anonymous code won't be created again.
            if code._is_anonymous:
                name = code.name
                version = code.version

            code_version_resource = code._to_rest_object()

            result = (
                self._version_operation.begin_create_or_update(
                    name=name,
                    version=version,
                    registry_name=self._registry_name,
                    resource_group_name=self._operation_scope.resource_group_name,
                    body=code_version_resource,
                    **self._init_kwargs,
                ).result()
                if self._registry_name
                else self._version_operation.create_or_update(
                    name=name,
                    version=version,
                    workspace_name=self._workspace_name,
                    resource_group_name=self._operation_scope.resource_group_name,
                    body=code_version_resource,
                    **self._init_kwargs,
                )
            )

            if not result:
                return self.get(name=name, version=version)
            return Code._from_rest_object(result)
        except Exception as ex:
            if isinstance(ex, (ValidationException, SchemaValidationError)):
                log_and_raise_error(ex)
            elif isinstance(ex, HttpResponseError):
                # service side raises an exception if we attempt to update an existing asset's asset path
                if str(ex) == ASSET_PATH_ERROR:
                    raise AssetPathException(
                        message=CHANGED_ASSET_PATH_MSG,
                        target=ErrorTarget.CODE,
                        no_personal_data_message=CHANGED_ASSET_PATH_MSG_NO_PERSONAL_DATA,
                        error_category=ErrorCategory.USER_ERROR,
                    )
            raise ex

    @monitor_with_activity(logger, "Code.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, version: str) -> Code:
        """Returns information about the specified code asset.

        :param name: Name of the code asset.
        :type name: str
        :param version: Version of the code asset.
        :type version: str
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Code cannot be successfully validated.
            Details will be provided in the error message.
        :return: Code asset object.
        :rtype: ~azure.ai.ml.entities.Code
        """
        if not version:
            msg = "Code asset version must be specified as part of name parameter, in format 'name:version'."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.CODE,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )
        code_version_resource = (
            self._version_operation.get(
                name=name,
                version=version,
                resource_group_name=self._operation_scope.resource_group_name,
                registry_name=self._registry_name,
                **self._init_kwargs,
            )
            if self._registry_name
            else self._version_operation.get(
                name=name,
                version=version,
                resource_group_name=self._operation_scope.resource_group_name,
                workspace_name=self._workspace_name,
                **self._init_kwargs,
            )
        )
        return Code._from_rest_object(code_version_resource)
