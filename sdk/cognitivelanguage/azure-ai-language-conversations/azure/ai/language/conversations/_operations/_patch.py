# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Mapping, Optional, Union, IO, cast, List
import json
from urllib.parse import urlparse

from azure.core.exceptions import HttpResponseError
from azure.core.paging import ItemPaged
from azure.core.polling import LROPoller
from azure.core.polling.base_polling import LROBasePolling, PollingMethod
from azure.core.rest import HttpRequest

from ..models import (
    AnalyzeConversationOperationInput,
    AnalyzeConversationOperationState,
    ConversationActions,
)

# -------------------------
# Helpers
# -------------------------

def _parse_operation_id(op_loc: Optional[str]) -> Optional[str]:
    """Extract the final path segment as operation id (service-agnostic)."""
    if not op_loc:
        return None
    path = urlparse(op_loc).path.rstrip("/")
    if "/" not in path:
        return None
    return path.rsplit("/", 1)[-1]


# -------------------------
# Custom Poller
# -------------------------

class AnalyzeConversationLROPoller(LROPoller[ItemPaged[ConversationActions]]):
    """Custom poller that returns ItemPaged[ConversationActions] and exposes operation metadata."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # populated by our deserialization callback
        self._last_state: Optional[AnalyzeConversationOperationState] = None

    @property
    def details(self) -> Mapping[str, Any]:
        """Metadata associated with the long-running operation."""
        try:
            # header name may vary in case; be tolerant
            headers = getattr(self.polling_method(), "_initial_response").http_response.headers  # type: ignore[attr-defined]
            op_loc = headers.get("Operation-Location") or headers.get("operation-location")
        except Exception:
            op_loc = None

        op_id = _parse_operation_id(op_loc)
        d: dict = {"operation_id": op_id}

        # Merge fields from the final state (if available)
        if self._last_state is not None:
            s = self._last_state
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
        polling_method: PollingMethod[ItemPaged[ConversationActions]],
        continuation_token: str,
        **kwargs: Any,
    ) -> "AnalyzeConversationLROPoller":
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

__all__ = ["AnalyzeConversationLROPoller"]