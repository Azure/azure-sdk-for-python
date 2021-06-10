# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.polling.base_polling import (
    BadResponse,
    BadStatus,
    HttpResponseError,
    LROBasePolling,
    OperationFailed,
    OperationResourcePolling,
    _raise_if_bad_http_status_and_method
)


class KeyVaultBackupClientPolling(OperationResourcePolling):
    def __init__(self):
        super(KeyVaultBackupClientPolling, self).__init__(operation_location_header="azure-asyncoperation")

    def can_poll(self, pipeline_response, **kwargs):
        """Answer if this polling method could be used.
        """
        if kwargs.get("continuation_url"):
            return True
        response = pipeline_response.http_response
        return self._operation_location_header in response.headers

    def set_initial_status(self, pipeline_response, **kwargs):
        # type: (PipelineResponseType) -> str
        """Process first response after initiating long running operation.

        :param azure.core.pipeline.PipelineResponse response: initial REST call response.
        """
        self._request = pipeline_response.http_response.request
        response = pipeline_response.http_response

        self._async_url = kwargs.get("continuation_url")
        if self._async_url is None:
            self._set_async_url_if_present(response)

        if response.status_code in {200, 201, 202, 204} and self._async_url:
            return "InProgress"
        raise OperationFailed("Operation failed or canceled")

    def get_final_get_url(self, pipeline_response):
        return None


class KeyVaultBackupClientPollingMethod(LROBasePolling):
    def initialize(self, client, initial_response, deserialization_callback):
        """Set the initial status of this LRO.

        :param initial_response: The initial response of the poller
        :raises: HttpResponseError if initial status is incorrect LRO state
        """
        self._client = client
        continuation_url = type(initial_response) == str
        if continuation_url:
            # get the status of the operation and a pipeline response from a URL continuation token
            self._pipeline_response = self._initial_response = self.request_initial_status(initial_response)
        else:
            self._pipeline_response = self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback

        for operation in self._lro_algorithms:
            if operation.can_poll(self._initial_response, continuation_url=continuation_url):
                self._operation = operation
                break
        else:
            raise BadResponse("Unable to find status link for polling.")

        try:
            _raise_if_bad_http_status_and_method(self._initial_response.http_response)
            self._status = self._operation.set_initial_status(self._initial_response, continuation_url=initial_response)

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

    def request_initial_status(self, status_link):
        """Do a GET to this status link to obtain a pipeline response.

        :rtype: azure.core.pipeline.PipelineResponse
        """
        if self._path_format_arguments:
            status_link = self._client.format_url(status_link, **self._path_format_arguments)
        request = self._client.get(status_link)
        return self._client._pipeline.run(  # pylint: disable=protected-access
            request, stream=False, **self._operation_config
        )
