# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=protected-access

import datetime
import json
from typing import Callable, Mapping, Union, TypeVar, Any, Optional
from typing_extensions import Protocol, runtime_checkable
from azure.core.exceptions import HttpResponseError, ODataV4Format
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import (
    HttpResponse,
    AsyncHttpResponse,
    HttpRequest,
)
from azure.core.polling import LROPoller, PollingMethod
from azure.core.polling.base_polling import (
    LocationPolling,
    OperationResourcePolling,
    _is_empty,
    _as_json,
    BadResponse,
)

PollingReturnType = TypeVar("PollingReturnType")


ResponseType = Union[HttpResponse, AsyncHttpResponse]
PipelineResponseType = PipelineResponse[HttpRequest, ResponseType]


def raise_error(response, errors, message):
    error_message = "({}) {}{}".format(errors[0]["code"], errors[0]["message"], message)
    error = HttpResponseError(message=error_message, response=response)
    error.error = ODataV4Format(errors[0])
    raise error


def parse_operation_id(location):
    prefix = location.split("?api-version")[0]
    operation_id = prefix.split("/operations/")[1]
    return operation_id


@runtime_checkable
class DocumentModelAdministrationLROPoller(Protocol[PollingReturnType]):
    """Implements a protocol followed by returned poller objects."""

    @property
    def details(  # pylint: disable=no-self-use, unused-argument
        self,
    ) -> Mapping[str, Any]:
        ...

    def polling_method(  # pylint: disable=no-self-use
        self,
    ) -> PollingMethod[PollingReturnType]:
        ...

    def continuation_token(self) -> str:  # pylint: disable=no-self-use
        ...

    def status(self) -> str:  # pylint: disable=no-self-use
        ...

    def result(  # pylint: disable=no-self-use, unused-argument
        self, timeout: Optional[int] = None
    ) -> PollingReturnType:
        ...

    def wait(self, timeout: Optional[float] = None) -> None:  # pylint: disable=no-self-use, unused-argument
        ...

    def done(self) -> bool:  # pylint: disable=no-self-use
        ...

    def add_done_callback(self, func: Callable) -> None:  # pylint: disable=no-self-use, unused-argument
        ...

    def remove_done_callback(self, func: Callable) -> None:  # pylint: disable=no-self-use, unused-argument
        ...


class DocumentModelAdministrationClientLROPoller(LROPoller[PollingReturnType]):
    """Custom poller for model build operations. Call `result()` on the poller to return
    a :class:`~azure.ai.formrecognizer.DocumentModelDetails`.

    .. versionadded:: 2021-09-30-preview
        The *DocumentModelAdministrationLROPoller* poller object
    """

    @property
    def _current_body(self):
        body = self.polling_method()._pipeline_response.http_response.text()
        if body:
            return json.loads(body)
        return {}

    @property
    def details(self) -> Mapping[str, Any]:
        """Returns metadata associated with the long-running operation."""
        created_on = self._current_body.get("createdDateTime", None)
        if created_on:
            created_on = datetime.datetime.strptime(created_on, "%Y-%m-%dT%H:%M:%SZ")
        last_updated_on = self._current_body.get("lastUpdatedDateTime", None)
        if last_updated_on:
            last_updated_on = datetime.datetime.strptime(last_updated_on, "%Y-%m-%dT%H:%M:%SZ")
        return {
            "operation_id": parse_operation_id(
                self.polling_method()._initial_response.http_response.headers["Operation-Location"]  # type: ignore
            ),
            "operation_kind": self._current_body.get("kind", None),
            "percent_completed": self._current_body.get("percentCompleted", 0),
            "resource_location_url": self._current_body.get("resourceLocation", None),
            "created_on": created_on,
            "last_updated_on": last_updated_on,
        }

    @classmethod
    def from_continuation_token(
        cls, polling_method: PollingMethod[PollingReturnType], continuation_token: str, **kwargs: Any
    ) -> "DocumentModelAdministrationClientLROPoller":
        (
            client,
            initial_response,
            deserialization_callback,
        ) = polling_method.from_continuation_token(continuation_token, **kwargs)

        return cls(client, initial_response, deserialization_callback, polling_method)


class DocumentModelAdministrationPolling(OperationResourcePolling):
    """Polling method overrides for training endpoints."""

    def get_final_get_url(self, pipeline_response: PipelineResponseType) -> None:
        """If a final GET is needed, returns the URL.

        :rtype: None
        """
        return None


class FormTrainingPolling(LocationPolling):
    """Polling method overrides for training endpoints."""

    def get_polling_url(self) -> str:
        """Return the polling URL."""
        return self._location_url + "?includeKeys=true"

    def get_status(self, pipeline_response: PipelineResponse) -> str:  # pylint: disable=no-self-use
        """Process the latest status update retrieved from a 'location' header.

        :param azure.core.pipeline.PipelineResponse pipeline_response: latest REST call response.
        :raises: BadResponse if response has no body.
        """
        response = pipeline_response.http_response
        if response.status_code == 200:
            body = _as_json(response)
            status = body["modelInfo"]["status"]
            if not status:
                raise BadResponse("No status found in body")
            if status.lower() == "invalid":
                train_result = body.get("trainResult")
                if train_result:
                    errors = train_result.get("errors")
                    if errors:
                        message = "\nInvalid model created with ID={}".format(body["modelInfo"]["modelId"])
                        raise_error(response, errors, message)
                return "Failed"
            if status.lower() != "creating":
                return "Succeeded"

            return "InProgress"

        return "Failed"


class AnalyzePolling(OperationResourcePolling):
    """Polling method overrides for custom analyze endpoints."""

    def get_status(self, pipeline_response: PipelineResponse) -> str:  # pylint: disable=no-self-use
        """Process the latest status update retrieved from an "Operation-Location" header.
        Raise errors for issues with input document.

        :param azure.core.pipeline.PipelineResponse pipeline_response: The response to extract the status.
        :raises: BadResponse if response has no body, or body does not contain status.
            HttpResponseError if there is an error with the input document.
        """
        response = pipeline_response.http_response
        if _is_empty(response):
            raise BadResponse("The response from long running operation does not contain a body.")

        body = _as_json(response)
        status = body.get("status")
        if not status:
            raise BadResponse("No status found in body")
        if status.lower() == "failed":
            analyze_result = body.get("analyzeResult")
            if analyze_result:
                errors = analyze_result.get("errors")
                if errors:
                    raise_error(response, errors, message="")
        return status


class CopyPolling(OperationResourcePolling):
    """Polling method overrides for copy endpoint."""

    def get_status(self, pipeline_response: PipelineResponse) -> str:  # pylint: disable=no-self-use
        """Process the latest status update retrieved from an "Operation-Location" header.
        Raise errors for issues occurring during the copy model operation.

        :param azure.core.pipeline.PipelineResponse pipeline_response: The response to extract the status.
        :raises: BadResponse if response has no body, or body does not contain status.
            HttpResponseError if there is an error with the input document.
        """
        response = pipeline_response.http_response
        if _is_empty(response):
            raise BadResponse("The response from long running operation does not contain a body.")

        body = _as_json(response)
        status = body.get("status")
        if not status:
            raise BadResponse("No status found in body")
        if status.lower() == "failed":
            copy_result = body.get("copyResult")
            if copy_result:
                errors = copy_result.get("errors")
                if errors:
                    raise_error(response, errors, message="")
        return status
