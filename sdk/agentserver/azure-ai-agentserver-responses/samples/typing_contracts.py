# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""Static typing contracts for public model shapes.

This module is checked by the package mypy validation. It intentionally keeps
small assignment-only examples that should type-check for public request models.
"""

from __future__ import annotations

from azure.ai.agentserver.responses.models import CreateResponse


def build_function_call_input_without_id() -> CreateResponse:
    return {
        "model": "test-model",
        "input": [
            {
                "type": "function_call",
                "call_id": "call_123",
                "name": "lookup",
                "arguments": "{}",
            }
        ],
    }
