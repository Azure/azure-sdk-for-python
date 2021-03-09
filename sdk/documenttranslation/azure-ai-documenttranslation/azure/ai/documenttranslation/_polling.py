# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.polling.base_polling import (
    OperationResourcePolling,
    _is_empty,
    _as_json,
    BadResponse,
    OperationFailed
)


class TranslationPolling(OperationResourcePolling):
    """Polling method overrides for custom analyze endpoints."""

    def can_poll(self, pipeline_response):
        """Answer if this polling method could be used.
        """
        location = pipeline_response.http_request.url
        return True if location else False

    def get_polling_url(self):
        # type: () -> str
        """Return the polling URL.
        """
        return self._async_url

    def set_initial_status(self, pipeline_response):
        # type: (PipelineResponseType) -> str
        """Process first response after initiating long running operation.

        :param azure.core.pipeline.PipelineResponse response: initial REST call response.
        """
        self._request = pipeline_response.http_response.request
        response = pipeline_response.http_response

        self._async_url = self._request.url

        if response.status_code in {200, 201, 202, 204} and self._async_url:
            return "InProgress"
        raise OperationFailed("Operation failed or canceled")

    def get_status(self, pipeline_response):
        # type: (PipelineResponseType) -> str
        """Process the latest status update retrieved from an "Operation-Location" header.

        :param azure.core.pipeline.PipelineResponse response: The response to extract the status.
        :raises: BadResponse if response has no body, or body does not contain status.
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
        return status
