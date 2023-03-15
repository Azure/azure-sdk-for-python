# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from pathlib import Path
from typing import TYPE_CHECKING, Dict, Optional, Union


from azure.ai.ml._restclient.v2023_02_01_preview.operations import (  # pylint: disable = unused-import
    FeaturesetContainersOperations,
    FeaturesetVersionsOperations,
    FeaturestoreEntityContainersOperations,
    FeaturestoreEntityVersionsOperations,
)
from azure.ai.ml.entities._assets.asset import Asset
from azure.ai.ml.exceptions import (
    ErrorCategory,
    ErrorTarget,
    ValidationErrorType,
    ValidationException,
)
from azure.core.exceptions import ResourceNotFoundError

from .utils import load_yaml

if TYPE_CHECKING:
    from azure.ai.ml.operations._feature_set_operations import _FeatureSetOperations
    from azure.ai.ml.operations._feature_store_entity_operations import _FeatureStoreEntityOperations


def read_feature_set_metadata_contents(*, path: str) -> Dict:
    metadata_path = str(Path(path, "FeaturesetSpec.yaml"))
    return load_yaml(metadata_path)


def _get_latest_version_from_container(
    asset_name: str,
    container_operation: Union[
        "FeaturesetContainersOperations",
        "FeaturestoreEntityContainersOperations",
    ],
    resource_group_name: str,
    workspace_name: str,
    **kwargs,
) -> str:
    try:
        container = container_operation.get_entity(
            name=asset_name,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
            **kwargs,
        )
        version = container.properties.latest_version

    except ResourceNotFoundError:
        message = f"Asset {asset_name} does not exist in feature store {workspace_name}."
        no_personal_data_message = "Asset {asset_name} does not exist in feature store {workspace_name}."
        raise ValidationException(
            message=message,
            no_personal_data_message=no_personal_data_message,
            target=ErrorTarget.ASSET,
            error_category=ErrorCategory.USER_ERROR,
            error_type=ValidationErrorType.RESOURCE_NOT_FOUND,
        )
    return version


def _archive_or_restore(
    asset_operations: Union["_FeatureSetOperations", "_FeatureStoreEntityOperations"],
    version_operation: Union[
        "FeaturesetVersionsOperations",
        "FeaturestoreEntityVersionsOperations",
    ],
    container_operation: Union[
        "FeaturesetContainersOperations",
        "FeaturestoreEntityContainersOperations",
    ],
    is_archived: bool,
    name: str,
    version: Optional[str] = None,
    label: Optional[str] = None,
) -> None:
    resource_group_name = asset_operations._operation_scope._resource_group_name
    workspace_name = asset_operations._workspace_name
    if version and label:
        msg = "Cannot specify both version and label."
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.ASSET,
            error_category=ErrorCategory.USER_ERROR,
            error_type=ValidationErrorType.RESOURCE_NOT_FOUND,
        )
    if label:
        version = _resolve_label_to_asset(asset_operations, name, label).version

    if version:
        version_resource = version_operation.get(
            name=name,
            version=version,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
        )
        version_resource.properties.is_archived = is_archived
        version_operation.begin_create_or_update(
            name=name,
            version=version,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
            body=version_resource,
        )
    else:
        container_resource = container_operation.get_entity(
            name=name,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
        )
        container_resource.properties.is_archived = is_archived
        container_operation.begin_create_or_update(
            name=name,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
            body=container_resource,
        )


def _resolve_label_to_asset(
    assetOperations: Union[
        "_FeatureSetOperations",
        "_FeatureStoreEntityOperations",
    ],
    name: str,
    label: str,
) -> Asset:
    """Returns the asset referred to by the given label.

    Throws if label does not refer to a version of the named asset
    """

    resolver = assetOperations._managed_label_resolver.get(label, None)
    if not resolver:
        msg = "Asset {} with version label {} does not exist in workspace."
        raise ValidationException(
            message=msg.format(name, label),
            no_personal_data_message=msg.format("[name]", "[label]"),
            target=ErrorTarget.ASSET,
            error_type=ValidationErrorType.RESOURCE_NOT_FOUND,
        )
    return resolver(name)
