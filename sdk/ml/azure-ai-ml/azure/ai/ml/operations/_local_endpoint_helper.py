# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import json
import logging
from typing import Any, Iterable, List, Optional

from marshmallow.exceptions import ValidationError as SchemaValidationError

from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._local_endpoints import EndpointStub
from azure.ai.ml._local_endpoints.docker_client import (
    DockerClient,
    get_endpoint_json_from_container,
    get_scoring_uri_from_container,
    get_status_from_container,
)
from azure.ai.ml._utils._endpoint_utils import local_endpoint_polling_wrapper
from azure.ai.ml._utils._http_utils import HttpPipeline
from azure.ai.ml._utils.utils import DockerProxy
from azure.ai.ml.constants._endpoint import EndpointInvokeFields, LocalEndpointConstants
from azure.ai.ml.entities import OnlineEndpoint
from azure.ai.ml.exceptions import InvalidLocalEndpointError, LocalEndpointNotFoundError, ValidationException

docker = DockerProxy()
module_logger = logging.getLogger(__name__)


class _LocalEndpointHelper(object):
    """A helper class to interact with Azure ML endpoints locally.

    Use this helper to manage Azure ML endpoints locally, e.g. create, invoke, show, list, delete.
    """

    def __init__(self, *, requests_pipeline: HttpPipeline):
        self._docker_client = DockerClient()
        self._endpoint_stub = EndpointStub()
        self._requests_pipeline = requests_pipeline

    def create_or_update(self, endpoint: OnlineEndpoint) -> OnlineEndpoint:  # type: ignore
        """Create or update an endpoint locally using Docker.

        :param endpoint: OnlineEndpoint object with information from user yaml.
        :type endpoint: OnlineEndpoint
        """
        try:
            if endpoint is None:
                msg = "The entity provided for local endpoint was null. Please provide valid entity."
                raise InvalidLocalEndpointError(message=msg, no_personal_data_message=msg)

            try:
                self.get(endpoint_name=str(endpoint.name))
                operation_message = "Updating local endpoint"
            except LocalEndpointNotFoundError:
                operation_message = "Creating local endpoint"

            local_endpoint_polling_wrapper(
                func=self._endpoint_stub.create_or_update,
                message=f"{operation_message} ({endpoint.name}) ",
                endpoint=endpoint,
            )
            return self.get(endpoint_name=str(endpoint.name))
        except Exception as ex:  # pylint: disable=W0718
            if isinstance(ex, (ValidationException, SchemaValidationError)):
                log_and_raise_error(ex)
            else:
                raise ex

    def invoke(self, endpoint_name: str, data: dict, deployment_name: Optional[str] = None) -> str:
        """Invoke a local endpoint.

        :param endpoint_name: Name of endpoint to invoke.
        :type endpoint_name: str
        :param data: json data to pass
        :type data: dict
        :param deployment_name: Name of specific deployment to invoke.
        :type deployment_name: (str, optional)
        :return: The text response
        :rtype: str
        """
        # get_scoring_uri will throw user error if there are multiple deployments and no deployment_name is specified
        scoring_uri = self._docker_client.get_scoring_uri(endpoint_name=endpoint_name, deployment_name=deployment_name)
        if scoring_uri:
            headers = {}
            if deployment_name is not None:
                headers[EndpointInvokeFields.MODEL_DEPLOYMENT] = deployment_name
            return str(self._requests_pipeline.post(scoring_uri, json=data, headers=headers).text())
        endpoint_stub = self._endpoint_stub.get(endpoint_name=endpoint_name)
        if endpoint_stub:
            return str(self._endpoint_stub.invoke())
        raise LocalEndpointNotFoundError(endpoint_name=endpoint_name, deployment_name=deployment_name)

    def get(self, endpoint_name: str) -> OnlineEndpoint:
        """Get a local endpoint.

        :param endpoint_name: Name of endpoint.
        :type endpoint_name: str
        :return OnlineEndpoint:
        """
        endpoint = self._endpoint_stub.get(endpoint_name=endpoint_name)
        container = self._docker_client.get_endpoint_container(endpoint_name=endpoint_name, include_stopped=True)
        if endpoint:
            if container:
                return _convert_container_to_endpoint(container=container, endpoint_json=endpoint.dump())
            return endpoint
        if container:
            return _convert_container_to_endpoint(container=container)
        raise LocalEndpointNotFoundError(endpoint_name=endpoint_name)

    def list(self) -> Iterable[OnlineEndpoint]:
        """List all local endpoints.

        :return: An iterable of local endpoints
        :rtype: Iterable[OnlineEndpoint]
        """
        endpoints: List = []
        containers = self._docker_client.list_containers()
        endpoint_stubs = self._endpoint_stub.list()
        # Iterate through all cached endpoint files
        for endpoint_file in endpoint_stubs:
            endpoint_json = json.loads(endpoint_file.read_text())
            container = self._docker_client.get_endpoint_container(
                endpoint_name=endpoint_json.get("name"), include_stopped=True
            )
            # If a deployment is associated with endpoint,
            # override certain endpoint properties with deployment information and remove it from containers list.
            # Otherwise, return endpoint spec.
            if container:
                endpoints.append(_convert_container_to_endpoint(endpoint_json=endpoint_json, container=container))
                containers.remove(container)
            else:
                endpoints.append(
                    OnlineEndpoint._load(
                        data=endpoint_json,
                        params_override=[{"location": LocalEndpointConstants.ENDPOINT_STATE_LOCATION}],
                    )
                )
        # Iterate through any deployments that don't have an explicit local endpoint stub.
        for container in containers:
            endpoints.append(_convert_container_to_endpoint(container=container))
        return endpoints

    def delete(self, name: str) -> None:
        """Delete a local endpoint.

        :param name: Name of endpoint to delete.
        :type name: str
        """
        endpoint_stub = self._endpoint_stub.get(endpoint_name=name)
        if endpoint_stub:
            self._endpoint_stub.delete(endpoint_name=name)
            endpoint_container = self._docker_client.get_endpoint_container(endpoint_name=name)
            if endpoint_container:
                self._docker_client.delete(endpoint_name=name)
        else:
            raise LocalEndpointNotFoundError(endpoint_name=name)


def _convert_container_to_endpoint(
    # Bug Item number: 2885719
    container: "docker.models.containers.Container",  # type: ignore
    endpoint_json: Optional[dict] = None,
) -> OnlineEndpoint:
    """Converts provided Container for local deployment to OnlineEndpoint entity.

    :param container: Container for a local deployment.
    :type container: docker.models.containers.Container
    :param endpoint_json: The endpoint json
    :type endpoint_json: Optional[dict]
    :return: The OnlineEndpoint entity
    :rtype: OnlineEndpoint
    """
    if endpoint_json is None:
        endpoint_json = get_endpoint_json_from_container(container=container)
    provisioning_state = get_status_from_container(container=container)
    if provisioning_state == LocalEndpointConstants.CONTAINER_EXITED:
        return _convert_json_to_endpoint(
            endpoint_json=endpoint_json,
            location=LocalEndpointConstants.ENDPOINT_STATE_LOCATION,
            provisioning_state=LocalEndpointConstants.ENDPOINT_STATE_FAILED,
        )
    scoring_uri = get_scoring_uri_from_container(container=container)
    return _convert_json_to_endpoint(
        endpoint_json=endpoint_json,
        location=LocalEndpointConstants.ENDPOINT_STATE_LOCATION,
        provisioning_state=LocalEndpointConstants.ENDPOINT_STATE_SUCCEEDED,
        scoring_uri=scoring_uri,
    )


def _convert_json_to_endpoint(endpoint_json: Optional[dict], **kwargs: Any) -> OnlineEndpoint:
    """Converts metadata json and kwargs to OnlineEndpoint entity.

    :param endpoint_json: dictionary representation of OnlineEndpoint entity.
    :type endpoint_json: dict
    :return: The OnlineEndpoint entity
    :rtype: OnlineEndpoint
    """
    params_override = []
    for k, v in kwargs.items():
        params_override.append({k: v})
    return OnlineEndpoint._load(data=endpoint_json, params_override=params_override)  # type: ignore
