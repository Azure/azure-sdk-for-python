# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Compatibility re-export for extension-owned Azure AI Projects generated types."""

from azure.ai.extensions.openai.projects._generated import types as _extension_types
from azure.ai.extensions.openai.projects._generated.types import *  # type: ignore # noqa: F401,F403

for _name in dir(_extension_types):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_extension_types, _name)
