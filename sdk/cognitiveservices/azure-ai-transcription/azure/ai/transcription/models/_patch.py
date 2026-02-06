# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Optional

from ._models import EnhancedModeProperties as _EnhancedModeProperties


class EnhancedModeProperties(_EnhancedModeProperties):
    """Enhanced mode properties for transcription.

    :ivar task: Task type for enhanced mode.
    :vartype task: str
    :ivar target_language: Target language for enhanced mode.
    :vartype target_language: str
    :ivar prompt: A list of user prompts.
    :vartype prompt: list[str]
    """

    def __init__(
        self,
        *,
        task: Optional[str] = None,
        target_language: Optional[str] = None,
        prompt: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(task=task, target_language=target_language, prompt=prompt, **kwargs)
        # Automatically set enabled=True if any enhanced mode properties are specified
        # This is hidden from public API but sent to the server
        self._enabled: Optional[bool] = None
        if task is not None or target_language is not None or prompt is not None:
            self._enabled = True

    def as_dict(self, *, exclude_readonly: bool = False) -> dict[str, Any]:
        """Return a dict that can be turned into json using json.dump.

        :keyword bool exclude_readonly: Whether to remove the readonly properties.
        :returns: A dict JSON compatible object
        :rtype: dict
        """
        result = super().as_dict(exclude_readonly=exclude_readonly)
        # Always include enabled in the request if it's set
        if self._enabled is not None:
            result["enabled"] = self._enabled
        return result


__all__: list[str] = [
    "EnhancedModeProperties"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
