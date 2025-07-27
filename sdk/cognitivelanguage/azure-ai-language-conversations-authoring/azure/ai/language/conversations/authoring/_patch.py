# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
from ._client import AuthoringClient as AuthoringClientGenerated
from ._conversation_project_patch import ConversationAuthoringProject

class ConversationAuthoringClient(AuthoringClientGenerated):
    def get_project(self, project_name: str) -> ConversationAuthoringProject:
        return ConversationAuthoringProject(self.conversation_authoring_project, project_name)

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

__all__ = ["ConversationAuthoringClient"]