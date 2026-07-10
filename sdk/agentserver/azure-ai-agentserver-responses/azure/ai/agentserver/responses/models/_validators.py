# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Validation entry points for response wire payloads."""

from __future__ import annotations

from typing import Any, Mapping

from ._generated._validators import validate_CreateResponse


def validate_create_response_payload(payload: Mapping[str, Any]) -> list[dict[str, str]]:
    """Validate a create response request payload against the generated wire schema."""
    return validate_CreateResponse(payload)
