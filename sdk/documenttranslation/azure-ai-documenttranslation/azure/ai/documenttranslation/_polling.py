# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.polling.base_polling import (
    LongRunningOperation,
    _is_empty,
    _as_json,
    BadResponse,
    OperationFailed
)


class TranslationPolling(LongRunningOperation):
    """Implements a Location polling.
    """

    def __init__(self):
        self._async_url = None

    def can_poll(self, pipeline_response):
        # type: (PipelineResponseType) -> bool
        """Answer if this polling method could be used.
        """
        response = pipeline_response.http_response
        if not _is_empty(response):
            body = _as_json(response)
            status = body.get("status")
            if status:
                return True
        return False

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
        self._async_url = pipeline_response.http_response.request.url

        response = pipeline_response.http_response
        if response.status_code in {200, 201, 202, 204} and self._async_url:
            return "InProgress"
        raise OperationFailed("Operation failed or canceled")

    def get_status(self, pipeline_response):
        # type: (PipelineResponseType) -> str
        """Process the latest status update retrieved from a 'location' header.

        :param azure.core.pipeline.PipelineResponse response: latest REST call response.
        :raises: BadResponse if response has no body and not status 202.
        """
        response = pipeline_response.http_response
        if not _is_empty(response):
            body = _as_json(response)
            status = body.get("status")
            if status:
                return self._map_nonstandard_statuses(status)
            raise BadResponse("No status found in body")
        raise BadResponse("The response from long running operation does not contain a body.")

    def get_final_get_url(self, pipeline_response):
        # type: (PipelineResponseType) -> Optional[str]
        """If a final GET is needed, returns the URL.

        :rtype: str
        """
        return None

    # pylint: disable=R0201
    def _map_nonstandard_statuses(self, status):
        # type: (str) -> str
        """Map non-standard statuses.

        :param str status: lro process status.
        """
        if status in ["ValidationFailed"]:
            return "Failed"
        if status in ["Cancelled", "Cancelling"]:
            return "Canceled"
        return status
