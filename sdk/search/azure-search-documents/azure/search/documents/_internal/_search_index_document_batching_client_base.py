# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import List, TYPE_CHECKING
from typing_extensions import Protocol

from .._api_versions import validate_api_version
from .._headers_mixin import HeadersMixin

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Union
    from azure.core.credentials import AzureKeyCredential

class IndexingHook(Protocol):
    def new(self, action, **kwargs):
        # type: (*str, IndexAction, dict) -> None
        pass

    def progress(self, action, **kwargs):
        # type: (*str, IndexAction, dict) -> None
        pass

    def error(self, action, **kwargs):
        # type: (*str, IndexAction, dict) -> None
        pass

    def remove(self, action, **kwargs):
        # type: (*str, IndexAction, dict) -> None
        pass

class SearchIndexDocumentBatchingClientBase(HeadersMixin):
    """Base of search index document batching client"""
    _ODATA_ACCEPT = "application/json;odata.metadata=none"  # type: str
    _DEFAULT_WINDOW = 60
    _DEFAULT_BATCH_SIZE = 1000
    _RETRY_LIMIT = 10

    def __init__(self, endpoint, index_name, credential, **kwargs):
        # type: (str, str, AzureKeyCredential, **Any) -> None

        api_version = kwargs.pop('api_version', None)
        validate_api_version(api_version)
        self._auto_flush = kwargs.pop('auto_flush', True)
        self._batch_size = kwargs.pop('batch_size', self._DEFAULT_BATCH_SIZE)
        self._window = kwargs.pop('window', self._DEFAULT_WINDOW)
        if self._window <= 0:
            self._window = 86400
        self._endpoint = endpoint  # type: str
        self._index_name = index_name  # type: str
        self._index_key = None
        self._credential = credential  # type: AzureKeyCredential
        self._hook = kwargs.pop('hook', None)
        self._retry_counter = {}

    @property
    def batch_size(self):
        # type: () -> int
        return self._batch_size

    def _succeed_callback(self, action):
        # type: (IndexAction) -> None
        if self._hook:
            self._hook.remove(action)
            self._hook.progress(action)

    def _fail_callback(self, action):
        # type: (IndexAction) -> None
        if self._hook:
            self._hook.remove(action)
            self._hook.error(action)

    def _new_callback(self, actions):
        # type: (List[IndexAction]) -> None
        if self._hook:
            for action in actions:
                self._hook.new(action)
