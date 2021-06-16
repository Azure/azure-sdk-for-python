# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import base64

from azure.core.polling.base_polling import BadResponse, LROBasePolling, OperationFailed, OperationResourcePolling


class KeyVaultBackupClientPolling(OperationResourcePolling):
    def __init__(self):
        super(KeyVaultBackupClientPolling, self).__init__(operation_location_header="azure-asyncoperation")

    def get_final_get_url(self, pipeline_response):
        return None

    def set_initial_status(self, pipeline_response):
        self._request = pipeline_response.http_response.request
        response = pipeline_response.http_response

        self._set_async_url_if_present(response)

        if response.status_code in {200, 201, 202, 204} and self._async_url:
            try:
                return self.get_status(pipeline_response)
            except BadResponse:
                return "InProgress"
        raise OperationFailed("Operation failed or canceled")


class KeyVaultBackupClientPollingMethod(LROBasePolling):
    def get_continuation_token(self):
        # type: () -> str
        return base64.b64encode(self._operation.get_polling_url().encode()).decode("ascii")
