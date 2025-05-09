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

# The correct success response should be "Succeeded", but this has already shipped. Handle "Success" just in case.
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
    def __init__(self) -> None:
        self._polling_url = ""
        super().__init__(operation_location_header="azure-asyncoperation")

    def get_polling_url(self) -> str:
        return self._polling_url

    def get_final_get_url(self, pipeline_response: "PipelineResponse") -> None:
        return None

    def set_initial_status(self, pipeline_response: "PipelineResponse") -> str:
        response: HttpResponse = pipeline_response.http_response
        self._polling_url = response.headers["azure-asyncoperation"]

        if response.status_code in {200, 201, 202, 204}:
            # The initial download response doesn't contain the status, so we consider it as "InProgress"
            # The next status update request will point to the download status endpoint and correctly update
            return "InProgress"
        raise OperationFailed("Operation failed or canceled")


class SecurityDomainDownloadPollingMethod(PollingTerminationMixin, LROBasePolling):
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
        """Return the built resource.

        :rtype: any
        :return: The built resource.
        """
        # The final response should actually be the security domain object that was returned in the initial response
        return cast(SecurityDomain, self.parse_resource(self._initial_response))


class SecurityDomainDownloadNoPolling(SecurityDomainDownloadPollingMethod, NoPollingMixin):
    pass


class SecurityDomainUploadPolling(SecurityDomainDownloadPolling):
    def set_initial_status(self, pipeline_response: PipelineResponse) -> str:
        response: HttpResponse = pipeline_response.http_response
        self._polling_url = response.headers["azure-asyncoperation"]

        if response.status_code in {200, 201, 202, 204}:
            return self.get_status(pipeline_response)
        raise OperationFailed("Operation failed or canceled")


class SecurityDomainUploadPollingMethod(PollingTerminationMixin, LROBasePolling):
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
        """Return the built resource.

        :rtype: any
        :return: The built resource.
        """
        return None

class SecurityDomainUploadNoPolling(SecurityDomainUploadPollingMethod, NoPollingMixin):
    pass
