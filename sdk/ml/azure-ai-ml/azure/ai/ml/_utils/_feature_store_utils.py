# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Dict, Union
from urllib.parse import urlparse

import yaml

from .._artifacts._artifact_utilities import get_datastore_info, get_storage_client
from .._restclient.v2023_10_01.operations import (  # pylint: disable = unused-import
    FeaturesetContainersOperations,
    FeaturesetVersionsOperations,
    FeaturestoreEntityContainersOperations,
    FeaturestoreEntityVersionsOperations,
)
from ..constants._common import DefaultOpenEncoding
from ..exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException
from ..operations._datastore_operations import DatastoreOperations
from ._storage_utils import AzureMLDatastorePathUri
from .utils import load_yaml

if TYPE_CHECKING:
    from azure.ai.ml.operations._feature_set_operations import FeatureSetOperations
    from azure.ai.ml.operations._feature_store_entity_operations import FeatureStoreEntityOperations


def read_feature_set_metadata(*, path: str) -> Dict:
    metadata_path = str(Path(path, "FeatureSetSpec.yaml"))
    return load_yaml(metadata_path)


def read_remote_feature_set_spec_metadata(
    *,
    base_uri: str,
    datastore_operations: DatastoreOperations,
) -> Union[Dict, None]:
    scheme = urlparse(base_uri).scheme
    if scheme == "azureml":
        datastore_path_uri = AzureMLDatastorePathUri(base_uri)
        datastore_info = get_datastore_info(datastore_operations, datastore_path_uri.datastore)
        storage_client = get_storage_client(**datastore_info)
        with TemporaryDirectory() as tmp_dir:
            starts_with = datastore_path_uri.path.rstrip("/")
            storage_client.download(f"{starts_with}/FeatureSetSpec.yaml", tmp_dir)
            downloaded_spec_path = Path(tmp_dir, "FeatureSetSpec.yaml")
            with open(downloaded_spec_path, "r", encoding=DefaultOpenEncoding.READ) as f:
                return yaml.safe_load(f)
    return None


def _archive_or_restore(
    asset_operations: Union["FeatureSetOperations", "FeatureStoreEntityOperations"],
    version_operation: Union[
        "FeaturesetVersionsOperations",
        "FeaturestoreEntityVersionsOperations",
    ],
    is_archived: bool,
    name: str,
    version: str,
    **kwargs,
) -> None:
    resource_group_name = asset_operations._operation_scope._resource_group_name
    workspace_name = asset_operations._workspace_name

    version_resource = version_operation.get(
        name=name,
        version=version,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
    )

    if version_resource.properties.stage == "Archived" and is_archived:
        raise ValidationException(
            message="Asset version is already archived: {}:{}".format(name, version),
            no_personal_data_message="Asset version is already archived",
            target=ErrorTarget.ASSET,
            error_category=ErrorCategory.USER_ERROR,
            error_type=ValidationErrorType.INVALID_VALUE,
        )

    if version_resource.properties.stage != "Archived" and not is_archived:
        raise ValidationException(
            message="Cannot restore non-archived asset version: {}:{}".format(name, version),
            no_personal_data_message="Asset version is not archived",
            target=ErrorTarget.ASSET,
            error_category=ErrorCategory.USER_ERROR,
            error_type=ValidationErrorType.INVALID_VALUE,
        )

    version_resource.properties.is_archived = is_archived
    version_resource.properties.stage = "Archived" if is_archived else "Development"
    poller = version_operation.begin_create_or_update(
        name=name,
        version=version,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
        body=version_resource,
        **kwargs,
    )
    poller.result()


def _datetime_to_str(datetime_obj: Union[str, datetime]):
    return datetime_obj if isinstance(datetime_obj, str) else datetime_obj.isoformat()
