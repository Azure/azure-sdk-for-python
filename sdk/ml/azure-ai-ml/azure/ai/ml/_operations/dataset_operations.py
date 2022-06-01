# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import Dict, Iterable

from azure.ai.ml._operations import DatastoreOperations
from azure.ai.ml._restclient.v2021_10_01 import AzureMachineLearningWorkspaces as ServiceClient102021
from azure.ai.ml._utils._asset_utils import _create_or_update_autoincrement, _get_latest, _resolve_label_to_asset
from azure.ai.ml._utils._arm_id_utils import is_ARM_id_for_resource, get_datastore_arm_id
from azure.ai.ml._artifacts._artifact_utilities import (
    _check_and_upload_path,
    _update_metadata,
    _get_default_datastore_info,
)
from azure.ai.ml._scope_dependent_operations import OperationScope, _ScopeDependentOperations
from azure.ai.ml.entities._assets import Dataset
from azure.ai.ml._artifacts._constants import (
    ASSET_PATH_ERROR,
    CHANGED_ASSET_PATH_MSG,
    CHANGED_ASSET_PATH_MSG_NO_PERSONAL_DATA,
)

from azure.ai.ml._telemetry import AML_INTERNAL_LOGGER_NAMESPACE, ActivityType, monitor_with_activity
from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, ValidationException, AssetPathException

logger = logging.getLogger(AML_INTERNAL_LOGGER_NAMESPACE + __name__)
logger.propagate = False
module_logger = logging.getLogger(__name__)


class DatasetOperations(_ScopeDependentOperations):
    def __init__(
        self,
        operation_scope: OperationScope,
        service_client: ServiceClient102021,
        datastore_operations: DatastoreOperations,
        **kwargs: Dict,
    ):

        super(DatasetOperations, self).__init__(operation_scope)
        if "app_insights_handler" in kwargs:
            logger.addHandler(kwargs.pop("app_insights_handler"))
        self._operation = service_client.dataset_versions
        self._container_operation = service_client.dataset_containers
        self._datastore_operation = datastore_operations
        self._init_kwargs = kwargs

        # Maps a label to a function which given an asset name,
        # returns the asset associated with the label
        self._managed_label_resolver = {"latest": self._get_latest_version}

    @monitor_with_activity(logger, "Dataset.List", ActivityType.PUBLICAPI)
    def list(self, name: str = None) -> Iterable[Dataset]:
        """List the dataset assets of the workspace.

        :param name: Name of a specific dataset asset, optional.
        :type name: Optional[str]
        :return: An iterator like instance of Dataset objects
        :rtype: ~azure.core.paging.ItemPaged[Dataset]
        """
        if name:
            return self._operation.list(
                name=name,
                workspace_name=self._workspace_name,
                cls=lambda objs: [Dataset._from_rest_object(obj) for obj in objs],
                **self._scope_kwargs,
            )
        else:
            return self._container_operation.list(
                workspace_name=self._workspace_name,
                cls=lambda objs: [Dataset._from_container_rest_object(obj) for obj in objs],
                **self._scope_kwargs,
            )

    @monitor_with_activity(logger, "Dataset.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, version: str = None, label: str = None) -> Dataset:
        """Get the specified dataset asset.

        :param name: Name of dataset asset.
        :type name: str
        :param version: Version of dataset asset.
        :type version: str
        :param label: Label of the dataset asset. (mutually exclusive with version)
        :type label: str
        :return: Dataset asset object.
        """
        if version and label:
            msg = "Cannot specify both version and label."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.DATASET,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )

        if label:
            return _resolve_label_to_asset(self, name, label)

        if not version:
            msg = "Must provide either version or label."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.DATASET,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        dataset_version_resource = self._operation.get(
            name,
            version,
            self._resource_group_name,
            self._workspace_name,
            **self._init_kwargs,
        )

        return Dataset._from_rest_object(dataset_version_resource)

    @monitor_with_activity(logger, "Dataset.CreateOrUpdate", ActivityType.PUBLICAPI)
    def create_or_update(self, dataset: Dataset) -> Dataset:
        """Returns created or updated dataset asset.

        If not already in storage, asset will be uploaded to the workspace's default datastore.

        :param dataset: Dataset asset object.
        :type dataset: Dataset
        :return: Dataset asset object.
        """

        dataset._validate()

        name = dataset.name
        version = dataset.version

        dataset, indicator_file = _check_and_upload_path(artifact=dataset, asset_operations=self)
        dataset_version_resource = dataset._to_rest_object()
        auto_increment_version = dataset._auto_increment_version
        try:
            if auto_increment_version:
                result = _create_or_update_autoincrement(
                    name=dataset.name,
                    body=dataset_version_resource,
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
                    body=dataset_version_resource,
                    **self._scope_kwargs,
                )
        except Exception as e:
            # service side raises an exception if we attempt to update an existing asset's asset path
            if str(e) == ASSET_PATH_ERROR:
                raise AssetPathException(
                    message=CHANGED_ASSET_PATH_MSG,
                    target=ErrorTarget.DATASET,
                    no_personal_data_message=CHANGED_ASSET_PATH_MSG_NO_PERSONAL_DATA,
                    error_category=ErrorCategory.USER_ERROR,
                )
            else:
                raise e

        dataset = Dataset._from_rest_object(result)
        if auto_increment_version and indicator_file:
            datastore_info = _get_default_datastore_info(self._datastore_operation)
            _update_metadata(
                dataset.name, dataset.version, indicator_file=indicator_file, datastore_info=datastore_info
            )  # update version in storage

        return dataset

    def _get_latest_version(self, name: str) -> Dataset:
        """Returns the latest version of the asset with the given name.

        Latest is defined as the most recently created, not the most recently updated.
        """
        result = _get_latest(name, self._operation, self._resource_group_name, self._workspace_name)
        return Dataset._from_rest_object(result)
