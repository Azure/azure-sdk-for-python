# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._client_async import DocumentTranslationClient
from ._async_polling import AsyncDocumentTranslationLROPoller

__all__ = ["DocumentTranslationClient", "AsyncDocumentTranslationLROPoller"]
