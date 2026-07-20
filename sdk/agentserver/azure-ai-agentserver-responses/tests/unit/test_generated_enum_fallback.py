# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Tests for generated enum compatibility fallback behavior."""

from __future__ import annotations

import pytest

from azure.ai.agentserver.responses.models._generated import _enums


def test_generated_enum_fallback_rejects_unknown_members() -> None:
    assert _enums.AnnotationType.FILECITATION.value == "file_citation"

    with pytest.raises(AttributeError):
        _enums.AnnotationType.FILECIATION
