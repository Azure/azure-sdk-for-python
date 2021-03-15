#my_polling 

from azure.core.polling.base_polling import (
    LongRunningOperation,
    _is_empty,
    _as_json,
    BadResponse,
    OperationFailed
)


class StatusPollingGETRequest(LongRunningOperation):
    """Implements a Location polling.
    """

    def __init__(self):
        self._location_url = None

    def can_poll(self, pipeline_response):
        # type: (PipelineResponseType) -> bool
        """Answer if this polling method could be used.
        """
        response = pipeline_response.http_response
        if not _is_empty(response):
            body = _as_json(response)
            status = body.get("status")
            return True if status else False
        return False

    def get_polling_url(self):
        # type: () -> str
        """Return the polling URL.
        """
        return self._async_url

    def get_final_get_url(self, pipeline_response):
        # type: (PipelineResponseType) -> Optional[str]
        """If a final GET is needed, returns the URL.

        :rtype: str
        """
        return self._async_url

    def set_initial_status(self, pipeline_response):
        # type: (PipelineResponseType) -> str
        """Process first response after initiating long running operation.

        :param azure.core.pipeline.PipelineResponse response: initial REST call response.
        """
        response = pipeline_response.http_response
        if not _is_empty(response):
            body = _as_json(response)
            status = body.get("status")
            if status:
                return status
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
                return status
            else:
                raise BadResponse("No status found in body")
        raise BadResponse("The response from long running operation does not contain a body.")
