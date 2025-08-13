# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Mapping, Optional, Union, IO, cast
import json
from urllib.parse import urlparse

from azure.core.exceptions import HttpResponseError
from azure.core.rest import HttpRequest
from azure.core.async_paging import AsyncItemPaged
from azure.core.polling import AsyncLROPoller
from azure.core.polling.async_base_polling import (
    AsyncLROBasePolling,
)
from azure.core.polling._async_poller import AsyncPollingMethod
from azure.core.polling import AsyncNoPolling  # lazy-import if you prefer

from ...models import (
    AnalyzeConversationOperationInput,
    AnalyzeConversationOperationState,
    ConversationActions,
)

# -------------------------
# Helpers
# -------------------------

def _parse_operation_id(op_loc: Optional[str]) -> Optional[str]:
    if not op_loc:
        return None
    path = urlparse(op_loc).path.rstrip("/")
    if "/" not in path:
        return None
    return path.rsplit("/", 1)[-1]


# -------------------------
# Custom ASYNC poller
# -------------------------

class AnalyzeConversationAsyncLROPoller(
    AsyncLROPoller[AsyncItemPaged[ConversationActions]]
):
    """Async poller that returns AsyncItemPaged[ConversationActions] and exposes operation metadata."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # populated by our deserialization callback
        self._last_state: Optional[AnalyzeConversationOperationState] = None

    @property
    def details(self) -> Mapping[str, Any]:
        """Metadata associated with the long-running operation."""
        try:
            headers = (
                self.polling_method()
                ._initial_response  # type: ignore[attr-defined]
                .http_response.headers
            )
            op_loc = headers.get("Operation-Location") or headers.get("operation-location")
        except Exception:
            op_loc = None

        d: dict = {"operation_id": _parse_operation_id(op_loc)}
        if self._last_state is not None:
            s = self._last_state  # attribute access maps wire names for us
            d.update(
                {
                    "status": s.status,
                    "job_id": s.job_id,
                    "display_name": s.display_name,
                    "created_date_time": s.created_date_time,
                    "last_updated_date_time": s.last_updated_date_time,
                    "expiration_date_time": s.expiration_date_time,
                    "statistics": s.statistics,
                    "errors": s.errors,
                    "next_link": s.next_link,
                }
            )
        return d

    @classmethod
    def from_continuation_token(
        cls,
        polling_method: AsyncPollingMethod[AsyncItemPaged[ConversationActions]],
        continuation_token: str,
        **kwargs: Any,
    ) -> "AnalyzeConversationAsyncLROPoller":
        client, initial_response, deserialization_callback = polling_method.from_continuation_token(
            continuation_token, **kwargs
        )
        return cls(client, initial_response, deserialization_callback, polling_method)
    
def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

__all__ = ["AnalyzeConversationAsyncLROPoller"]