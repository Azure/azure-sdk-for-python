# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from os import PathLike, path
from typing import Dict, Iterable, Optional, Union
from contextlib import contextmanager

from marshmallow.exceptions import ValidationError as SchemaValidationError

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._artifacts._artifact_utilities import (
    _check_and_upload_path,
    _get_default_datastore_info,
    _update_metadata,
)
from azure.ai.ml._artifacts._constants import (
    ASSET_PATH_ERROR,
    CHANGED_ASSET_PATH_MSG,
    CHANGED_ASSET_PATH_MSG_NO_PERSONAL_DATA,
)
from azure.ai.ml._utils._arm_id_utils import is_ARM_id_for_resource
from azure.ai.ml._utils._registry_utils import get_registry_client
from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._restclient.v2021_10_01_dataplanepreview import (
    AzureMachineLearningWorkspaces as ServiceClient102021Dataplane,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import ModelVersion # TODO: will need CustomAssetVersion in restclient contract to import from here
from azure.ai.ml._restclient.v2023_04_01_preview import AzureMachineLearningWorkspaces as ServiceClient042023Preview
from azure.ai.ml._scope_dependent_operations import (
    OperationConfig,
    OperationScope,
    _ScopeDependentOperations,
    OperationsContainer,
)
from azure.ai.ml.entities._assets._artifacts.code import Code

from azure.ai.ml.constants._common import ARM_ID_PREFIX
from azure.ai.ml._telemetry import ActivityType, monitor_with_activity
from azure.ai.ml._utils._asset_utils import (
    _archive_or_restore,
    _get_latest,
    _resolve_label_to_asset,
    _get_next_version_from_container,
)
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml._utils._registry_utils import (
    get_asset_body_for_registry_storage,
    get_sas_uri_for_registry_asset,
    get_storage_details_for_registry_assets,
)
from azure.ai.ml._utils._storage_utils import get_ds_name_and_path_prefix, get_storage_client
from azure.ai.ml._utils.utils import resolve_short_datastore_url, validate_ml_flow_folder
from azure.ai.ml.constants._common import ASSET_ID_FORMAT, AzureMLResourceType
from azure.ai.ml.entities._assets._artifacts.custom_asset import CustomAsset
from azure.ai.ml.entities._assets.workspace_asset_reference import WorkspaceAssetReference
from azure.ai.ml.entities._credentials import AccountKeyConfiguration
from azure.ai.ml.exceptions import (
    AssetPathException,
    ErrorCategory,
    ErrorTarget,
    ValidationErrorType,
    ValidationException,
)
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.ml.operations._datastore_operations import DatastoreOperations
from ._operation_orchestrator import OperationOrchestrator

ops_logger = OpsLogger(__name__)
logger, module_logger = ops_logger.package_logger, ops_logger.module_logger


class CustomAssetOperations(_ScopeDependentOperations):
    """CustomAssetOperations.

    You should not instantiate this class directly. Instead, you should create an MLClient instance that instantiates it
    for you and attaches it as an attribute.
    """

    # pylint: disable=unused-argument
    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: OperationConfig,
        service_client: Union[ServiceClient042023Preview, ServiceClient102021Dataplane],
        datastore_operations: DatastoreOperations,
        all_operations: OperationsContainer = None,
        **kwargs: Dict,
    ):
        super(CustomAssetOperations, self).__init__(operation_scope, operation_config)
        ops_logger.update_info(kwargs)
        self._custom_asset_versions_operation = service_client.custom_asset_versions
        self._custom_asset_container_operation = service_client.custom_asset_containers
        self._service_client = service_client
        self._datastore_operation = datastore_operations
        self._all_operations = all_operations

        # Maps a label to a function which given an asset name,
        # returns the asset associated with the label
        self._managed_label_resolver = {"latest": self._get_latest_version}

    @monitor_with_activity(logger, "CustomAsset.CreateOrUpdate", ActivityType.PUBLICAPI)
    def create_or_update(
        self, custom_asset: Union[CustomAsset, WorkspaceAssetReference]
    ) -> CustomAsset:
        """Returns created or updated custom asset.

        :param custom_asset: Custom asset object.
        :type custom_asset: ~azure.ai.ml.entities._assets._artifacts.CustomAsset
        :raises ~azure.ai.ml.exceptions.AssetPathException: Raised when the CustomAsset artifact path is
            already linked to another asset
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if CustomAsset cannot be successfully validated.
            Details will be provided in the error message.
        :raises ~azure.ai.ml.exceptions.EmptyDirectoryError: Raised if local path provided points to an empty directory.
        :return: Custom asset object.
        :rtype: ~azure.ai.ml.entities._assets._artifacts.CustomAsset
        """
        return NotImplementedError

    def _get(self, name: str, version: Optional[str] = None) -> "CustomAssetVersion":  # name:latest
        return NotImplementedError

    @monitor_with_activity(logger, "CustomAsset.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, version: Optional[str] = None, label: Optional[str] = None) -> CustomAsset:
        """Returns information about the specified custom asset.

        :param name: Name of the custom asset.
        :type name: str
        :param version: Version of the custom asset.
        :type version: str
        :param label: Label of the custom asset. (mutually exclusive with version)
        :type label: str
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Custom Asset cannot be successfully validated.
            Details will be provided in the error message.
        :return: Custom asset object.
        :rtype: ~azure.ai.ml.entities._assets._artifacts.CustomAsset
        """
        return self._get(name=name, version=version, label=label)


    @monitor_with_activity(logger, "CustomAsset.List", ActivityType.PUBLICAPI)
    def list(
        self,
        name: Optional[str] = None,
        stage: Optional[str] = None,
        *,
    ) -> Iterable[CustomAsset]:
        """List all custom assets in workspace.

        :param name: Name of the custom asset.
        :type name: Optional[str]
        :return: An iterator like instance of CustomAsset objects
        :rtype: ~azure.core.paging.ItemPaged[CustomAsset]
        """
        return NotImplementedError


    def _get_latest_version(self, name: str) -> Model:
        """Returns the latest version of the asset with the given name.

        Latest is defined as the most recently created, not the most recently updated.
        """
        return NotImplementedError
