# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Callable, TypeVar

from azure.core.pipeline import PipelineResponse
from azure.core.polling.base_polling import (
    BadResponse,
    BadStatus,
    LROBasePolling,
    OperationFailed,
    OperationResourcePolling,
)
from azure.core.exceptions import HttpResponseError
from azure.core.rest import HttpResponse, HttpRequest

from ..models import SecurityDomainObject
from .._model_base import _deserialize
from .._serialization import Deserializer


PipelineClientType = TypeVar("PipelineClientType")

# The correct success response should be "Succeeded", but this has already shipped.
_FINISHED = frozenset(["success", "canceled", "failed"])


def _finished(status):
    if hasattr(status, "value"):
        status = status.value
    return str(status).lower() in _FINISHED


def _raise_if_bad_http_status_and_method(response: HttpResponse) -> None:
    """Check response status code is valid.

    Must be 200, 201, 202, or 204.

    :param response: The response object.
    :type response: any
    :raises: BadStatus if invalid status.
    """
    code = response.status_code
    if code in {200, 201, 202, 204}:
        return
    raise BadStatus("Invalid return status {!r} for {!r} operation".format(code, response.request.method))


def _is_empty(response: HttpResponse) -> bool:
    """Check if response body contains meaningful content.

    :param response: The response object.
    :type response: any
    :return: True if response body is empty, False otherwise.
    :rtype: bool
    """
    return not bool(response.content)


class SecurityDomainClientPolling(OperationResourcePolling):
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
            return "InProgress"
        raise OperationFailed("Operation failed or canceled")


class SecurityDomainClientPollingMethod(LROBasePolling):
    def initialize(
        self,
        client: PipelineClientType,
        initial_response: PipelineResponse[HttpRequest, HttpResponse],
        deserialization_callback: Callable[
            [PipelineResponse[HttpRequest, HttpResponse]],
            SecurityDomainObject,
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
        self._client = client
        self._pipeline_response = (  # pylint: disable=attribute-defined-outside-init
            self._initial_response  # pylint: disable=attribute-defined-outside-init
        ) = initial_response

        def get_long_running_output(pipeline_response):
            response_headers = {}
            response = pipeline_response.http_response
            deserializer = Deserializer()
            response_headers["Azure-AsyncOperation"] = deserializer._deserialize(
                "str", response.headers.get("Azure-AsyncOperation")
            )
            response_headers["Retry-After"] = deserializer._deserialize("int", response.headers.get("Retry-After"))

            deserialized = _deserialize(SecurityDomainObject, response.json())
            return deserialized

        self._deserialization_callback = get_long_running_output

        for operation in self._lro_algorithms:
            if operation.can_poll(initial_response):
                self._operation = operation
                break
        else:
            raise BadResponse("Unable to find status link for polling.")

        try:
            _raise_if_bad_http_status_and_method(self._initial_response.http_response)
            self._status = self._operation.set_initial_status(initial_response)

        except BadStatus as err:
            self._status = "Failed"
            raise HttpResponseError(response=initial_response.http_response, error=err) from err
        except BadResponse as err:
            self._status = "Failed"
            raise HttpResponseError(response=initial_response.http_response, message=str(err), error=err) from err
        except OperationFailed as err:
            raise HttpResponseError(response=initial_response.http_response, error=err) from err

    def finished(self) -> bool:
        """Is this polling finished?

        :rtype: bool
        :return: True if finished, False otherwise.
        """
        return _finished(self.status())

    def resource(self) -> SecurityDomainObject:
        """Return the built resource.

        :rtype: any
        :return: The built resource.
        """
        return self._parse_resource(self._initial_response)

    def _parse_resource(
        self,
        pipeline_response: PipelineResponse[HttpRequest, HttpResponse],
    ) -> SecurityDomainObject:
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
