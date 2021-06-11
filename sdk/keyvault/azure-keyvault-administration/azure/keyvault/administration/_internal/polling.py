# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from azure.core.polling.base_polling import LROBasePolling, OperationResourcePolling

if TYPE_CHECKING:
    from typing import Union
    from azure.core.pipeline import PipelineResponse
    from azure.core.pipeline.transport import (
        HttpResponse,
        AsyncHttpResponse,
        HttpRequest,
    )

    ResponseType = Union[HttpResponse, AsyncHttpResponse]
    PipelineResponseType = PipelineResponse[HttpRequest, ResponseType]


class KeyVaultBackupClientPolling(OperationResourcePolling):
    def __init__(self):
        super(KeyVaultBackupClientPolling, self).__init__(operation_location_header="azure-asyncoperation")

    def get_final_get_url(self, pipeline_response):
        return None


class KeyVaultBackupClientPollingMethod(LROBasePolling):
    def initialize(self, client, initial_response, deserialization_callback):
        """Set the initial status of this LRO.

        :param initial_response: The initial pipeline response of the poller, or a URL continuation token
        :raises: HttpResponseError if initial status is incorrect LRO state
        """
        self._continuation_url = None

        if type(initial_response) != str:
            super(KeyVaultBackupClientPollingMethod, self).initialize(
                client, initial_response, deserialization_callback
            )

        else:
            self._client = client
            self._continuation_url = initial_response
            self._deserialization_callback = deserialization_callback
            self._operation = self._lro_algorithms[0]
            self._operation._async_url = initial_response  # pylint: disable=protected-access
            self._status = "InProgress" # assume the operation is ongoing for now so the actual status gets polled

    def get_continuation_token(self):
        return self._operation.get_polling_url()

    @classmethod
    def from_continuation_token(cls, continuation_token, **kwargs):
        """continuation_token is expected to be the URL of a pending operation"""
        # type(str, Any) -> Tuple
        try:
            client = kwargs["client"]
        except KeyError:
            raise ValueError("Need kwarg 'client' to be recreated from continuation_token")

        try:
            deserialization_callback = kwargs["deserialization_callback"]
        except KeyError:
            raise ValueError("Need kwarg 'deserialization_callback' to be recreated from continuation_token")

        return client, continuation_token, deserialization_callback

    def _parse_resource(self, pipeline_response):
        # type: (PipelineResponseType) -> Optional[Any]
        """Assuming this response is a resource, use the deserialization callback to parse it.
        If body is empty, assuming no resource to return.
        """
        if pipeline_response is None:
            return None
        return super(KeyVaultBackupClientPollingMethod, self)._parse_resource(pipeline_response)

    def _extract_delay(self):
        if self._continuation_url:
            return 0
        return super(KeyVaultBackupClientPollingMethod, self)._extract_delay()

    def request_status(self, status_link):
        """Do a simple GET to this status link.

        This method re-inject 'x-ms-client-request-id'.

        :rtype: azure.core.pipeline.PipelineResponse
        """
        if self._path_format_arguments:
            status_link = self._client.format_url(status_link, **self._path_format_arguments)
        request = self._client.get(status_link)
        if self._continuation_url is None:
            # Re-inject 'x-ms-client-request-id' while polling
            if "request_id" not in self._operation_config:
                self._operation_config["request_id"] = self._get_request_id()
        return self._client._pipeline.run(  # pylint: disable=protected-access
            request, stream=False, **self._operation_config
        )
