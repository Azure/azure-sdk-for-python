# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-few-public-methods, too-many-instance-attributes
from typing import TYPE_CHECKING

from ._api_versions import DEFAULT_VERSION
from ._headers_mixin import HeadersMixin

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any
    from azure.core.credentials import AzureKeyCredential


class SearchIndexingBufferedSenderBase(HeadersMixin):
    """Base of search indexing buffered sender"""

    _ODATA_ACCEPT = "application/json;odata.metadata=none"  # type: str
    _DEFAULT_AUTO_FLUSH_INTERVAL = 60
    _DEFAULT_INITIAL_BATCH_ACTION_COUNT = 512
    _DEFAULT_MAX_RETRIES = 3

    def __init__(self, endpoint, index_name, credential, **kwargs):
        # type: (str, str, AzureKeyCredential, **Any) -> None

        self._api_version = kwargs.pop("api_version", DEFAULT_VERSION)
        self._auto_flush = kwargs.pop("auto_flush", True)
        self._batch_action_count = kwargs.pop(
            "initial_batch_action_count", self._DEFAULT_INITIAL_BATCH_ACTION_COUNT
        )
        self._auto_flush_interval = kwargs.pop(
            "auto_flush_interval", self._DEFAULT_AUTO_FLUSH_INTERVAL
        )
        if self._auto_flush_interval <= 0:
            raise ValueError("auto_flush_interval must be a positive number.")
        self._max_retries_per_action = kwargs.pop(
            "max_retries_per_action ", self._DEFAULT_MAX_RETRIES
        )
        self._endpoint = endpoint  # type: str
        self._index_name = index_name  # type: str
        self._index_key = None
        self._credential = credential
        self._on_new = kwargs.pop("on_new", None)
        self._on_progress = kwargs.pop("on_progress", None)
        self._on_error = kwargs.pop("on_error", None)
        self._on_remove = kwargs.pop("on_remove", None)
        self._retry_counter = {}
