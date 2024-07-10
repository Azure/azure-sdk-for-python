# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from os import PathLike
from pathlib import Path
from typing import Tuple, Union

from azure.ai.ml._artifacts._artifact_utilities import download_artifact
from azure.ai.ml._utils._arm_id_utils import parse_prefixed_name_version
from azure.ai.ml._utils._storage_utils import AzureMLDatastorePathUri
from azure.ai.ml.entities import OnlineDeployment
from azure.ai.ml.entities._assets import Model
from azure.ai.ml.exceptions import RequiredLocalArtifactsNotFoundError
from azure.ai.ml.operations._model_operations import ModelOperations


def get_model_artifacts(
    endpoint_name: str,
    deployment: OnlineDeployment,
    model_operations: ModelOperations,
    download_path: str,
) -> Union[str, Tuple]:
    """Validates and returns model artifacts from deployment specification.

    :param endpoint_name: name of endpoint which this deployment is linked to
    :type endpoint_name: str
    :param deployment: deployment to validate
    :type deployment: OnlineDeployment
    :param model_operations: The model operations
    :type model_operations: ModelOperations
    :param download_path: The path to download to
    :type download_path: str
    :return: (model name, model version, the local directory of the model artifact)
    :rtype: Tuple[str, str, Path]
    :raises: azure.ai.ml._local_endpoints.errors.RequiredLocalArtifactsNotFoundError
    :raises: azure.ai.ml._local_endpoints.errors.CloudArtifactsNotSupportedError
    """
    # Validate model for local endpoint
    if _model_contains_cloud_artifacts(deployment=deployment):
        return _get_cloud_model_artifacts(
            model_operations=model_operations,
            model=str(deployment.model),
            download_path=download_path,
        )
    if not _local_model_is_valid(deployment=deployment):
        raise RequiredLocalArtifactsNotFoundError(
            endpoint_name=endpoint_name,
            required_artifact="model.path",
            required_artifact_type=str,
            deployment_name=deployment.name,
        )
    _model: Model = deployment.model  # type: ignore[assignment]
    _model_path: Union[str, PathLike] = _model.path  # type: ignore[assignment]
    return (
        _model.name,
        _model.version,
        Path(deployment._base_path, _model_path).resolve().parent,
    )


def _local_model_is_valid(deployment: OnlineDeployment):
    return deployment.model and isinstance(deployment.model, Model) and deployment.model.path


def _model_contains_cloud_artifacts(deployment: OnlineDeployment):
    # If the deployment.model is a string, then it is the cloud model name or full arm ID
    return isinstance(deployment.model, str) or (deployment.model is not None and deployment.model.id is not None)


def _get_cloud_model_artifacts(model_operations: ModelOperations, model: str, download_path: str) -> Tuple:
    if isinstance(model, Model):
        name = model.name
        version = model._version
        model_asset = model
    else:
        name, version = parse_prefixed_name_version(model)
        model_asset = model_operations.get(name=name, version=version)
    model_uri_path = AzureMLDatastorePathUri(model_asset.path)
    path = Path(model_uri_path.path)
    starts_with = path if path.is_dir() else path.parent
    return (
        name,
        version,
        download_artifact(
            starts_with=starts_with,
            destination=download_path,
            datastore_operation=model_operations._datastore_operation,
            datastore_name=model_uri_path.datastore,
        ),
    )
