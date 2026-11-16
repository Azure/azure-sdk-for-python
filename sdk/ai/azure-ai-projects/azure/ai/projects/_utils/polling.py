# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Shared polling customizations."""

from azure.core.polling.base_polling import LROBasePolling
from azure.core.polling.async_base_polling import AsyncLROBasePolling


class AIProjectsLROBasePolling(LROBasePolling):
    """Azure AI Projects polling that accepts both cancellation spellings."""

    def status(self) -> str:
        value = super().status()
        return "canceled" if value.lower() == "cancelled" else value


class AsyncAIProjectsLROBasePolling(AsyncLROBasePolling):
    """Async Azure AI Projects polling that accepts both cancellation spellings."""

    def status(self) -> str:
        value = super().status()
        return "canceled" if value.lower() == "cancelled" else value
