# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.polling.base_polling import LROBasePolling, _FAILED


def _finished(pipeline_response, status):
    if hasattr(status, "value"):
        status = status.value
    if status.lower() == "succeeded" and \
            pipeline_response.context['deserialized_data']['modelInfo']['status'] != "creating":
        return True
    return str(status).lower() in _FAILED


class TrainingPolling(LROBasePolling):

    def __init__(
        self, timeout=30, lro_algorithms=None, lro_options=None, **operation_config
    ):
        super(TrainingPolling, self).__init__(timeout, lro_algorithms, lro_options, **operation_config)

    def finished(self):
        """Is this polling finished?
        :rtype: bool
        """
        return _finished(self._pipeline_response, self._status)

    def request_status(self, status_link):
        """Do a simple GET to this status link.

        This method re-inject 'x-ms-client-request-id'.

        :rtype: azure.core.pipeline.PipelineResponse
        """
        params = {"includeKeys": True}
        request = self._client.get(status_link, params=params)
        # Re-inject 'x-ms-client-request-id' while polling
        if "request_id" not in self._operation_config:
            self._operation_config["request_id"] = self._get_request_id()
        return self._client._pipeline.run(  # pylint: disable=protected-access
            request, stream=False, **self._operation_config
        )
