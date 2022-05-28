# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Dict, Optional
from azure.core.paging import ItemPaged

from azure.ai.ml.constants import OrderString
from azure.ai.ml._operations import DatastoreOperations
from azure.ai.ml._restclient.v2022_05_01 import (
    AzureMachineLearningWorkspaces as ServiceClient052022,
)
from azure.ai.ml._restclient.v2022_02_01_preview.models import ListViewType
from azure.ai.ml._artifacts._artifact_utilities import _check_and_upload_path
from azure.ai.ml._scope_dependent_operations import OperationScope, _ScopeDependentOperations
from azure.ai.ml.entities._assets import Data
from azure.ai.ml._artifacts._constants import (
    ASSET_PATH_ERROR,
    CHANGED_ASSET_PATH_MSG,
    CHANGED_ASSET_PATH_MSG_NO_PERSONAL_DATA,
)
from azure.ai.ml._utils._asset_utils import (
    _create_or_update_autoincrement,
    _get_latest,
    _resolve_label_to_asset,
    _archive_or_restore,
)
from azure.ai.ml._utils.utils import get_list_view_type

from azure.ai.ml._telemetry import AML_INTERNAL_LOGGER_NAMESPACE, ActivityType, monitor_with_activity
from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, ValidationException, AssetPathException

logger = logging.getLogger(AML_INTERNAL_LOGGER_NAMESPACE + __name__)
logger.propagate = False
module_logger = logging.getLogger(__name__)


class DataOperations(_ScopeDependentOperations):
    def __init__(
        self,
        operation_scope: OperationScope,
        service_client: ServiceClient052022,
        datastore_operations: DatastoreOperations,
        **kwargs: Dict,
    ):

        super(DataOperations, self).__init__(operation_scope)
        if "app_insights_handler" in kwargs:
            logger.addHandler(kwargs.pop("app_insights_handler"))
        self._operation = service_client.data_versions
        self._container_operation = service_client.data_containers
        self._datastore_operation = datastore_operations
        self._init_kwargs = kwargs

        # Maps a label to a function which given an asset name,
        # returns the asset associated with the label
        self._managed_label_resolver = {"latest": self._get_latest_version}

    @monitor_with_activity(logger, "Data.List", ActivityType.PUBLICAPI)
    def list(
        self, name: Optional[str] = None, *, list_view_type: ListViewType = ListViewType.ACTIVE_ONLY
    ) -> ItemPaged[Data]:
        """List the data assets of the workspace.

        :param name: Name of a specific data asset, optional.
        :type name: Optional[str]
        :param list_view_type: View type for including/excluding (for example) archived data assets. Default: ACTIVE_ONLY.
        :type list_view_type: Optional[ListViewType]
        :return: An iterator like instance of Data objects
        :rtype: ~azure.core.paging.ItemPaged[Data]
        """
        if name:
            return self._operation.list(
                name=name,
                workspace_name=self._workspace_name,
                cls=lambda objs: [Data._from_rest_object(obj) for obj in objs],
                list_view_type=list_view_type,
                **self._scope_kwargs,
            )
        else:
            return self._container_operation.list(
                workspace_name=self._workspace_name,
                cls=lambda objs: [Data._from_container_rest_object(obj) for obj in objs],
                list_view_type=list_view_type,
                **self._scope_kwargs,
            )

    @monitor_with_activity(logger, "Data.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, version: Optional[str] = None, label: Optional[str] = None) -> Data:
        """Get the specified data asset.

        :param name: Name of data asset.
        :type name: str
        :param version: Version of data asset.
        :type version: str
        :param label: Label of the data asset. (mutually exclusive with version)
        :type label: str
        :return: Data asset object.
        """
        if version and label:
            msg = "Cannot specify both version and label."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.DATA,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )

        if label:
            return _resolve_label_to_asset(self, name, label)

        if not version:
            msg = "Must provide either version or label."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.DATA,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        data_version_resource = self._operation.get(
            resource_group_name=self._resource_group_name,
            workspace_name=self._workspace_name,
            name=name,
            version=version,
            **self._init_kwargs,
        )

        return Data._from_rest_object(data_version_resource)

    @monitor_with_activity(logger, "Data.CreateOrUpdate", ActivityType.PUBLICAPI)
    def create_or_update(self, data: Data) -> Data:
        """Returns created or updated data asset.

        If not already in storage, asset will be uploaded to datastore name specified in data.datastore or the workspace's default datastore.

        :param data: Data asset object.
        :type data: Data
        :return: Data asset object.
        """
        name = data.name
        version = data.version

        data, _ = _check_and_upload_path(artifact=data, asset_operations=self)
        data_version_resource = data._to_rest_object()
        auto_increment_version = data._auto_increment_version
        try:
            if auto_increment_version:
                result = _create_or_update_autoincrement(
                    name=data.name,
                    body=data_version_resource,
                    version_operation=self._operation,
                    container_operation=self._container_operation,
                    resource_group_name=self._operation_scope.resource_group_name,
                    workspace_name=self._workspace_name,
                    **self._init_kwargs,
                )
            else:
                result = self._operation.create_or_update(
                    name=name,
                    version=version,
                    workspace_name=self._workspace_name,
                    body=data_version_resource,
                    **self._scope_kwargs,
                )
        except Exception as e:
            # service side raises an exception if we attempt to update an existing asset's asset path
            if str(e) == ASSET_PATH_ERROR:
                raise AssetPathException(
                    message=CHANGED_ASSET_PATH_MSG,
                    target=ErrorTarget.DATA,
                    no_personal_data_message=CHANGED_ASSET_PATH_MSG_NO_PERSONAL_DATA,
                    error_category=ErrorCategory.USER_ERROR,
                )
            else:
                raise e

        return Data._from_rest_object(result)

    @monitor_with_activity(logger, "Data.Archive", ActivityType.PUBLICAPI)
    def archive(self, name: str, version: str = None, label: str = None) -> None:
        """Archive a data asset.

        :param name: Name of data asset.
        :type name: str
        :param version: Version of data asset.
        :type version: str
        :param label: Label of the data asset. (mutually exclusive with version)
        :type label: str
        :return: None
        """

        _archive_or_restore(
            asset_operations=self,
            version_operation=self._operation,
            container_operation=self._container_operation,
            is_archived=True,
            name=name,
            version=version,
            label=label,
        )

    @monitor_with_activity(logger, "Data.Restore", ActivityType.PUBLICAPI)
    def restore(self, name: str, version: str = None, label: str = None) -> None:
        """Restore an archived data asset.

        :param name: Name of data asset.
        :type name: str
        :param version: Version of data asset.
        :type version: str
        :param label: Label of the data asset. (mutually exclusive with version)
        :type label: str
        :return: None
        """

        _archive_or_restore(
            asset_operations=self,
            version_operation=self._operation,
            container_operation=self._container_operation,
            is_archived=False,
            name=name,
            version=version,
            label=label,
        )

    def _get_latest_version(self, name: str) -> Data:
        """Returns the latest version of the asset with the given name.

        Latest is defined as the most recently created, not the most recently updated.
        """
        result = _get_latest(name, self._operation, self._resource_group_name, self._workspace_name)
        return Data._from_rest_object(result)
