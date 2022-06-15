# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Dict, Union

from azure.ai.ml._artifacts._artifact_utilities import _check_and_upload_path
from azure.ai.ml._artifacts._constants import (
    ASSET_PATH_ERROR,
    CHANGED_ASSET_PATH_MSG,
    CHANGED_ASSET_PATH_MSG_NO_PERSONAL_DATA,
)
from azure.ai.ml.operations._datastore_operations import DatastoreOperations
from azure.ai.ml._restclient.v2022_05_01 import AzureMachineLearningWorkspaces as ServiceClient052022
from azure.ai.ml._scope_dependent_operations import OperationScope, _ScopeDependentOperations
from azure.ai.ml.entities._assets import Code
from azure.ai.ml._restclient.v2021_10_01_dataplanepreview import (
    AzureMachineLearningWorkspaces as ServiceClient102021Dataplane,
)
from azure.ai.ml._telemetry import AML_INTERNAL_LOGGER_NAMESPACE, ActivityType, monitor_with_activity
from azure.ai.ml._utils._registry_utils import get_sas_uri_for_registry_asset, get_asset_body_for_registry_storage
from azure.ai.ml._ml_exceptions import ValidationException, ErrorCategory, ErrorTarget, AssetPathException

logger = logging.getLogger(AML_INTERNAL_LOGGER_NAMESPACE + __name__)
logger.propagate = False
module_logger = logging.getLogger(__name__)


class CodeOperations(_ScopeDependentOperations):
    """Represents a client for performing operations on code assets

    You should not instantiate this class directly. Instead, you should create MLClient and
    use this client via the property MLClient.code
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        service_client: Union[ServiceClient052022, ServiceClient102021Dataplane],
        datastore_operations: DatastoreOperations,
        **kwargs: Dict,
    ):
        super(CodeOperations, self).__init__(operation_scope)
        if "app_insights_handler" in kwargs:
            logger.addHandler(kwargs.pop("app_insights_handler"))
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
        """
        name = code.name
        version = code.version
        sas_uri = None

        if self._registry_name:
            sas_uri = get_sas_uri_for_registry_asset(
                service_client=self._service_client,
                name=name,
                version=version,
                resource_group=self._resource_group_name,
                registry=self._registry_name,
                body=get_asset_body_for_registry_storage(self._registry_name, "codes", name, version),
            )
        code, _ = _check_and_upload_path(artifact=code, asset_operations=self, sas_uri=sas_uri)

        # For anonymous code, if the code already exists in storage, we reuse the name, version stored in the storage
        # metadata so the same anonymous code won't be created again.
        if code._is_anonymous:
            name = code.name
            version = code.version

        code_version_resource = code._to_rest_object()

        try:
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
        except Exception as e:
            # service side raises an exception if we attempt to update an existing asset's asset path
            if str(e) == ASSET_PATH_ERROR:
                raise AssetPathException(
                    message=CHANGED_ASSET_PATH_MSG,
                    tartget=ErrorTarget.CODE,
                    no_personal_data_message=CHANGED_ASSET_PATH_MSG_NO_PERSONAL_DATA,
                    error_category=ErrorCategory.USER_ERROR,
                )
            else:
                raise e

        if not result:
            return self.get(name=name, version=version)
        else:
            return Code._from_rest_object(result)

    @monitor_with_activity(logger, "Code.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, version: str) -> Code:
        """Returns information about the specified code asset.

        :param name: Name of the code asset.
        :type name: str
        :param version: Version of the code asset.
        :type version: str
        """
        if not version:
            msg = "Code asset version must be specified as part of name parameter, in format 'name:version'."
            raise ValidationException(
                message=msg,
                tartget=ErrorTarget.CODE,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        else:
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
