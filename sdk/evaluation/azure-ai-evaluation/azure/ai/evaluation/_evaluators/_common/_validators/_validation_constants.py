# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Constants and enums for validation.
"""

from enum import Enum
from azure.ai.projects.models import ResponsesMessageRole

class MessageRole(str, Enum):
    """Valid message roles in conversations."""
    USER = ResponsesMessageRole.USER.value
    ASSISTANT = ResponsesMessageRole.ASSISTANT.value
    SYSTEM = ResponsesMessageRole.SYSTEM.value
    TOOL = "tool"


class ContentType(str, Enum):
    """Valid content types in messages."""
    TEXT = "text"
    INPUT_TEXT = "input_text"
    OUTPUT_TEXT = "output_text"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
