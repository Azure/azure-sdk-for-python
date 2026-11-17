# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------

from azure.core.polling.async_base_polling import AsyncLROBasePolling

_FINISHED = frozenset(["succeeded", "canceled", "cancelled", "failed", "partiallycompleted"])


class AnalyzeDocumentsAsyncLROPollingMethod(AsyncLROBasePolling):
    """Custom async polling method for Analyze Documents LROs.

    The service may report terminal cancellation state as ``cancelled``.
    azure-core's default AsyncLROBasePolling only recognizes ``canceled``.
    """

    def finished(self) -> bool:
        status = self.status()
        if hasattr(status, "value"):
            status = status.value
        return str(status).lower() in _FINISHED
