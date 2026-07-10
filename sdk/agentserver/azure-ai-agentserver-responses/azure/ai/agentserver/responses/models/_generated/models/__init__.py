# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Compatibility re-export for extension-owned OpenAI Responses model classes."""

from azure.ai.extensions.openai.responses._generated.sdk.models.models import *  # type: ignore # noqa: F401,F403

try:
    from azure.ai.extensions.openai.responses._generated.sdk.models.models import __all__  # type: ignore # noqa: F401
except ImportError:
    __all__: list[str] = []
