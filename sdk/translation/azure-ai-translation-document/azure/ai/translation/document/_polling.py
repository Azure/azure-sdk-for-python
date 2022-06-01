# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Any, Union, Tuple, TypeVar, Dict
from azure.core.polling import LROPoller
from azure.core.polling.base_polling import (
    LROBasePolling,
    OperationResourcePolling,
    _is_empty,
    _as_json,
    BadResponse,
    OperationFailed,
    _raise_if_bad_http_status_and_method,
)

from azure.core.exceptions import HttpResponseError, ODataV4Format
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import (
    HttpResponse,
    AsyncHttpResponse,
    HttpRequest,
)
from ._generated.models import TranslationStatus as _TranslationStatus
from ._models import TranslationStatus


ResponseType = Union[HttpResponse, AsyncHttpResponse]
PipelineResponseType = PipelineResponse[HttpRequest, ResponseType]
PollingReturnType = TypeVar("PollingReturnType")

_FINISHED = frozenset(["succeeded", "cancelled", "cancelling", "failed"])
_FAILED = frozenset(["validationfailed"])


class DocumentTranslationLROPoller(LROPoller[PollingReturnType]):
    """A custom poller implementation for Document Translation. Call `result()` on the poller to return
    a pageable of :class:`~azure.ai.translation.document.DocumentStatus`."""

    @property
    def id(self) -> str:
        """The ID for the translation operation

        :rtype: str
        """
        if self._polling_method._current_body:  # type: ignore # pylint: disable=protected-access
            return (
                self._polling_method._current_body.id  # type: ignore # pylint: disable=protected-access
            )
        return (
            self._polling_method._get_id_from_headers()  # type: ignore # pylint: disable=protected-access
        )

    @property
    def details(self) -> TranslationStatus:
        """The details for the translation operation

        :rtype: ~azure.ai.translation.document.TranslationStatus
        """
        if self._polling_method._current_body:  # type: ignore # pylint: disable=protected-access
            return TranslationStatus._from_generated(  # pylint: disable=protected-access
                self._polling_method._current_body  # type: ignore # pylint: disable=protected-access
            )
        return TranslationStatus(id=self._polling_method._get_id_from_headers())  # type: ignore # pylint: disable=protected-access


class DocumentTranslationLROPollingMethod(LROBasePolling):
    """A custom polling method implementation for Document Translation."""

    def __init__(self, *args, **kwargs):
        self._cont_token_response = kwargs.pop("cont_token_response")
        super().__init__(*args, **kwargs)

    @property
    def _current_body(self) -> _TranslationStatus:
        return _TranslationStatus.deserialize(self._pipeline_response)

    def _get_id_from_headers(self) -> str:
        return self._initial_response.http_response.headers[
            "Operation-Location"
        ].split("/batches/")[1]

    def finished(self) -> bool:
        """Is this polling finished?
        :rtype: bool
        """
        return self._finished(self.status())

    @staticmethod
    def _finished(status) -> bool:
        if hasattr(status, "value"):
            status = status.value
        return str(status).lower() in _FINISHED

    @staticmethod
    def _failed(status) -> bool:
        if hasattr(status, "value"):
            status = status.value
        return str(status).lower() in _FAILED

    def get_continuation_token(self) -> str:
        if self._current_body:
            return self._current_body.id
        return self._get_id_from_headers()

    def from_continuation_token(self, continuation_token: str, **kwargs: Any) -> Tuple:  # type: ignore
        try:
            client = kwargs["client"]
        except KeyError:
            raise ValueError(
                "Need kwarg 'client' to be recreated from continuation_token"
            )

        try:
            deserialization_callback = kwargs["deserialization_callback"]
        except KeyError:
            raise ValueError(
                "Need kwarg 'deserialization_callback' to be recreated from continuation_token"
            )

        return client, self._cont_token_response, deserialization_callback

    def _poll(self) -> None:
        """Poll status of operation so long as operation is incomplete and
        we have an endpoint to query.

        :param callable update_cmd: The function to call to retrieve the
         latest status of the long running operation.
        :raises: OperationFailed if operation status 'Failed' or 'Canceled'.
        :raises: BadStatus if response status invalid.
        :raises: BadResponse if response invalid.
        """

        while not self.finished():
            self._delay()
            self.update_status()

        if self._failed(self.status()):
            raise OperationFailed("Operation failed or canceled")

        final_get_url = self._operation.get_final_get_url(self._pipeline_response)
        if final_get_url:
            self._pipeline_response = self.request_status(final_get_url)
            _raise_if_bad_http_status_and_method(self._pipeline_response.http_response)


class TranslationPolling(OperationResourcePolling):
    """Implements a Location polling."""

    def can_poll(self, pipeline_response: PipelineResponseType) -> bool:
        """Answer if this polling method could be used."""
        response = pipeline_response.http_response
        can_poll = self._operation_location_header in response.headers
        if can_poll:
            return True

        if not _is_empty(response):
            body = _as_json(response)
            status = body.get("status")
            if status:
                return True
        return False

    def _set_async_url_if_present(self, response: ResponseType) -> None:
        self._async_url = response.headers.get(self._operation_location_header)
        if not self._async_url:
            self._async_url = response.request.url

    def get_status(self, pipeline_response: PipelineResponseType) -> str:
        """Process the latest status update retrieved from a 'location' header.

        :param azure.core.pipeline.PipelineResponse pipeline_response: latest REST call response.
        :raises: BadResponse if response has no body and not status 202.
        """
        response = pipeline_response.http_response
        if not _is_empty(response):
            body = _as_json(response)
            status = body.get("status")
            if status:
                return self._map_nonstandard_statuses(status, body)
            raise BadResponse("No status found in body")
        raise BadResponse(
            "The response from long running operation does not contain a body."
        )

    # pylint: disable=R0201
    def _map_nonstandard_statuses(self, status: str, body: Dict[str, Any]) -> str:
        """Map non-standard statuses.

        :param str status: lro process status.
        :param str body: pipeline response body.
        """
        if status == "ValidationFailed":
            self.raise_error(body)
        return status

    def raise_error(self, body: Dict[str, Any]) -> None:
        error = body["error"]
        if body["error"].get("innerError", None):
            error = body["error"]["innerError"]
        http_response_error = HttpResponseError(
            message="({}): {}".format(error["code"], error["message"])
        )
        http_response_error.error = ODataV4Format(error)  # set error.code
        raise http_response_error
