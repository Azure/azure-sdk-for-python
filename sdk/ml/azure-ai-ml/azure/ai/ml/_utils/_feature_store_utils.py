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

from .utils import load_yaml

if TYPE_CHECKING:
    from azure.ai.ml.operations._feature_set_operations import _FeatureSetOperations
    from azure.ai.ml.operations._feature_store_entity_operations import _FeatureStoreEntityOperations


def read_feature_set_metadata_contents(*, path: str) -> Dict:
    metadata_path = str(Path(path, "FeaturesetSpec.yaml"))
    return load_yaml(metadata_path)


def _archive_or_restore(
    asset_operations: Union["_FeatureSetOperations", "_FeatureStoreEntityOperations"],
    version_operation: Union[
        "FeaturesetVersionsOperations",
        "FeaturestoreEntityVersionsOperations",
    ],
    is_archived: bool,
    name: str,
    version: str,
) -> None:
    resource_group_name = asset_operations._operation_scope._resource_group_name
    workspace_name = asset_operations._workspace_name

    version_resource = version_operation.get(
        name=name,
        version=version,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
    )
    version_resource.properties.is_archived = is_archived
    version_resource.properties.stage = "Archived" if is_archived else "Development"
    version_operation.begin_create_or_update(
        name=name,
        version=version,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
        body=version_resource,
    )
