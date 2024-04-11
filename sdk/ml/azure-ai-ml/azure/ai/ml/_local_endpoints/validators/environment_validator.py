# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import os
from pathlib import Path
from typing import Optional, Tuple, Union

from azure.ai.ml._artifacts._artifact_utilities import download_artifact_from_storage_url
from azure.ai.ml._utils._arm_id_utils import parse_name_label, parse_name_version
from azure.ai.ml._utils.utils import dump_yaml, is_url
from azure.ai.ml.constants._common import DefaultOpenEncoding
from azure.ai.ml.entities import OnlineDeployment
from azure.ai.ml.entities._assets.environment import BuildContext, Environment
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, RequiredLocalArtifactsNotFoundError, ValidationException
from azure.ai.ml.operations._environment_operations import EnvironmentOperations


def get_environment_artifacts(
    endpoint_name: str,
    deployment: OnlineDeployment,
    environment_operations: EnvironmentOperations,
    download_path: str,
) -> Optional[Tuple]:
    """Validates and returns artifacts from environment specification.

    :param endpoint_name: name of endpoint which this deployment is linked to
    :type endpoint_name: str
    :param deployment: deployment to validate
    :type deployment: OnlineDeployment
    :param environment_operations: The environment operations
    :type environment_operations: EnvironmentOperations
    :param download_path: The path to download to
    :type download_path: str
    :return: (base_image, conda_file_path, conda_file_contents, build_directory,
        dockerfile_contents, inference_config)

        Either base_image or build_directory should be None.
    :rtype: Union[
            Tuple[str, Optional[Path], str, None, None, Optional[Dict]],
            Tuple[None, None, None, Path, str, Optional[Dict]]
        ]
    :raises: azure.ai.ml._local_endpoints.errors.RequiredLocalArtifactsNotFoundError
    :raises: azure.ai.ml._local_endpoints.errors.CloudArtifactsNotSupportedError
    """
    # Validate environment for local endpoint
    if _environment_contains_cloud_artifacts(deployment=deployment):
        if isinstance(deployment.environment, Environment):
            environment_asset = deployment.environment
        else:
            name, version = parse_name_version(deployment.environment)
            label = None
            if not version:
                name, label = parse_name_label(deployment.environment)
            environment_asset = environment_operations.get(name=name, version=version, label=label)

        if not _cloud_environment_is_valid(environment=environment_asset):
            msg = (
                "Cloud environment must have environment.image "
                "or the environment.build.path set to work for local endpoints."
                " Note: Curated environments are not supported for local deployments."
            )
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.LOCAL_ENDPOINT,
                error_category=ErrorCategory.USER_ERROR,
            )
        return _get_cloud_environment_artifacts(
            environment_operations=environment_operations,
            environment_asset=environment_asset,
            download_path=download_path,
        )
    if not _local_environment_is_valid(deployment=deployment):
        raise RequiredLocalArtifactsNotFoundError(
            endpoint_name=endpoint_name,
            required_artifact="environment.image or environment.build.path",
            required_artifact_type=str(Environment),
            deployment_name=deployment.name,
        )
    return _get_local_environment_artifacts(deployment.base_path, deployment.environment)  # type: ignore[arg-type]


def _get_cloud_environment_artifacts(
    environment_operations: EnvironmentOperations,
    environment_asset: Environment,
    download_path: str,
) -> Tuple:
    """Retrieves the cloud environment's artifacts

    :param environment_operations: The environment operations
    :type environment_operations: EnvironmentOperations
    :param environment_asset: The cloud environment
    :type environment_asset: Environment
    :param download_path: The path to download to
    :type download_path: str
    :return: (base_image, conda_file_path, conda_file_contents, build_directory,
        dockerfile_contents, inference_config)

        Either base_image or build_directory should be None.
    :rtype: Union[
            Tuple[str, Optional[Path], str, None, None, Optional[Dict]],
            Tuple[None, None, None, Path, str, Optional[Dict]]
        ]
    """
    if environment_asset.build and environment_asset.build.path and is_url(environment_asset.build.path):
        environment_build_directory = download_artifact_from_storage_url(
            blob_url=str(environment_asset.build.path),
            destination=download_path,
            datastore_operation=environment_operations._datastore_operation,
            datastore_name="workspaceartifactstore",
        )
        dockerfile_path = Path(environment_build_directory, str(environment_asset.build.dockerfile_path))
        dockerfile_contents = dockerfile_path.read_text(encoding=DefaultOpenEncoding.READ)
        return (
            None,
            None,
            None,
            environment_build_directory,
            dockerfile_contents,
            environment_asset.inference_config,
        )
    conda_file_contents = dump_yaml(environment_asset.conda_file) if environment_asset.conda_file else None
    return (
        environment_asset.image,
        environment_asset.id,
        conda_file_contents,
        None,
        None,
        environment_asset.inference_config,
    )


def _get_local_environment_artifacts(base_path: Union[str, os.PathLike], environment: Environment) -> Optional[Tuple]:
    """Retrieves the local environment's artifacts

    :param base_path: The base path
    :type base_path: Union[str, os.PathLike]
    :param environment: The local environment
    :type environment: Environment
    :return: (base_image, conda_file_path, conda_file_contents, build_directory,
        dockerfile_contents, inference_config)

        Either base_image or build_directory should be None.
    :rtype: Union[
            Tuple[str, Optional[Path], str, None, None, Optional[Dict]],
            Tuple[None, None, None, Path, str, Optional[Dict]]
        ]
    """
    if environment.image:
        conda_file_contents = dump_yaml(environment.conda_file)
        return (
            environment.image,
            environment._conda_file_path,
            conda_file_contents,
            None,
            None,
            environment.inference_config,
        )
    if environment.build and environment.build.dockerfile_path:
        absolute_build_directory = Path(base_path, str(environment.build.path)).resolve()
        absolute_dockerfile_path = Path(absolute_build_directory, environment.build.dockerfile_path).resolve()
        dockerfile_contents = absolute_dockerfile_path.read_text(encoding=DefaultOpenEncoding.READ)
        return (
            None,
            None,
            None,
            absolute_build_directory,
            dockerfile_contents,
            environment.inference_config,
        )

    return None


def _local_environment_is_valid(deployment: OnlineDeployment):
    return isinstance(deployment.environment, Environment) and (
        deployment.environment.image
        or (
            deployment.environment.build is not None
            and isinstance(deployment.environment.build, BuildContext)
            and _local_build_context_is_valid(deployment.environment.build)
        )
    )


def _local_build_context_is_valid(build_context: BuildContext):
    return build_context.path is not None


def _cloud_environment_is_valid(environment: Environment):
    return isinstance(environment, Environment) and (
        environment.image or (environment.build and environment.build.path)
    )


def _environment_contains_cloud_artifacts(deployment: OnlineDeployment):
    return isinstance(deployment.environment, str) or (
        deployment.environment is not None and deployment.environment.id is not None
    )
