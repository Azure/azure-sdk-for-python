# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from pathlib import Path
from typing import Iterable, Tuple

from azure.ai.ml.entities import OnlineDeployment
from azure.ai.ml.entities._assets.environment import BuildContext, Environment

from azure.ai.ml._local_endpoints.errors import RequiredLocalArtifactsNotFoundError
from azure.core.exceptions import AzureError

from azure.ai.ml.operations._environment_operations import EnvironmentOperations
from azure.ai.ml._artifacts._artifact_utilities import download_artifact_from_storage_url

from azure.ai.ml._utils._arm_id_utils import parse_name_version
from azure.ai.ml._utils.utils import convert_ordered_dict_to_yaml_str, is_url
from azure.ai.ml._ml_exceptions import ValidationException, ErrorCategory, ErrorTarget


class EnvironmentValidator:
    def get_environment_artifacts(
        self,
        endpoint_name: str,
        deployment: OnlineDeployment,
        environment_operations: EnvironmentOperations,
        download_path: str,
    ) -> Iterable[str]:
        """Validates and returns artifacts from environment specification.

        :param endpoint_name: name of endpoint which this deployment is linked to
        :type endpoint_name: str
        :param deployment: deployment to validate
        :type deployment: OnlineDeployment entity
        :return: (base_image, conda_file_path, conda_file_contents, build_directory, dockerfile_contents, inference_config) - Either base_image or build_directory should be None.
        :type return: Iterable[str]
        :raises: azure.ai.ml._local_endpoints.errors.RequiredLocalArtifactsNotFoundError
        :raises: azure.ai.ml._local_endpoints.errors.CloudArtifactsNotSupportedError
        """
        # Validate environment for local endpoint
        if self._environment_contains_cloud_artifacts(deployment=deployment):
            name, version = parse_name_version(deployment.environment)
            environment_asset = environment_operations.get(name=name, version=version)
            if not self._cloud_environment_is_valid(environment=environment_asset):
                msg = "Cloud environment must have environment.image "
                +"or the environment.build.path set to work for local endpoints."
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.LOCAL_ENDPOINT,
                    error_category=ErrorCategory.USER_ERROR,
                )
            return self._get_cloud_environment_artifacts(
                environment_operations=environment_operations,
                environment_asset=environment_asset,
                download_path=download_path,
            )
        if not self._local_environment_is_valid(deployment=deployment):
            raise RequiredLocalArtifactsNotFoundError(
                endpoint_name=endpoint_name,
                required_artifact="environment.image or environment.build.path",
                required_artifact_type=str(Environment),
                deployment_name=deployment.name,
            )
        return self._get_local_environment_artifacts(deployment.base_path, deployment.environment)

    def _get_cloud_environment_artifacts(
        self,
        environment_operations: EnvironmentOperations,
        environment_asset: Environment,
        download_path: str,
    ) -> Tuple[str, str, str, str]:
        """
        :return: (base_image, conda_file_path, conda_file_contents, build_directory, dockerfile_contents) - Either base_image or build_directory should be None.
        :type return: Iterable[str]
        """
        if environment_asset.build and environment_asset.build.path and is_url(environment_asset.build.path):
            environment_build_directory = download_artifact_from_storage_url(
                blob_url=environment_asset.build.path,
                destination=download_path,
                datastore_operation=environment_operations._datastore_operation,
                datastore_name=None,
            )
            dockerfile_path = Path(environment_build_directory, environment_asset.build.dockerfile_path)
            dockerfile_contents = dockerfile_path.read_text()
            return (
                None,
                None,
                None,
                environment_build_directory,
                dockerfile_contents,
                environment_asset.inference_config,
            )
        conda_file_contents = (
            convert_ordered_dict_to_yaml_str(environment_asset.conda_file) if environment_asset.conda_file else None
        )
        return (
            environment_asset.image,
            environment_asset.id,
            conda_file_contents,
            None,
            None,
            environment_asset.inference_config,
        )

    def _get_local_environment_artifacts(self, base_path: str, environment: Environment):
        """
        :return: (base_image, conda_file_path, conda_file_contents, build_directory, dockerfile_contents, inference_config) - Either base_image or build_directory should be None.
        :type return: Iterable[str]
        """
        if environment.image:
            conda_file_contents = convert_ordered_dict_to_yaml_str(environment.conda_file)
            return (
                environment.image,
                environment._conda_file_path,
                conda_file_contents,
                None,
                None,
                environment.inference_config,
            )

        dockerfile_contents = None
        if environment.build and environment.build.dockerfile_path:
            absolute_build_directory = Path(base_path, environment.build.path).resolve()
            absolute_dockerfile_path = Path(absolute_build_directory, environment.build.dockerfile_path).resolve()
            dockerfile_contents = absolute_dockerfile_path.read_text()
            return (None, None, None, absolute_dockerfile_path, dockerfile_contents, environment.inference_config)

    def _local_environment_is_valid(self, deployment: OnlineDeployment):
        return isinstance(deployment.environment, Environment) and (
            deployment.environment.image
            or (
                deployment.environment.build is not None
                and isinstance(deployment.environment.build, BuildContext)
                and self._local_build_context_is_valid(deployment.environment.build)
            )
        )

    def _local_build_context_is_valid(self, build_context: BuildContext):
        return build_context.path is not None

    def _cloud_environment_is_valid(self, environment: Environment):
        return isinstance(environment, Environment) and (
            environment.image or (environment.build and environment.build.path)
        )

    def _environment_contains_cloud_artifacts(self, deployment: OnlineDeployment):
        return isinstance(deployment.environment, str)
