# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Shared polling customizations."""

from functools import wraps
from typing import Any, Type

from azure.core.polling.base_polling import LROBasePolling
from azure.core.polling.async_base_polling import AsyncLROBasePolling


# Foundry services report terminal cancellation as "cancelled", while Azure Core's
# LRO polling logic recognizes "canceled". Patch both base classes so every generated
# and custom sync/async poller terminates correctly without operation-specific subclasses.
# Pollers that directly expose Azure Core status, such as dataset and evaluator generation,
# return "canceled". Agent optimization and Agent Insights pollers preserve their existing
# service-facing contract by translating the internal status back to "cancelled".
def _patch_status(polling_type: Type[Any]) -> None:
    original_status = polling_type.status
    # patch_sdk can be called more than once; do not stack wrappers around status().
    if getattr(original_status, "azure_ai_projects_normalizes_cancelled", False):
        return

    @wraps(original_status)
    def status(self: Any) -> str:
        value = original_status(self)
        return "canceled" if value.lower() == "cancelled" else value

    status.azure_ai_projects_normalizes_cancelled = True  # type: ignore[attr-defined]
    polling_type.status = status


def patch_azure_core_polling_status() -> None:
    """Normalize cancellation status for Azure Core sync and async pollers."""
    _patch_status(LROBasePolling)
    _patch_status(AsyncLROBasePolling)
