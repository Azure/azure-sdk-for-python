# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for public sync and async voice-agent operation exports."""

from importlib import import_module
import inspect
from typing import get_type_hints
from unittest.mock import MagicMock

import pytest


@pytest.mark.parametrize("namespace", ["azure.ai.projects.operations", "azure.ai.projects.aio.operations"])
def test_live_conversations_operation_export(namespace):
    operations = import_module(namespace)
    generated = import_module(f"{namespace}._operations")
    operation_name = "BetaVoiceAgentsLiveConversationsOperations"
    operation_type = getattr(operations, operation_name)

    assert operation_name in operations.__all__
    assert operation_type is getattr(generated, operation_name)
    assert get_type_hints(operations.BetaVoiceAgentsOperations)["live_conversations"] is operation_type

    voice_agents = operations.BetaVoiceAgentsOperations(MagicMock(), MagicMock(), MagicMock(), MagicMock())
    assert isinstance(voice_agents.live_conversations, operation_type)
    assert inspect.iscoroutinefunction(operation_type.get) == (".aio." in namespace)
