# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=missing-client-constructor-parameter-credential,missing-client-constructor-parameter-kwargs
# pylint: disable=client-accepts-api-version-keyword

import json
import logging
import time
from typing import Optional

from azure.ai.ml._local_endpoints.local_endpoint_mode import LocalEndpointMode
from azure.ai.ml._local_endpoints.vscode_debug.vscode_client import VSCodeClient
from azure.ai.ml._utils._logger_utils import initialize_logger_info
from azure.ai.ml._utils.utils import DockerProxy
from azure.ai.ml.constants._endpoint import LocalEndpointConstants
from azure.ai.ml.exceptions import (
    DockerEngineNotAvailableError,
    InvalidLocalEndpointError,
    LocalEndpointImageBuildError,
    LocalEndpointInFailedStateError,
    LocalEndpointNotFoundError,
    MultipleLocalDeploymentsFoundError,
)

docker = DockerProxy()
module_logger = logging.getLogger(__name__)
initialize_logger_info(module_logger, terminator="")

DEFAULT_LABELS = {
    LocalEndpointConstants.LABEL_KEY_AZUREML_LOCAL_ENDPOINT: "",
    LocalEndpointConstants.LABEL_KEY_ENDPOINT_NAME: "",
    LocalEndpointConstants.LABEL_KEY_DEPLOYMENT_NAME: "",
    LocalEndpointConstants.LABEL_KEY_ENDPOINT_JSON: "",
    LocalEndpointConstants.LABEL_KEY_DEPLOYMENT_JSON: "",
    LocalEndpointConstants.LABEL_KEY_AZUREML_PORT: "",
}


class DockerClient(object):
    """Client for interacting with User's Docker environment for local
    endpoints."""

    # pylint: disable=client-method-missing-type-annotations

    def __init__(
        self,
        client: Optional["docker.DockerClient"] = None,
        vscode_client: Optional[VSCodeClient] = None,
    ):
        self._lazy_client = client
        self._vscode_client = vscode_client if vscode_client else VSCodeClient()

    @property
    def _client(self) -> "docker.DockerClient":
        """Lazy initializer for docker-py client.

        :return: docker.client.DockerClient
        :raises: azure.ai.ml._local_endpoints.errors.DockerEngineNotAvailableError
        """
        if self._lazy_client is None:
            try:
                self._lazy_client = docker.from_env()
            except docker.errors.DockerException as e:
                if "Error while fetching server API version" in str(e):
                    raise DockerEngineNotAvailableError()
                raise
        return self._lazy_client

    def create_endpoint(
        self,
        endpoint_name: str,
        endpoint_metadata: str,
        build_directory: str,
        image_name: str,
        dockerfile_path: str,
    ) -> None:
        try:
            self._client.images.build(path=build_directory, tag=image_name, dockerfile=dockerfile_path)
        except docker.errors.BuildError:
            pass
        self.delete(endpoint_name=endpoint_name, verify_exists=False)

        labels = DEFAULT_LABELS.copy()
        labels[LocalEndpointConstants.LABEL_KEY_ENDPOINT_NAME] = endpoint_name
        labels[LocalEndpointConstants.LABEL_KEY_ENDPOINT_JSON] = endpoint_metadata
        container_name = _get_container_name(endpoint_name)
        self._client.containers.run(
            image_name,
            name=container_name,
            labels=labels,
            detach=True,
            tty=True,
            publish_all_ports=True,
        )

    # pylint: disable=client-method-has-more-than-5-positional-arguments

    def create_deployment(
        self,
        endpoint_name: str,
        deployment_name: str,
        endpoint_metadata: str,
        deployment_metadata: str,
        build_directory: str,
        dockerfile_path: str,
        conda_source_path: str,
        conda_yaml_contents: str,
        volumes: dict,
        environment: dict,
        azureml_port: int,
        local_endpoint_mode: LocalEndpointMode,
        prebuilt_image_name: Optional[str] = None,
    ) -> None:
        """Builds and runs an image from provided image context.

        :param endpoint_name: name of local endpoint
        :type endpoint_name: str
        :param deployment_name: name of local deployment
        :type deployment_name: str
        :param endpoint_metadata: Endpoint entity information serialized.
        :type endpoint_metadata: str
        :param deployment_metadata: Deployment entity information serialized.
        :type deployment_metadata: str
        :param build_directory: directory on user's local system to write conda file
        :type build_directory: str
        :param dockerfile_path: directory on user's local system to write Dockerfile
        :type dockerfile_path: str
        :param conda_source_path: source of conda file (either path on user's local machine or environment ID)
        :type conda_source_path: str
        :param conda_yaml_contents: contents of user's conda file for docker build
        :type conda_yaml_contents: str
        :param volumes: dictionary of volumes to mount to docker container
        :type volumes: dict
        :param environment: dictionary of docker environment variables to set in container
        :type environment: dict
        :param azureml_port: Port exposed in Docker image for AzureML service.
        :type azureml_port: int
        :param local_endpoint_mode: Mode for how to create the local user container.
        :type local_endpoint_mode: LocalEndpointMode
        :param prebuilt_image_name: Name of pre-built image from customer if using BYOC flow.
        :type prebuilt_image_name: str
        """
        # Prepare image
        if prebuilt_image_name is None:
            image_name = _get_image_name(endpoint_name, deployment_name)
            module_logger.debug("Building local image '%s'\n", image_name)
            module_logger.debug("Build directory: '%s'\n", build_directory)
            module_logger.debug("Dockerfile path: '%s'\n", dockerfile_path)
            module_logger.debug("Image '%s' is built.", image_name)
            self._build_image(
                build_directory=build_directory,
                image_name=image_name,
                dockerfile_path=dockerfile_path,
                conda_source_path=conda_source_path,
                conda_yaml_contents=conda_yaml_contents,
            )
        else:
            image_name = prebuilt_image_name
            try:
                self._client.images.get(image_name)
            except docker.errors.ImageNotFound:
                module_logger.info("\nDid not find image '%s' locally. Pulling from registry.\n", image_name)
                try:
                    self._client.images.pull(image_name)
                except docker.errors.NotFound:
                    raise InvalidLocalEndpointError(
                        message=(
                            f"Could not find image '{image_name}' locally or in registry. "
                            "Please check your image name."
                        ),
                        no_personal_data_message=(
                            "Could not find image locally or in registry. Please check your image name."
                        ),
                    )

        module_logger.info("\nStarting up endpoint")
        # Delete container if exists
        self.delete(endpoint_name=endpoint_name, verify_exists=False)

        labels = get_container_labels(
            endpoint_name=endpoint_name,
            deployment_name=deployment_name,
            endpoint_metadata=endpoint_metadata,
            deployment_metadata=deployment_metadata,
            azureml_port=azureml_port,
        )
        module_logger.debug("Setting labels: '%s'\n", labels)
        module_logger.debug("Mounting volumes: '%s'\n", volumes)
        module_logger.debug("Setting environment variables: '%s'\n", environment)
        container_name = _get_container_name(endpoint_name, deployment_name)
        container = self._client.containers.create(
            image_name,
            name=container_name,
            labels=labels,
            volumes=self._reformat_volumes(volumes),
            environment=environment,
            detach=True,
            tty=True,
            publish_all_ports=True,
        )
        if local_endpoint_mode == LocalEndpointMode.VSCodeDevContainer:
            try:
                devcontainer_path = self._vscode_client.create_dev_container_json(
                    azureml_container=container,
                    endpoint_name=endpoint_name,
                    deployment_name=deployment_name,
                    build_directory=build_directory,
                    image_name=image_name,
                    environment=environment,
                    volumes=volumes,
                    labels=labels,
                )
            finally:
                # This pre-created container is only used for retrieving the entry script
                # to add debugpy statements
                container.remove()
            app_path = environment[LocalEndpointConstants.ENVVAR_KEY_AML_APP_ROOT]
            self._vscode_client.invoke_dev_container(
                devcontainer_path=devcontainer_path, app_path=app_path
            )  # pylint: disable=redundant-keyword-arg
            time.sleep(LocalEndpointConstants.DEFAULT_STARTUP_WAIT_TIME_SECONDS)
        else:
            container.start()
            time.sleep(LocalEndpointConstants.DEFAULT_STARTUP_WAIT_TIME_SECONDS)
            container.reload()
            _validate_container_state(
                endpoint_name=endpoint_name,
                deployment_name=deployment_name,
                container=container,
            )
            scoring_uri = self.get_scoring_uri(endpoint_name=endpoint_name, deployment_name=deployment_name)
            module_logger.debug("Container '%s' is up and running at '%s'\n", container_name, scoring_uri)

    def delete(
        self,
        endpoint_name: str,
        deployment_name: Optional[str] = None,
        verify_exists: bool = True,
    ) -> None:
        """Deletes local endpoint / deployment.

        :param endpoint_name: name of local endpoint
        :type endpoint_name: str
        :param deployment_name: name of local deployment
        :type deployment_name: (str, optional)
        :param verify_exists: Verify that the endpoint exists on deletion. Default: True
        :type verify_exists: (bool, optional)
        :raises: azure.ai.ml._local_endpoints.errors.LocalEndpointNotFoundError
        """
        containers = self.list_containers(endpoint_name=endpoint_name, deployment_name=deployment_name)
        if verify_exists and len(containers) == 0:
            raise LocalEndpointNotFoundError(endpoint_name=endpoint_name, deployment_name=deployment_name)

        for container in containers:
            container.stop()
            container.remove()
            module_logger.debug("Endpoint container '%s' is removed.", container.name)

    def get_endpoint(self, endpoint_name: str) -> dict:
        """Returns metadata for local endpoint or deployment.

        :param endpoint_name: name of local endpoint
        :type endpoint_name: str
        :returns dict: JSON dict representing user provided endpoint input
        """
        container = self.get_endpoint_container(endpoint_name=endpoint_name)
        if container is None:
            raise LocalEndpointNotFoundError(endpoint_name=endpoint_name)
        return get_endpoint_json_from_container(container=container)

    def get_deployment(self, endpoint_name: str, deployment_name: Optional[str] = None) -> dict:
        """Returns metadata for local deployment.

        :param endpoint_name: name of local endpoint
        :type endpoint_name: str
        :param deployment_name: name of local deployment
        :type deployment_name: (str, optional)
        :returns dict: JSON dict representing user provided endpoint input
        """
        container = self.get_endpoint_container(endpoint_name=endpoint_name, deployment_name=deployment_name)
        if container is None:
            raise LocalEndpointNotFoundError(endpoint_name=endpoint_name, deployment_name=deployment_name)
        return get_deployment_json_from_container(container=container)

    def get_scoring_uri(self, endpoint_name: str, deployment_name: Optional[str] = None) -> str:
        """Returns scoring uri for local endpoint or deployment.

        :param endpoint_name: name of local endpoint
        :type endpoint_name: str
        :param deployment_name: name of local deployment
        :type deployment_name: (str, optional)
        :raises: azure.ai.ml._local_endpoints.errors.LocalEndpointNotFoundError
        :raises: azure.ai.ml._local_endpoints.errors.MultipleLocalDeploymentsFoundError
        """
        container = self.get_endpoint_container(
            endpoint_name=endpoint_name,
            deployment_name=deployment_name,
            verify_single_deployment=True,
        )
        if container is None:
            return
        _validate_container_state(
            endpoint_name=endpoint_name,
            deployment_name=deployment_name,
            container=container,
        )
        return get_scoring_uri_from_container(container=container)

    def logs(self, endpoint_name: str, deployment_name: str, lines: int) -> str:
        """Returns logs from local deployment.

        :param endpoint_name: name of local endpoint
        :type endpoint_name: str
        :param deployment_name: name of local deployment
        :type deployment_name: str
        :param lines: number of lines to retrieve from container logs
        :type lines: int
        :return: str
        :raises: azure.ai.ml._local_endpoints.errors.LocalEndpointNotFoundError
        """
        container = self.get_endpoint_container(endpoint_name, deployment_name=deployment_name)
        if container is None:
            raise LocalEndpointNotFoundError(endpoint_name=endpoint_name, deployment_name=deployment_name)
        return container.logs(tail=int(lines)).decode()

    def list_containers(
        self,
        endpoint_name: Optional[str] = None,
        deployment_name: Optional[str] = None,
        include_stopped: bool = True,
    ) -> list:
        """Returns a list of local endpoints.

        :param endpoint_name: Name of local endpoint. If none, all local endpoints will be returned.
        :type endpoint_name: (str, optional)
        :param deployment_name: Name of local deployment. If none, all deployments under endpoint will be returned.
        :type deployment_name: (str, optional)
        :param include_stopped: Include stopped containers. Default: True.
        :type include_stopped: (str, optional)
        :returns list[Container]: array of Container objects from docker-py library
        """
        filters = {"label": [f"{LocalEndpointConstants.LABEL_KEY_AZUREML_LOCAL_ENDPOINT}"]}
        if endpoint_name:
            filters["label"].append(f"{LocalEndpointConstants.LABEL_KEY_ENDPOINT_NAME}={endpoint_name}")
        if deployment_name:
            filters["label"].append(f"{LocalEndpointConstants.LABEL_KEY_DEPLOYMENT_NAME}={deployment_name}")

        return self._client.containers.list(filters=filters, all=include_stopped)

    def get_endpoint_container(
        self,
        endpoint_name: str,
        deployment_name: Optional[str] = None,
        verify_single_deployment: bool = False,
        include_stopped: bool = True,
    ) -> "docker.models.containers.Container":
        """Builds and runs an image from provided image context.

        :param endpoint_name: name of local endpoint
        :type endpoint_name: str
        :param deployment_name: name of local deployment
        :type deployment_name: (str, optional)
        :param verify_single_deployment: Fail if more than one deployment container exists
        :type verify_single_deployment: (bool, optional)
        :param include_stopped: Include container even if it's stopped. Default: True.
        :type include_stopped: (bool, optional)
        :returns docker.models.containers.Container:
        """
        containers = self.list_containers(
            endpoint_name=endpoint_name,
            deployment_name=deployment_name,
            include_stopped=include_stopped,
        )
        if len(containers) == 0:
            return
        if len(containers) > 1 and verify_single_deployment:
            raise MultipleLocalDeploymentsFoundError(endpoint_name=endpoint_name)
        return containers[0]

    def _build_image(
        self,
        build_directory: str,
        image_name: str,
        dockerfile_path: str,
        conda_source_path: str,  # pylint: disable=unused-argument
        conda_yaml_contents: str,  # pylint: disable=unused-argument
    ) -> None:
        try:
            module_logger.info("\nBuilding Docker image from Dockerfile")
            first_line = True
            for status in self._client.api.build(
                path=build_directory,
                tag=image_name,
                dockerfile=dockerfile_path,
                pull=True,
                decode=True,
                quiet=False,
            ):
                if first_line:
                    module_logger.info("\n")
                    first_line = False
                if "stream" in status:
                    if "An unexpected error has occurred. Conda has prepared the above report." in status["stream"]:
                        raise LocalEndpointImageBuildError(status["stream"])
                    module_logger.info(status["stream"])

                if "error" in status:
                    module_logger.info(status["error"])
                    raise LocalEndpointImageBuildError(status["error"])
        except docker.errors.APIError as e:
            raise LocalEndpointImageBuildError(e)
        except Exception as e:
            if isinstance(e, LocalEndpointImageBuildError):
                raise
            raise LocalEndpointImageBuildError(e)

    def _reformat_volumes(self, volumes_dict: dict) -> list:  # pylint: disable=no-self-use
        """Returns a list of volumes to pass to docker.

        :param volumes_dict: custom formatted dict of volumes to mount. We expect the keys to be unique.
        Example: {
            "codesrc:codedest": {
                "codesrc": {
                    "bind": "codedest"
                }
            },
            "modelsrc:modeldest": {
                "modelsrc": {
                    "bind": "modeldest"
                }
            }
        }
        :type volumes_dict: str
        :return list: list of volumes to pass to docker. Example: ["codesrc:codedest", "modelsrc:modeldest"]
        """
        return list(volumes_dict.keys())


def get_container_labels(
    endpoint_name: str,
    deployment_name: str,
    endpoint_metadata: dict,
    deployment_metadata: dict,
    azureml_port: int,
) -> dict:
    labels = DEFAULT_LABELS.copy()
    labels[LocalEndpointConstants.LABEL_KEY_ENDPOINT_NAME] = endpoint_name
    labels[LocalEndpointConstants.LABEL_KEY_DEPLOYMENT_NAME] = deployment_name
    labels[LocalEndpointConstants.LABEL_KEY_ENDPOINT_JSON] = endpoint_metadata
    labels[LocalEndpointConstants.LABEL_KEY_DEPLOYMENT_JSON] = deployment_metadata
    labels[LocalEndpointConstants.LABEL_KEY_AZUREML_PORT] = str(azureml_port)
    return labels


def get_endpoint_json_from_container(container: "docker.models.containers.Container") -> dict:
    if container:
        data = container.labels[LocalEndpointConstants.LABEL_KEY_ENDPOINT_JSON]
        return json.loads(data)
    return


def get_deployment_json_from_container(container: "docker.models.containers.Container") -> dict:
    if container:
        data = container.labels[LocalEndpointConstants.LABEL_KEY_DEPLOYMENT_JSON]
        return json.loads(data)
    return


def get_status_from_container(container: "docker.models.containers.Container") -> str:
    """Returns status of container.

    :param container: container of local Deployment
    :type container: docker.models.containers.Container
    :return str: container status
    """
    return container.status


def get_scoring_uri_from_container(container: "docker.models.containers.Container") -> str:
    """Returns scoring_uri of container.

    :param container: container of local Deployment
    :type container: docker.models.containers.Container
    :return str: container scoring_uri
    """
    port = 5001
    # Example container.ports: {'5001/tcp': [{'HostIp': '0.0.0.0', 'HostPort': '5001'}],
    # '8883/tcp': None, '8888/tcp': None }
    if container is not None and container.ports is not None:
        azureml_port = container.labels["azureml-port"]
        for docker_port, host_addresses in container.ports.items():
            if azureml_port in docker_port and host_addresses is not None:
                for address in host_addresses:
                    if "HostPort" in address:
                        port = address["HostPort"]
                        break
    # TODO: resolve scoring path correctly
    return f"http://localhost:{port}/score"


def _get_image_name(endpoint_name: str, deployment_name: str) -> str:
    """Returns an image name.

    :param endpoint_name: name of local endpoint
    :type endpoint_name: str
    :param deployment_name: name of local deployment
    :type deployment_name: str
    :return str: image name
    """
    return f"{endpoint_name}:{deployment_name}"


def _get_container_name(endpoint_name: str, deployment_name: Optional[str] = None) -> str:
    """Returns a container name.

    :param endpoint_name: name of local endpoint
    :type endpoint_name: str
    :param deployment_name: name of local deployment
    :type deployment_name: str
    :return str: container name
    """
    return f"{endpoint_name}.{deployment_name}" if deployment_name else endpoint_name


def _validate_container_state(
    endpoint_name: str,
    deployment_name: str,
    container: "docker.models.containers.Container",
):
    """Returns a container name.

    :param endpoint_name: name of local endpoint
    :type endpoint_name: str
    :param deployment_name: name of local deployment
    :type deployment_name: str
    :param container: container of local Deployment
    :type container: docker.models.containers.Container
    :raises: azure.ai.ml._local_endpoints.errors.LocalEndpointInFailedStateError
    """
    status = get_status_from_container(container=container)
    if LocalEndpointConstants.CONTAINER_EXITED == status:
        raise LocalEndpointInFailedStateError(endpoint_name=endpoint_name, deployment_name=deployment_name)
