# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Type definitions for OpenAI API response models.
This module contains TypedDict definitions based on the OpenAI SDK types.
"""
# from openai.types.responses import *
from . import response_create_params
from .response_input_protocols import (
    ResponseInputItemParam,
)

__all__ = [
    "response_create_params",
    "ResponseInputItemParam",
]