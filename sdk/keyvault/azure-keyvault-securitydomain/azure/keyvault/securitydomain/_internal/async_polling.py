# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.polling.async_base_polling import AsyncLROBasePolling

from .polling import SecurityDomainClientDownloadPollingMethod, SecurityDomainClientUploadPollingMethod


class AsyncSecurityDomainClientDownloadPollingMethod(AsyncLROBasePolling, SecurityDomainClientDownloadPollingMethod):
    pass


class AsyncSecurityDomainClientUploadPollingMethod(AsyncLROBasePolling, SecurityDomainClientUploadPollingMethod):
    pass
