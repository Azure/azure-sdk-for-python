# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Tests for generated enum compatibility fallback behavior."""

from __future__ import annotations

import pytest

from azure.ai.agentserver.responses.models._generated import _enums


def test_generated_enums_preserve_enum_runtime_contract() -> None:
    assert _enums.AnnotationType.FILECITATION.value == "file_citation"
    assert _enums.AnnotationType.FILE_CITATION.value == "file_citation"
    assert isinstance(_enums.AnnotationType.FILECITATION, _enums.AnnotationType)
    assert list(_enums.AnnotationType)


def test_generated_enums_reject_unknown_members() -> None:
    with pytest.raises(AttributeError):
        _enums.AnnotationType.UNKNOWN_MEMBER
