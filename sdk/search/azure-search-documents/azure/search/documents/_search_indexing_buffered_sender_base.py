# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-few-public-methods, too-many-instance-attributes
from typing import Any, Union, Dict, Optional

from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.core.credentials_async import AsyncTokenCredential
from ._api_versions import DEFAULT_VERSION
from ._headers_mixin import HeadersMixin


class SearchIndexingBufferedSenderBase(HeadersMixin):
    """Base of search indexing buffered sender"""

    _ODATA_ACCEPT: str = "application/json;odata.metadata=none"
    _DEFAULT_AUTO_FLUSH_INTERVAL = 60
    _DEFAULT_INITIAL_BATCH_ACTION_COUNT = 512
    _DEFAULT_MAX_RETRIES = 3

    def __init__(
        self,
        endpoint: str,
        index_name: str,
        credential: Union[AzureKeyCredential, TokenCredential, AsyncTokenCredential],
        *,
        auto_flush: bool = True,
        initial_batch_action_count: int = _DEFAULT_INITIAL_BATCH_ACTION_COUNT,
        auto_flush_interval: int = _DEFAULT_AUTO_FLUSH_INTERVAL,
        max_retries_per_action: int = _DEFAULT_MAX_RETRIES,
        **kwargs: Any
    ) -> None:

        self._api_version = kwargs.pop("api_version", DEFAULT_VERSION)
        self._auto_flush = auto_flush
        self._batch_action_count = initial_batch_action_count
        self._auto_flush_interval = auto_flush_interval
        if self._auto_flush_interval <= 0:
            raise ValueError("auto_flush_interval must be a positive number.")
        self._max_retries_per_action = max_retries_per_action
        self._endpoint = endpoint
        self._index_name = index_name
        self._index_key: Optional[str] = None
        self._credential = credential
        self._on_new = kwargs.pop("on_new", None)
        self._on_progress = kwargs.pop("on_progress", None)
        self._on_error = kwargs.pop("on_error", None)
        self._on_remove = kwargs.pop("on_remove", None)
        self._retry_counter: Dict[str, int] = {}
