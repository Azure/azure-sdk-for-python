# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: disable=protected-access
from typing import Any, Callable, cast, TypeVar, Union

from azure.core import PipelineClient
from azure.core.pipeline import PipelineResponse
from azure.core.polling.base_polling import LROBasePolling, OperationFailed, OperationResourcePolling
from azure.core.rest import AsyncHttpResponse, HttpResponse, HttpRequest

from ..models import SecurityDomain, SecurityDomainOperationStatus
from .._utils.model_base import _deserialize


PollingReturnType_co = TypeVar("PollingReturnType_co", covariant=True)

# Correct success response should be "Succeeded", but this has already shipped. Still, handle "Succeeded" just in case.
_FINISHED = frozenset(["succeeded", "success", "canceled", "failed"])


def _finished(status):
    if hasattr(status, "value"):
        status = status.value
    return str(status).lower() in _FINISHED


def _is_empty(response: Union[HttpResponse, AsyncHttpResponse]) -> bool:
    """Check if response body contains meaningful content.

    :param response: The response object.
    :type response: any
    :return: True if response body is empty, False otherwise.
    :rtype: bool
    """
    return not bool(response.content)


class PollingTerminationMixin(LROBasePolling):
    """Mixin to correctly handle polling termination.

    Uses a custom implementation of `finished` because Security Domain LROs return "Success" as a terminal response
    instead of the standard "Succeeded". At the time of writing, there's no way to more easily patch the base poller
    from `azure-core` to handle this.
    """

    def finished(self) -> bool:
        """Is this polling finished?

        :rtype: bool
        :return: True if finished, False otherwise.
        """
        return _finished(self.status())

    def parse_resource(
        self,
        pipeline_response: PipelineResponse[HttpRequest, HttpResponse],
    ) -> Union[SecurityDomain, SecurityDomainOperationStatus]:
        """Assuming this response is a resource, use the deserialization callback to parse it.
        If body is empty, assuming no resource to return.

        :param pipeline_response: The response object.
        :type pipeline_response: ~azure.core.pipeline.PipelineResponse
        :return: The parsed resource.
        :rtype: any
        """
        response = pipeline_response.http_response
        if not _is_empty(response):
            return self._deserialization_callback(pipeline_response)

        # This "type ignore" has been discussed with architects.
        # We have a typing problem that if the Swagger/TSP describes a return type (PollingReturnType_co is not None),
        # BUT the returned payload is actually empty, we don't want to fail, but return None.
        # To be clean, we would have to make the polling return type Optional "just in case the Swagger/TSP is wrong".
        # This is reducing the quality and the value of the typing annotations
        # for a case that is not supposed to happen in the first place. So we decided to ignore the type error here.
        return None  # type: ignore


class NoPollingMixin(LROBasePolling):
    """Mixin that intentionally bypasses any polling by immediately returning a success status.

    The Azure CLI accepts a `--no-wait` parameter in download and upload operations, allowing users to immediately get
    the result before HSM activation completes. This polling logic is used to support that behavior.
    """

    def finished(self) -> bool:
        """Is this polling finished?

        :rtype: bool
        :return: Whether this polling is finished
        """
        return True

    def status(self) -> str:
        """Return the current status.

        :rtype: str
        :return: The current status
        """
        return "succeeded"

    def result(self, *args, **kwargs):  # pylint: disable=unused-argument
        return self.resource()


class SecurityDomainDownloadPolling(OperationResourcePolling):
    """Adapts to the non-standard response pattern for security domain download."""

    def __init__(self) -> None:
        self._polling_url = ""
        super().__init__(operation_location_header="azure-asyncoperation")

    def get_polling_url(self) -> str:
        return self._polling_url

    def get_final_get_url(self, pipeline_response: "PipelineResponse") -> None:
        """Returns None instead of a URL because the final result includes a status monitor but no resource URL.

        :param pipeline_response: The response object. Unused here.
        :type pipeline_response: ~azure.core.pipeline.PipelineResponse

        :rtype: None
        :return: None
        """
        return None

    def set_initial_status(self, pipeline_response: "PipelineResponse") -> str:
        """Manually marks the operation as "InProgress".

        This is necessary because the initial response includes the security domain object -- which would usually be the
        result fetched from a final resource URL -- but no status monitor.

        :param pipeline_response: The response object.
        :type pipeline_response: ~azure.core.pipeline.PipelineResponse

        :rtype: str
        :return: The initial status, which is always "InProgress".
        """
        response: HttpResponse = pipeline_response.http_response
        self._polling_url = response.headers["azure-asyncoperation"]

        if response.status_code in {200, 201, 202, 204}:
            # The initial download response doesn't contain the status, so we consider it as "InProgress"
            # The next status update request will point to the download status endpoint and correctly update
            return "InProgress"
        raise OperationFailed("Operation failed or canceled")


class SecurityDomainDownloadPollingMethod(PollingTerminationMixin, LROBasePolling):
    """Polling method for the unique pattern of security domain download operations."""

    def initialize(
        self,
        client: PipelineClient[Any, Any],
        initial_response: PipelineResponse[HttpRequest, HttpResponse],
        deserialization_callback: Callable[
            [PipelineResponse[HttpRequest, HttpResponse]],
            PollingReturnType_co,
        ],
    ) -> None:
        """Set the initial status of this LRO.

        :param client: The Azure Core Pipeline client used to make request.
        :type client: ~azure.core.pipeline.PipelineClient
        :param initial_response: The initial response for the call.
        :type initial_response: ~azure.core.pipeline.PipelineResponse
        :param deserialization_callback: A callback function to deserialize the final response.
        :type deserialization_callback: callable
        :raises: HttpResponseError if initial status is incorrect LRO state
        """

        def get_long_running_output(pipeline_response):
            response = pipeline_response.http_response
            return _deserialize(SecurityDomain, response.json())

        super().initialize(client, initial_response, get_long_running_output)

    def resource(self) -> SecurityDomain:
        """Return the security domain deserialized from the initial response.

        This returns the final result of the `SecurityDomainClient.begin_download` operation by deserializing the
        initial response. This is an unusual LRO pattern and requires custom support. Usually, the object returned from
        an LRO is only returned as part of the terminal status response; in Security Domain, the download operation
        instead immediately returns the security domain object, and the terminal response only includes the activation
        status.

        :rtype: ~azure.keyvault.securitydomain.SecurityDomain
        :return: The security domain object.
        """
        # The final response should actually be the security domain object that was returned in the initial response
        return cast(SecurityDomain, self.parse_resource(self._initial_response))


class SecurityDomainDownloadNoPolling(SecurityDomainDownloadPollingMethod, NoPollingMixin):
    """Polling method for security domain download operations that bypass polling."""


class SecurityDomainUploadPolling(SecurityDomainDownloadPolling):
    """Polling logic for security domain upload operations.

    This class inherits from `SecurityDomainDownloadPolling` but uses the actual initial response status since the
    upload operation has a more typical LRO resource pattern.
    """

    def set_initial_status(self, pipeline_response: PipelineResponse) -> str:
        response: HttpResponse = pipeline_response.http_response
        self._polling_url = response.headers["azure-asyncoperation"]

        if response.status_code in {200, 201, 202, 204}:
            return self.get_status(pipeline_response)
        raise OperationFailed("Operation failed or canceled")


class SecurityDomainUploadPollingMethod(PollingTerminationMixin, LROBasePolling):
    """Polling method that will poll the HSM's activation but returns None.

    This is manually done because the generated implementation returns a poller with a status monitor for a final
    result. Python guidelines suggest returning None instead in this scenario, since the polling status can already be
    accessed from the poller object.
    """

    def initialize(
        self,
        client: PipelineClient[Any, Any],
        initial_response: PipelineResponse[HttpRequest, HttpResponse],
        deserialization_callback: Callable[
            [PipelineResponse[HttpRequest, HttpResponse]],
            PollingReturnType_co,
        ],
    ) -> None:
        """Set the initial status of this LRO.

        :param client: The Azure Core Pipeline client used to make request.
        :type client: ~azure.core.pipeline.PipelineClient
        :param initial_response: The initial response for the call.
        :type initial_response: ~azure.core.pipeline.PipelineResponse
        :param deserialization_callback: A callback function to deserialize the final response.
        :type deserialization_callback: callable
        :raises: HttpResponseError if initial status is incorrect LRO state
        """

        def get_long_running_output(_):
            return None

        super().initialize(client, initial_response, get_long_running_output)

    def resource(self) -> None:
        """Return the final resource -- in this case, None.

        :rtype: None
        :return: The final resource -- in this case, None.
        """
        return None


class SecurityDomainUploadNoPolling(SecurityDomainUploadPollingMethod, NoPollingMixin):
    """Polling method for security domain upload operations that bypass polling."""
