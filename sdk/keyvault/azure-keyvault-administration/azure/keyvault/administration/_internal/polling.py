# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import base64

from azure.core.polling.base_polling import LROBasePolling, OperationFailed, OperationResourcePolling


class KeyVaultBackupClientPolling(OperationResourcePolling):
    def __init__(self):
        self._polling_url = None
        super(KeyVaultBackupClientPolling, self).__init__(operation_location_header="azure-asyncoperation")

    def get_polling_url(self):
        return self._polling_url

    def get_final_get_url(self, pipeline_response):
        return None

    def set_initial_status(self, pipeline_response):
        response = pipeline_response.http_response
        self._polling_url = response.headers["azure-asyncoperation"]

        if response.status_code in {200, 201, 202, 204}:
            return self.get_status(pipeline_response)
        raise OperationFailed("Operation failed or canceled")


class KeyVaultBackupClientPollingMethod(LROBasePolling):
    def get_continuation_token(self):
        # type: () -> str
        return base64.b64encode(self._operation.get_polling_url().encode()).decode("ascii")
