# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import base64
from typing import TYPE_CHECKING

from azure.core.polling.base_polling import LROBasePolling, OperationFailed, OperationResourcePolling

if TYPE_CHECKING:
    from azure.core.pipeline import PipelineResponse
    from azure.core.rest import HttpResponse


class KeyVaultBackupClientPolling(OperationResourcePolling):
    def __init__(self) -> None:
        self._polling_url = ""
        super().__init__(operation_location_header="azure-asyncoperation")

    def get_polling_url(self) -> str:
        return self._polling_url

    def get_final_get_url(self, pipeline_response: "PipelineResponse") -> None:
        return None

    def set_initial_status(self, pipeline_response: "PipelineResponse") -> str:
        response = pipeline_response.http_response  # type: HttpResponse
        self._polling_url = response.headers["azure-asyncoperation"]

        if response.status_code in {200, 201, 202, 204}:
            return self.get_status(pipeline_response)
        raise OperationFailed("Operation failed or canceled")


class KeyVaultBackupClientPollingMethod(LROBasePolling):
    def get_continuation_token(self) -> str:
        """
        Get a continuation token to resume the polling later.
        
        :return: A continuation token.
        :rtype: str
        """
        # Because of the operation structure, we need to use a "continuation token" that is just the status URL.
        # This URL can then be used to fetch the status of the operation when resuming, at which point a genuine
        # continuation token will be created from the response and provided to Core.
        return base64.b64encode(self._operation.get_polling_url().encode()).decode("ascii")
