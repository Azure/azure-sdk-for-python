# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Mapping, Optional, Dict, IO, cast, List, TypeVar
import json
from urllib.parse import urlparse

from azure.core.exceptions import HttpResponseError
from azure.core.paging import ItemPaged
from azure.core.polling import LROPoller, AsyncLROPoller
from azure.core.polling.base_polling import LROBasePolling, PollingMethod
from azure.core.rest import HttpRequest
from azure.core.polling.async_base_polling import (
    AsyncLROBasePolling,
)
from azure.core.polling._async_poller import AsyncPollingMethod
from ._models import (
    AnalyzeConversationOperationInput,
    MultiLanguageConversationInput,
    SummarizationOperationAction,
    ConversationSummarizationActionContent,
    AnalyzeConversationOperationAction,
    AnalyzeConversationOperationState,
)

def _parse_operation_id(op_loc: Optional[str]) -> Optional[str]:
    """Extract the final path segment as operation id (service-agnostic)."""
    if not op_loc:
        return None
    path = urlparse(op_loc).path.rstrip("/")
    if "/" not in path:
        return None
    return path.rsplit("/", 1)[-1]

PollingReturnType_co = TypeVar("PollingReturnType_co", covariant=True)

class AnalyzeConversationLROPoller(LROPoller[PollingReturnType_co]):
    """Custom poller that returns PollingReturnType_co and exposes operation metadata."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # populated by the deserialization callback in your begin_* method
        self._last_state: Optional["AnalyzeConversationOperationState"] = None

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
        info: Dict[str, Any] = {"operation_id": op_id}

        # Merge fields from the final state (if available)
        if self._last_state is not None:
            s = self._last_state
            info.update(
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
        return info

    @classmethod
    def from_continuation_token(
        cls,
        polling_method: PollingMethod[PollingReturnType_co],
        continuation_token: str,
        **kwargs: Any,
    ) -> "AnalyzeConversationLROPoller[PollingReturnType_co]":
        client, initial_response, deserialization_callback = polling_method.from_continuation_token(
            continuation_token, **kwargs
        )
        return cls(client, initial_response, deserialization_callback, polling_method)

class AnalyzeConversationAsyncLROPoller(AsyncLROPoller[PollingReturnType_co]):
    """Async poller that returns PollingReturnType_co and exposes operation metadata."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # populated by your deserialization callback in begin_*_async
        self._last_state: Optional["AnalyzeConversationOperationState"] = None

    @property
    def details(self) -> Mapping[str, Any]:
        """Metadata associated with the long-running operation."""
        try:
            headers = self.polling_method()._initial_response.http_response.headers  # type: ignore[attr-defined]
            op_loc = headers.get("Operation-Location") or headers.get("operation-location")
        except Exception:
            op_loc = None

        info: Dict[str, Any] = {"operation_id": _parse_operation_id(op_loc)}

        # Enrich from final state if available
        if self._last_state is not None:
            s = self._last_state
            info.update(
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
        return info

    @classmethod
    def from_continuation_token(
        cls,
        polling_method: AsyncPollingMethod[PollingReturnType_co],
        continuation_token: str,
        **kwargs: Any,
    ) -> "AnalyzeConversationAsyncLROPoller[PollingReturnType_co]":
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


__all__ = [
    "AnalyzeConversationOperationInput",
    "MultiLanguageConversationInput",
    "SummarizationOperationAction",
    "ConversationSummarizationActionContent",
    "AnalyzeConversationOperationAction",
    "AnalyzeConversationLROPoller",
    "AnalyzeConversationAsyncLROPoller",
]