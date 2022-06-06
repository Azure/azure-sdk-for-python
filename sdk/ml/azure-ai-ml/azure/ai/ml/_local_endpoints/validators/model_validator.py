# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from pathlib import Path

from azure.ai.ml.entities import OnlineDeployment
from azure.ai.ml.entities._assets import Model

from azure.ai.ml._operations.model_operations import ModelOperations

from azure.ai.ml._local_endpoints.errors import RequiredLocalArtifactsNotFoundError
from azure.ai.ml._artifacts._artifact_utilities import download_artifact
from azure.ai.ml._utils._arm_id_utils import parse_prefixed_name_version, is_ARM_id_for_resource
from azure.ai.ml._utils._storage_utils import AzureMLDatastorePathUri


class ModelValidator:
    def get_model_artifacts(
        self, endpoint_name: str, deployment: OnlineDeployment, model_operations: ModelOperations, download_path: str
    ) -> str:
        """Validates and returns model artifacts from deployment specification.

        :param endpoint_name: name of endpoint which this deployment is linked to
        :type endpoint_name: str
        :param deployment: deployment to validate
        :type deployment: OnlineDeployment entity
        :return: (model name, model version, the local directory of the model artifact)
        :type return: (str, str, str)
        :raises: azure.ai.ml._local_endpoints.errors.RequiredLocalArtifactsNotFoundError
        :raises: azure.ai.ml._local_endpoints.errors.CloudArtifactsNotSupportedError
        """
        # Validate model for local endpoint
        if self._model_contains_cloud_artifacts(deployment=deployment):
            return self._get_cloud_model_artifacts(
                model_operations=model_operations,
                model=deployment.model,
                download_path=download_path,
            )
        if not self._local_model_is_valid(deployment=deployment):
            raise RequiredLocalArtifactsNotFoundError(
                endpoint_name=endpoint_name,
                required_artifact="model.path",
                required_artifact_type=str,
                deployment_name=deployment.name,
            )
        return (
            deployment.model.name,
            deployment.model.version,
            Path(deployment._base_path, deployment.model.path).resolve().parent,
        )

    def _local_model_is_valid(self, deployment: OnlineDeployment):
        return deployment.model and isinstance(deployment.model, Model) and deployment.model.path

    def _model_contains_cloud_artifacts(self, deployment: OnlineDeployment):
        # If the deployment.model is a string, then it is the cloud model name or full arm ID
        return isinstance(deployment.model, str)

    def _get_cloud_model_artifacts(self, model_operations: ModelOperations, model: str, download_path: str) -> str:
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
