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
from enum import Enum
from typing import TYPE_CHECKING, Optional, Union

from azure.core import CaseInsensitiveEnumMeta
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

if TYPE_CHECKING:
    from azure.core.pipeline import PipelineResponse
    from azure.core.pipeline.transport import (
        HttpResponse,
        AsyncHttpResponse,
        HttpRequest,
    )

    ResponseType = Union[HttpResponse, AsyncHttpResponse]
    PipelineResponseType = PipelineResponse[HttpRequest, ResponseType]


class _LroOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Known LRO options from Swagger."""

    FINAL_STATE_VIA = "final-state-via"


class _FinalStateViaOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Possible final-state-via options."""

    AZURE_ASYNC_OPERATION_FINAL_STATE = "azure-async-operation"
    LOCATION_FINAL_STATE = "location"


class AzureAsyncOperationPolling(OperationResourcePolling):
    """Implements a operation resource polling, typically from Azure-AsyncOperation.
    """

    def __init__(self, lro_options=None):
        super(AzureAsyncOperationPolling, self).__init__(
            operation_location_header="azure-asyncoperation"
        )

        self._lro_options = lro_options or {}

    def get_final_get_url(self, pipeline_response):
        # type: (PipelineResponseType) -> Optional[str]
        """If a final GET is needed, returns the URL.

        :rtype: str
        """
        if (
            self._lro_options.get(_LroOption.FINAL_STATE_VIA)
            == _FinalStateViaOption.AZURE_ASYNC_OPERATION_FINAL_STATE
            and self._request.method == "POST"
        ):
            return None
        return super(AzureAsyncOperationPolling, self).get_final_get_url(
            pipeline_response
        )


class BodyContentPolling(LongRunningOperation):
    """Poll based on the body content.

    Implement a ARM resource poller (using provisioning state).
    """

    def __init__(self):
        self._initial_response = None

    def can_poll(self, pipeline_response):
        # type: (PipelineResponseType) -> bool
        """Answer if this polling method could be used.
        """
        response = pipeline_response.http_response
        return response.request.method in ["PUT", "PATCH"]

    def get_polling_url(self):
        # type: () -> str
        """Return the polling URL.
        """
        return self._initial_response.http_response.request.url

    def get_final_get_url(self, pipeline_response):
        # type: (PipelineResponseType) -> Optional[str]
        """If a final GET is needed, returns the URL.

        :rtype: str
        """
        return None

    def set_initial_status(self, pipeline_response):
        # type: (PipelineResponseType) -> str
        """Process first response after initiating long running operation.

        :param azure.core.pipeline.PipelineResponse response: initial REST call response.
        """
        self._initial_response = pipeline_response
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

    @staticmethod
    def _get_provisioning_state(response):
        # type: (ResponseType) -> Optional[str]
        """Attempt to get provisioning state from resource.

        :param azure.core.pipeline.transport.HttpResponse response: latest REST call response.
        :returns: Status if found, else 'None'.
        """
        if _is_empty(response):
            return None
        body = _as_json(response)
        return body.get("properties", {}).get("provisioningState")

    def get_status(self, pipeline_response):
        # type: (PipelineResponseType) -> str
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
        self,
        timeout=30,
        lro_algorithms=None,
        lro_options=None,
        path_format_arguments=None,
        **operation_config
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
            path_format_arguments=path_format_arguments,
            **operation_config
        )

__all__ = [
    'AzureAsyncOperationPolling',
    'BodyContentPolling',
    'ARMPolling',
]
