# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for shared polling customizations."""

import pytest
from azure.core.polling.base_polling import LROBasePolling
from azure.core.polling.async_base_polling import AsyncLROBasePolling

from azure.ai.projects._utils.polling import patch_azure_core_polling_status


@pytest.mark.parametrize(
    "polling_type",
    [
        LROBasePolling,
        AsyncLROBasePolling,
    ],
)
@pytest.mark.parametrize(
    "status, expected",
    [
        ("cancelled", "canceled"),
        ("Cancelled", "canceled"),
        ("completed", "completed"),
    ],
)
def test_polling_status_normalization(polling_type, status, expected):
    """The Azure Core pollers expose the normalized cancellation spelling."""
    polling = polling_type.__new__(polling_type)
    polling._operation = object()  # pylint: disable=protected-access
    polling._status = status  # pylint: disable=protected-access

    assert polling.status() == expected


@pytest.mark.parametrize("polling_type", [LROBasePolling, AsyncLROBasePolling])
def test_polling_status_patch_is_idempotent(polling_type):
    """Applying the package patch repeatedly does not wrap status repeatedly."""
    patched_status = polling_type.status

    patch_azure_core_polling_status()

    assert polling_type.status is patched_status
