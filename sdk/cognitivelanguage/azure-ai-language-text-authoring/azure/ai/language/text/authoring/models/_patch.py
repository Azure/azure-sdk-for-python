# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
from ._models import (
    TextAuthoringCreateProjectDetails as TextAuthoringCreateProjectDetailsGenerated,
    TextAuthoringProjectSettings,
    TextAuthoringProjectKind,
)
from typing import Any, Dict, List, Literal, Mapping, Optional, TYPE_CHECKING, Union, overload
class TextAuthoringCreateProjectDetails(TextAuthoringCreateProjectDetailsGenerated):

    @overload
    def __init__(
        self,
        *,
        project_kind: Union[str, "TextAuthoringProjectKind"],
        storage_input_container_name: str,
        language: str,
        settings: Optional["TextAuthoringProjectSettings"] = None,
        multilingual: Optional[bool] = None,
        description: Optional[str] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None: ...

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("project_name", "")  # provide dummy value
        super().__init__(*args, **kwargs)

def patch_sdk():
    """Do not remove from this file.
    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

__all__ = ["TextAuthoringCreateProjectDetails"]