# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.polling.async_base_polling import AsyncLROBasePolling

from .polling import (
    SecurityDomainDownloadPollingMethod,
    SecurityDomainDownloadNoPolling,
    SecurityDomainUploadPollingMethod,
    SecurityDomainUploadNoPolling,
)


class AsyncSecurityDomainDownloadPollingMethod(AsyncLROBasePolling, SecurityDomainDownloadPollingMethod):
    pass


class AsyncSecurityDomainDownloadNoPolling(AsyncLROBasePolling, SecurityDomainDownloadNoPolling):
    pass


class AsyncSecurityDomainUploadPollingMethod(AsyncLROBasePolling, SecurityDomainUploadPollingMethod):
    pass


class AsyncSecurityDomainUploadNoPolling(AsyncLROBasePolling, SecurityDomainUploadNoPolling):
    pass
