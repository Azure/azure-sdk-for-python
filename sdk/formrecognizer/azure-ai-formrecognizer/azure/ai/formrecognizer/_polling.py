# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import TYPE_CHECKING
from azure.core.exceptions import HttpResponseError
from azure.core.polling.base_polling import (
    LocationPolling,
    OperationResourcePolling,
    _is_empty,
    _as_json,
    BadResponse
)
if TYPE_CHECKING:
    from azure.core.pipeline import PipelineResponse


def raise_error(response, errors, message):
    for err in errors:
        message += "({}) {}\n".format(err["code"], err["message"])
    raise HttpResponseError(message=message, response=response)


class TrainingPolling(LocationPolling):
    """Polling method overrides for training endpoints.
    """

    def get_polling_url(self):
        # type: () -> str
        """Return the polling URL.
        """
        return self._location_url + "?includeKeys=true"

    def get_status(self, pipeline_response):  # pylint: disable=no-self-use
        # type: (PipelineResponse) -> str
        """Process the latest status update retrieved from a 'location' header.

        :param azure.core.pipeline.PipelineResponse pipeline_response: latest REST call response.
        :raises: BadResponse if response has no body.
        """
        response = pipeline_response.http_response
        if response.status_code == 200:
            body = _as_json(response)
            status = body['modelInfo']['status']
            if not status:
                raise BadResponse("No status found in body")
            if status.lower() == "invalid":
                train_result = body.get('trainResult')
                if train_result:
                    errors = train_result.get("errors")
                    if errors:
                        message = "Invalid model created with ID={}\n".format(body["modelInfo"]["modelId"])
                        raise_error(response, errors, message)
                return "Failed"
            if status.lower() != "creating":
                return "Succeeded"

            return "InProgress"

        return "Failed"


class AnalyzePolling(OperationResourcePolling):
    """Polling method overrides for custom analyze endpoints.
    """

    def get_status(self, pipeline_response):  # pylint: disable=no-self-use
        # type: (PipelineResponse) -> str
        """Process the latest status update retrieved from an "Operation-Location" header.
        Raise errors for issues with input document.

        :param azure.core.pipeline.PipelineResponse pipeline_response: The response to extract the status.
        :raises: BadResponse if response has no body, or body does not contain status.
            HttpResponseError if there is an error with the input document.
        """
        response = pipeline_response.http_response
        if _is_empty(response):
            raise BadResponse(
                "The response from long running operation does not contain a body."
            )

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
    """Polling method overrides for copy endpoint.

    """

    def get_status(self, pipeline_response):  # pylint: disable=no-self-use
        # type: (PipelineResponse) -> str
        """Process the latest status update retrieved from an "Operation-Location" header.
        Raise errors for issues occurring during the copy model operation.

        :param azure.core.pipeline.PipelineResponse pipeline_response: The response to extract the status.
        :raises: BadResponse if response has no body, or body does not contain status.
            HttpResponseError if there is an error with the input document.
        """
        response = pipeline_response.http_response
        if _is_empty(response):
            raise BadResponse(
                "The response from long running operation does not contain a body."
            )

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
