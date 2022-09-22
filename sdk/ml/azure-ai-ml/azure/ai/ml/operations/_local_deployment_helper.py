# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import json
import logging
import shutil
from pathlib import Path
from typing import Iterable

from docker.models.containers import Container

from azure.ai.ml._local_endpoints import AzureMlImageContext, DockerClient, DockerfileResolver, LocalEndpointMode
from azure.ai.ml._local_endpoints.errors import InvalidLocalEndpointError, LocalEndpointNotFoundError
from azure.ai.ml._local_endpoints.validators import CodeValidator, EnvironmentValidator, ModelValidator
from azure.ai.ml._scope_dependent_operations import OperationsContainer
from azure.ai.ml._utils._endpoint_utils import local_endpoint_polling_wrapper
from azure.ai.ml.constants import AzureMLResourceType, LocalEndpointConstants
from azure.ai.ml.entities import OnlineDeployment

module_logger = logging.getLogger(__name__)


class _LocalDeploymentHelper(object):
    """A helper class to interact with Azure ML endpoints locally.

    Use this helper to manage Azure ML endpoints locally, e.g. create,
    invoke, show, list, delete.
    """

    def __init__(
        self,
        operation_container: OperationsContainer,
    ):
        self._code_validator = CodeValidator()
        self._environment_validator = EnvironmentValidator()
        self._model_validator = ModelValidator()
        self._docker_client = DockerClient()
        self._model_operations = operation_container.all_operations.get(AzureMLResourceType.MODEL)
        self._code_operations = operation_container.all_operations.get(AzureMLResourceType.CODE)
        self._environment_operations = operation_container.all_operations.get(AzureMLResourceType.ENVIRONMENT)

    def create_or_update(
        self, deployment: OnlineDeployment, local_endpoint_mode: LocalEndpointMode
    ) -> OnlineDeployment:
        """Create or update an deployment locally using Docker.

        :param deployment: OnlineDeployment object with information from user yaml.
        :type deployment: OnlineDeployment
        :param local_endpoint_mode: Mode for how to create the local user container.
        :type local_endpoint_mode: LocalEndpointMode
        """
        if deployment is None:
            msg = "The entity provided for local endpoint was null. Please provide valid entity."
            raise InvalidLocalEndpointError(message=msg, no_personal_data_message=msg)

        endpoint_metadata = None
        try:
            self.get(endpoint_name=deployment.endpoint_name, deployment_name=deployment.name)
            endpoint_metadata = json.dumps(self._docker_client.get_endpoint(endpoint_name=deployment.endpoint_name))
            operation_message = "Updating local deployment"
        except LocalEndpointNotFoundError:
            operation_message = "Creating local deployment"

        deployment_metadata = json.dumps(deployment._to_dict())
        endpoint_metadata = (
            endpoint_metadata
            if endpoint_metadata
            else self._get_stubbed_endpoint_metadata(endpoint_name=deployment.endpoint_name)
        )
        local_endpoint_polling_wrapper(
            func=self._create_deployment,
            message=f"{operation_message} ({deployment.endpoint_name} / {deployment.name}) ",
            endpoint_name=deployment.endpoint_name,
            deployment=deployment,
            local_endpoint_mode=local_endpoint_mode,
            endpoint_metadata=endpoint_metadata,
            deployment_metadata=deployment_metadata,
        )
        return self.get(endpoint_name=deployment.endpoint_name, deployment_name=deployment.name)

    def get_deployment_logs(self, endpoint_name: str, deployment_name: str, lines: int) -> str:
        """Get logs from a local endpoint.

        :param endpoint_name: Name of endpoint to invoke.
        :type endpoint_name: str
        :param deployment_name: Name of specific deployment to invoke.
        :type deployment_name: str
        :param lines: Number of most recent lines from container logs.
        :type lines: int
        :return: str
        """
        return self._docker_client.logs(endpoint_name=endpoint_name, deployment_name=deployment_name, lines=lines)

    def get(self, endpoint_name: str, deployment_name: str) -> OnlineDeployment:
        """Get a local deployment.

        :param endpoint_name: Name of endpoint.
        :type endpoint_name: str
        :param deployment_name: Name of deployment.
        :type deployment_name: str
        :return OnlineDeployment:
        """
        container = self._docker_client.get_endpoint_container(
            endpoint_name=endpoint_name,
            deployment_name=deployment_name,
            include_stopped=True,
        )
        if container is None:
            raise LocalEndpointNotFoundError(endpoint_name=endpoint_name, deployment_name=deployment_name)
        return self._convert_container_to_deployment(container=container)

    def list(self) -> Iterable[OnlineDeployment]:
        """List all local endpoints."""
        containers = self._docker_client.list_containers()
        deployments = []
        for container in containers:
            deployments.append(self._convert_container_to_deployment(container=container))
        return deployments

    def delete(self, name: str, deployment_name: str = None):
        """Delete a local deployment.

        :param name: Name of endpoint associated with the deployment to delete.
        :type name: str
        :param deployment_name: Name of specific deployment to delete.
        :type deployment_name: str
        """
        self._docker_client.delete(endpoint_name=name, deployment_name=deployment_name)
        try:
            build_directory = self._get_deployment_directory(endpoint_name=name, deployment_name=deployment_name)
            shutil.rmtree(build_directory)
        except (PermissionError, OSError):
            pass

    def _create_deployment(
        self,
        endpoint_name: str,
        deployment: OnlineDeployment,
        local_endpoint_mode: LocalEndpointMode,
        endpoint_metadata: dict = None,
        deployment_metadata: dict = None,
    ):
        """Create deployment locally using Docker.

        :param endpoint: OnlineDeployment object with information from user yaml.
        :type endpoint: OnlineDeployment
        :param deployment: Deployment to create
        :type deployment: Deployment entity
        :param local_endpoint_mode: Mode for local endpoint.
        :type local_endpoint_mode: LocalEndpointMode
        :param endpoint_metadata: Endpoint metadata (json serialied Endpoint entity)
        :type endpoint_metadata: dict
        :param deployment_metadata: Deployment metadata (json serialied Deployment entity)
        :type deployment_metadata: dict
        """
        deployment_name = deployment.name
        deployment_directory = self._create_build_directory(
            endpoint_name=endpoint_name, deployment_name=deployment_name
        )
        deployment_directory_path = str(deployment_directory.resolve())

        # Get assets for mounting into the container
        # If code_directory_path is None, consider NCD flow
        code_directory_path = self._code_validator.get_code_configuration_artifacts(
            endpoint_name=endpoint_name,
            deployment=deployment,
            code_operations=self._code_operations,
            download_path=deployment_directory_path,
        )
        # We always require the model, however it may be anonymous for local (model_name=None)
        (model_name, model_version, model_directory_path,) = self._model_validator.get_model_artifacts(
            endpoint_name=endpoint_name,
            deployment=deployment,
            model_operations=self._model_operations,
            download_path=deployment_directory_path,
        )

        # Resolve the environment information
        # - Image + conda file - environment.image / environment.conda_file
        # - Docker context - environment.build
        (
            yaml_base_image_name,
            yaml_env_conda_file_path,
            yaml_env_conda_file_contents,
            downloaded_build_context,
            yaml_dockerfile,
            inference_config,
        ) = self._environment_validator.get_environment_artifacts(
            endpoint_name=endpoint_name,
            deployment=deployment,
            environment_operations=self._environment_operations,
            download_path=deployment_directory,
        )
        # Retrieve AzureML specific information
        # - environment variables required for deployment
        # - volumes to mount into container
        image_context = AzureMlImageContext(
            endpoint_name=endpoint_name,
            deployment_name=deployment_name,
            yaml_code_directory_path=code_directory_path,
            yaml_code_scoring_script_file_name=deployment.code_configuration.scoring_script
            if code_directory_path
            else None,
            model_directory_path=model_directory_path,
            model_mount_path=f"/{model_name}/{model_version}" if model_name else "",
        )

        # Construct Dockerfile if necessary, ie.
        # - User did not provide environment.inference_config, then this is not BYOC flow, cases below:
        # --- user provided environment.build
        # --- user provided environment.image
        # --- user provided environment.image + environment.conda_file
        is_byoc = inference_config is not None
        dockerfile = None
        if not is_byoc:
            install_debugpy = local_endpoint_mode is LocalEndpointMode.VSCodeDevContainer
            if yaml_env_conda_file_path:
                self._write_conda_file(
                    conda_contents=yaml_env_conda_file_contents,
                    directory_path=deployment_directory,
                    conda_file_name=LocalEndpointConstants.CONDA_FILE_NAME,
                )
                dockerfile = DockerfileResolver(
                    dockerfile=yaml_dockerfile,
                    docker_base_image=yaml_base_image_name,
                    docker_azureml_app_path=image_context.docker_azureml_app_path,
                    docker_conda_file_name=LocalEndpointConstants.CONDA_FILE_NAME,
                    docker_port=LocalEndpointConstants.DOCKER_PORT,
                    install_debugpy=install_debugpy,
                )
            else:
                dockerfile = DockerfileResolver(
                    dockerfile=yaml_dockerfile,
                    docker_base_image=yaml_base_image_name,
                    docker_azureml_app_path=image_context.docker_azureml_app_path,
                    docker_conda_file_name=None,
                    docker_port=LocalEndpointConstants.DOCKER_PORT,
                    install_debugpy=install_debugpy,
                )
            dockerfile.write_file(directory_path=deployment_directory_path)

        # Merge AzureML environment variables and user environment variables
        user_environment_variables = deployment.environment_variables
        environment_variables = {
            **image_context.environment,
            **user_environment_variables,
        }
        # Determine whether we need to use local context or downloaded context
        build_directory = downloaded_build_context if downloaded_build_context else deployment_directory
        self._docker_client.create_deployment(
            endpoint_name=endpoint_name,
            deployment_name=deployment_name,
            endpoint_metadata=endpoint_metadata,
            deployment_metadata=deployment_metadata,
            build_directory=str(build_directory),
            dockerfile_path=None if is_byoc else dockerfile.local_path,
            conda_source_path=yaml_env_conda_file_path,
            conda_yaml_contents=yaml_env_conda_file_contents,
            volumes=image_context.volumes,
            environment=environment_variables,
            azureml_port=inference_config.scoring_route.port if is_byoc else LocalEndpointConstants.DOCKER_PORT,
            local_endpoint_mode=local_endpoint_mode,
            prebuilt_image_name=yaml_base_image_name if is_byoc else None,
        )

    def _write_conda_file(self, conda_contents: str, directory_path: str, conda_file_name: str):
        """Writes out conda file to provided directory.

        :param conda_contents: contents of conda yaml file provided by user
        :type conda_contents: str
        :param directory_path: directory on user's local system to write conda file
        :type directory_path: str
        """
        conda_file_path = f"{directory_path}/{conda_file_name}"
        p = Path(conda_file_path)
        p.write_text(conda_contents)

    def _convert_container_to_deployment(self, container: Container) -> OnlineDeployment:
        """Converts provided Container for local deployment to OnlineDeployment
        entity.

        :param container: Container for a local deployment.
        :type container: docker.models.containers.Container
        :returns OnlineDeployment entity:
        """
        deployment_json = self._docker_client.get_deployment_json_from_container(container=container)
        provisioning_state = self._docker_client.get_status_from_container(container=container)
        if provisioning_state == LocalEndpointConstants.CONTAINER_EXITED:
            return self._convert_json_to_deployment(
                deployment_json=deployment_json,
                instance_type=LocalEndpointConstants.ENDPOINT_STATE_LOCATION,
                provisioning_state=LocalEndpointConstants.ENDPOINT_STATE_FAILED,
            )
        else:
            return self._convert_json_to_deployment(
                deployment_json=deployment_json,
                instance_type=LocalEndpointConstants.ENDPOINT_STATE_LOCATION,
                provisioning_state=LocalEndpointConstants.ENDPOINT_STATE_SUCCEEDED,
            )

    def _convert_json_to_deployment(self, deployment_json: dict, **kwargs) -> OnlineDeployment:
        """Converts metadata json and kwargs to OnlineDeployment entity.

        :param deployment_json: dictionary representation of OnlineDeployment entity.
        :type deployment_json: dict
        :returns OnlineDeployment entity:
        """
        params_override = []
        for k, v in kwargs.items():
            params_override.append({k: v})
        return OnlineDeployment._load(data=deployment_json, params_override=params_override)

    def _get_stubbed_endpoint_metadata(self, endpoint_name: str) -> dict:
        return json.dumps({"name": endpoint_name})

    def _create_build_directory(self, endpoint_name: str, deployment_name: str) -> Path:
        build_directory = self._get_deployment_directory(endpoint_name=endpoint_name, deployment_name=deployment_name)
        build_directory.mkdir(parents=True, exist_ok=True)
        return build_directory

    def _get_deployment_directory(self, endpoint_name: str, deployment_name: str) -> Path:
        return Path(Path.home(), ".azureml", "inferencing", endpoint_name, deployment_name)
