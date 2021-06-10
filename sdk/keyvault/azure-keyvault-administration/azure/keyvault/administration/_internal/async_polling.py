# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from azure.core.polling.base_polling import (
    BadResponse,
    BadStatus,
    HttpResponseError,
    OperationFailed,
    _raise_if_bad_http_status_and_method
)


class KeyVaultAsyncBackupClientPollingMethod(AsyncLROBasePolling):
    def initialize(self, client, initial_response, deserialization_callback):
        """Set the initial status of this LRO.

        :param initial_response: The initial pipeline response of the poller, or a URL continuation token
        :raises: HttpResponseError if initial status is incorrect LRO state
        """
        self._client = client
        self._deserialization_callback = deserialization_callback
        self._continuation_url = None

        continuation_url = type(initial_response) == str
        if continuation_url:
            self._continuation_url = initial_response
            self._operation = self._lro_algorithms[0]
            self._status = "InProgress"  # assume the operation is ongoing for now
        else:
            self._pipeline_response = self._initial_response = initial_response

            for operation in self._lro_algorithms:
                if operation.can_poll(self._initial_response, continuation_url=continuation_url):
                    self._operation = operation
                    break
            else:
                raise BadResponse("Unable to find status link for polling.")

            try:
                _raise_if_bad_http_status_and_method(self._initial_response.http_response)
                self._status = self._operation.set_initial_status(
                    self._initial_response, continuation_url=initial_response
                )

            except BadStatus as err:
                self._status = "Failed"
                raise HttpResponseError(response=self._initial_response.http_response, error=err)
            except BadResponse as err:
                self._status = "Failed"
                raise HttpResponseError(
                    response=self._initial_response.http_response, message=str(err), error=err
                )
            except OperationFailed as err:
                raise HttpResponseError(response=self._initial_response.http_response, error=err)

    def get_continuation_token(self):
        return self._operation.get_polling_url().http_response.headers["azure-asyncoperation"]

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
        return super(KeyVaultAsyncBackupClientPollingMethod, self)._parse_resource(pipeline_response)

    def _extract_delay(self):
        if self._continuation_url:
            return 0
        return super(KeyVaultAsyncBackupClientPollingMethod, self)._extract_delay()

    async def update_status(self):
        """Update the current status of the LRO.
        """
        if self._continuation_url:
            self._pipeline_response = await self.request_status(self._continuation_url)
        else:
            self._pipeline_response = await self.request_status(self._operation.get_polling_url())
        _raise_if_bad_http_status_and_method(self._pipeline_response.http_response)
        self._status = self._operation.get_status(self._pipeline_response)

    async def request_status(self, status_link):
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
        return await self._client._pipeline.run(  # pylint: disable=protected-access
            request, stream=False, **self._operation_config
        )
