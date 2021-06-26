# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import base64

from azure.core.polling.async_base_polling import AsyncLROBasePolling


class KeyVaultAsyncBackupClientPollingMethod(AsyncLROBasePolling):
    def get_continuation_token(self) -> str:
        return base64.b64encode(self._operation.get_polling_url().encode()).decode("ascii")
