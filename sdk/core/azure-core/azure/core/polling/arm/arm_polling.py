# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
from azure.core.polling.base_polling import (
    LongRunningOperation,
    LROBasePolling,
    OperationFailed,
    BadResponse,
    OperationResourcePolling,
    LocationPolling,
    StatusCheckPolling,
    _as_json,
    _is_empty,
)


_AZURE_ASYNC_OPERATION_FINAL_STATE = "azure-async-operation"
_LOCATION_FINAL_STATE = "location"


class AzureAsyncOperationPolling(OperationResourcePolling):
    """Implements a operation resource polling, typically from Azure-AsyncOperation.
    """
    def __init__(self, lro_options=None):
        super(AzureAsyncOperationPolling, self).__init__(header="azure-asyncoperation")

        if lro_options is None:
            lro_options = {
                'final-state-via': _AZURE_ASYNC_OPERATION_FINAL_STATE
            }
        self.lro_options = lro_options

    def should_do_final_get(self):
        """Check whether the polling should end doing a final GET.

        :rtype: bool
        """
        return (self.lro_options['final-state-via'] == _LOCATION_FINAL_STATE and self.request.method == 'POST') or \
            self.request.method in {'PUT', 'PATCH'}


class BodyContentPolling(LongRunningOperation):
    """Poll based on the body content.

    Implement a ARM resource poller (using provisioning state).
    """

    def __init__(self):
        self.initial_response = None

    def can_poll(self, pipeline_response):
        """Answer if this polling method could be used.
        """
        response = pipeline_response.http_response
        return response.request.method == "PUT"

    def get_polling_url(self):
        """Return the polling URL.
        """
        return self.initial_response.http_response.request.url

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
        self.initial_response = pipeline_response
        response = pipeline_response.http_response

        if response.status_code == 202:
            return "InProgress"
        if response.status_code == 201:
            status = self._get_provisioning_state(response)
            return status or "InProgress"
        if response.status_code == 200:
            status = self._get_provisioning_state(response)
            return status or "Succeeded"
        if response.status_code == 204:
            return "Succeeded"

        raise OperationFailed("Invalid status found")

    def _get_provisioning_state(self, response):
        # type: (azure.core.pipeline.transport.HttpResponse) -> None
        """
        Attempt to get provisioning state from resource.
        :param azure.core.pipeline.transport.HttpResponse response: latest REST call response.
        :returns: Status if found, else 'None'.
        """
        if _is_empty(response):
            return None
        body = _as_json(response)
        return body.get("properties", {}).get("provisioningState")

    def get_status(self, pipeline_response):
        # type: (azure.core.pipeline.PipelineResponse) -> str
        """Process the latest status update retrieved from the same URL as
        the previous request.

        :param azure.core.pipeline.PipelineResponse response: latest REST call response.
        :raises: BadResponse if status not 200 or 204.
        """
        response = pipeline_response.http_response
        if _is_empty(response):
            raise BadResponse(
                "The response from long running operation does not contain a body."
            )

        status = self._get_provisioning_state(response)
        return status or "Succeeded"


class ARMPolling(LROBasePolling):
    def __init__(
        self, timeout=30, lro_algorithms=None, lro_options=None, **operation_config
    ):
        lro_algorithms = lro_algorithms or [
            AzureAsyncOperationPolling(lro_options=lro_options),
            LocationPolling(),
            BodyContentPolling(),
            StatusCheckPolling(),
        ]
        super(ARMPolling, self).__init__(
            timeout=timeout,
            lro_algorithms=lro_algorithms,
            lro_options=lro_options,
            **operation_config
        )
