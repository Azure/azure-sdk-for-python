# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.polling.base_polling import LocationPolling


class TrainingPolling(LocationPolling):

    def get_polling_url(self):
        # type: () -> str
        """Return the polling URL.
        """
        return self._location_url + "?includeKeys=true"

    def get_status(self, pipeline_response):
        # type: (PipelineResponseType) -> str
        """Process the latest status update retrieved from a 'location' header.

        :param azure.core.pipeline.PipelineResponse response: latest REST call response.
        :raises: BadResponse if response has no body and not status 200.
        """

        if pipeline_response.http_response.status_code == 200:
            if pipeline_response.context['deserialized_data']['modelInfo']['status'] != "creating":
                return "Succeeded"
            return "InProgress"
        return "Failed"
