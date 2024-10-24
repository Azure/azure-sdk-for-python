# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.polling.async_base_polling import AsyncLROBasePolling

from .polling import SecurityDomainClientPollingMethod


class AsyncSecurityDomainClientPollingMethod(SecurityDomainClientPollingMethod, AsyncLROBasePolling):
    pass
