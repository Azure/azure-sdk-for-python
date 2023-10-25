# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.
Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import List
from ._legacy import (
    EventGridPublisherClient,
    SystemEventNames,
    EventGridEvent,
    generate_sas,
)

def patch_sdk():
    """Do not remove from this file.
    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


__all__: List[str] = [
    "EventGridPublisherClient",
    "SystemEventNames",
    "EventGridEvent",
    "generate_sas",
]  # Add all objects you want publicly available to users at this package level
