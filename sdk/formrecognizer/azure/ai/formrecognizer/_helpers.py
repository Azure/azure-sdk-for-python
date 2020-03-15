# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.polling.base_polling import LongRunningOperation, OperationFailed


class TrainingPolling(LongRunningOperation):
    """Implements a Location polling.
    """

    def __init__(self):
        self.location_url = None

    def can_poll(self, pipeline_response):
        """Answer if this polling method could be used.
        """
        response = pipeline_response.http_response
        return 'location' in response.headers

    def get_polling_url(self):
        """Return the polling URL.
        """
        return self.location_url

    def should_do_final_get(self):
        """Check whether the polling should end doing a final GET.

        :rtype: bool
        """
        return False

    def set_initial_status(self, pipeline_response):
        # type: (azure.core.pipeline.PipelineResponse) -> str
        """Process first response after initiating long running operation.

        :param azure.core.pipeline.PipelineResponse response: initial REST call response.
        """
        response = pipeline_response.http_response

        self.location_url = response.headers['location']

        if response.status_code in {200, 201, 202, 204} and self.location_url:
            return 'InProgress'
        else:
            raise OperationFailed("Operation failed or canceled")

    def get_status(self, pipeline_response):
        # type: (azure.core.pipeline.PipelineResponse) -> str
        """Process the latest status update retrieved from a 'location' header.

        :param azure.core.pipeline.PipelineResponse response: latest REST call response.
        :raises: BadResponse if response has no body and not status 202.
        """
        response = pipeline_response.http_response
        if 'location' in response.headers:
            self.location_url = response.headers['location']

        code = response.status_code
        if code == 202:
            return "InProgress"
        elif code == 200 and response.internal_response.text.find("creating") != -1:
            return "InProgress"
        else:
            return 'Succeeded'
