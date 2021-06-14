# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import base64
from typing import TYPE_CHECKING

from azure.core.polling.base_polling import LROBasePolling, OperationResourcePolling

if TYPE_CHECKING:
    from typing import Union
    from azure.core.pipeline import PipelineResponse
    from azure.core.pipeline.transport import HttpResponse, AsyncHttpResponse, HttpRequest

    ResponseType = Union[HttpResponse, AsyncHttpResponse]
    PipelineResponseType = PipelineResponse[HttpRequest, ResponseType]


class KeyVaultBackupClientPolling(OperationResourcePolling):
    def __init__(self):
        super(KeyVaultBackupClientPolling, self).__init__(operation_location_header="azure-asyncoperation")

    def get_final_get_url(self, pipeline_response):
        return None


class KeyVaultBackupClientPollingMethod(LROBasePolling):
    def get_continuation_token(self):
        # type() -> str
        return base64.b64encode(self._operation.get_polling_url().encode()).decode("ascii")
