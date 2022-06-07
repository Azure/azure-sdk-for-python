# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from pathlib import Path

from azure.ai.ml._artifacts._artifact_utilities import download_artifact_from_blob_url
from azure.ai.ml._local_endpoints.errors import RequiredLocalArtifactsNotFoundError
from azure.ai.ml._utils._arm_id_utils import parse_prefixed_name_version
from azure.ai.ml._operations.code_operations import CodeOperations
from azure.ai.ml.entities import OnlineDeployment
from azure.ai.ml.entities._assets import Code
from azure.ai.ml.entities._deployment.code_configuration import CodeConfiguration
from azure.ai.ml._utils.utils import is_url
from azure.ai.ml.constants import ARM_ID_PREFIX


class CodeValidator:
    def get_code_configuration_artifacts(
        self, endpoint_name: str, deployment: OnlineDeployment, code_operations: CodeOperations, download_path: str
    ) -> str:
        """Validates and returns code artifacts from deployment specification.

        :param endpoint_name: name of endpoint which this deployment is linked to
        :type endpoint_name: str
        :param deployment: deployment to validate
        :type deployment: OnlineDeployment entity
        :return: local path to code
        :type return: str
        :raises: azure.ai.ml._local_endpoints.errors.RequiredLocalArtifactsNotFoundError
        :raises: azure.ai.ml._local_endpoints.errors.CloudArtifactsNotSupportedError
        """
        # Validate code for local endpoint
        if not deployment.code_configuration:
            return None

        if not isinstance(deployment.code_configuration, CodeConfiguration):
            raise RequiredLocalArtifactsNotFoundError(
                endpoint_name=endpoint_name,
                required_artifact="code_configuration",
                required_artifact_type=str(str),
                deployment_name=deployment.name,
            )

        if self._code_configuration_contains_cloud_artifacts(deployment=deployment):
            return self._get_cloud_code_configuration_artifacts(
                deployment.code_configuration.code, code_operations, download_path
            )

        if not self._local_code_path_is_valid(deployment=deployment):
            raise RequiredLocalArtifactsNotFoundError(
                endpoint_name=endpoint_name,
                required_artifact="code_configuration.code",
                required_artifact_type=str(str),
                deployment_name=deployment.name,
            )
        if not self._local_scoring_script_is_valid(deployment=deployment):
            raise RequiredLocalArtifactsNotFoundError(
                endpoint_name=endpoint_name,
                required_artifact="code_configuration.scoring_script",
                required_artifact_type=str(str),
                deployment_name=deployment.name,
            )
        return self._get_local_code_configuration_artifacts(deployment)

    def _local_code_path_is_valid(self, deployment: OnlineDeployment):
        return (
            deployment.code_configuration
            and deployment.code_configuration.code
            and isinstance(deployment.code_configuration.code, str)
            and self._get_local_code_configuration_artifacts(deployment).exists()
        )

    def _local_scoring_script_is_valid(self, deployment: OnlineDeployment):
        return deployment.code_configuration and deployment.code_configuration.scoring_script

    def _code_configuration_contains_cloud_artifacts(self, deployment: OnlineDeployment):
        # If the deployment.code_configuration.code is a string, then it is the cloud code artifact name or full arm ID

        return isinstance(deployment.code_configuration.code, str) and (
            is_url(deployment.code_configuration.code) or deployment.code_configuration.code.startswith(ARM_ID_PREFIX)
        )

    def _get_local_code_configuration_artifacts(
        self,
        deployment: OnlineDeployment,
    ) -> Path:
        return Path(deployment._base_path, deployment.code_configuration.code).resolve()

    def _get_cloud_code_configuration_artifacts(
        self, code: str, code_operations: CodeOperations, download_path: str
    ) -> str:
        name, version = parse_prefixed_name_version(code)
        code_asset = code_operations.get(name=name, version=version)

        return download_artifact_from_blob_url(
            blob_url=code_asset.path,
            destination=download_path,
            datastore_operation=code_operations._datastore_operation,
            datastore_name=None,  # Use default datastore of current workspace
        )
