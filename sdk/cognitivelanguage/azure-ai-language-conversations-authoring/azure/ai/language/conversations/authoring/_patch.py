# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
from ._client import ConversationAuthoringClient as AuthoringClientGenerated
from ._client import ConversationAuthoringProjectClient as AuthoringProjectClientGenerated


class ConversationAuthoringProjectClient(AuthoringProjectClientGenerated):
    """Custom Project Client that auto-injects project_name into operation groups."""

    def __init__(self, parent_client: AuthoringClientGenerated, project_name: str, **kwargs):
        # Call the generated constructor with values from the parent
        super().__init__(
            endpoint=parent_client._config.endpoint,
            credential=parent_client._config.credential,
            project_name=project_name,
            **kwargs
        )
        self._project_name = project_name

        # Re-wrap operation groups so they auto-inject project_name
        self.deployment_operations = self._wrap_ops(super().deployment_operations)
        self.project_operations = self._wrap_ops(super().project_operations)
        self.exported_model = self._wrap_ops(super().exported_model)
        self.trained_model = self._wrap_ops(super().trained_model)

    def _wrap_ops(self, operations_group):
        """Wrap each callable in the operations group to inject project_name."""

        class Wrapper:
            def __init__(self, operations, project_name):
                self._operations = operations
                self._project_name = project_name

            def __getattr__(self, item):
                func = getattr(self._operations, item)
                if callable(func):

                    def wrapped(*args, **kwargs):
                        kwargs.setdefault("project_name", self._project_name)
                        return func(*args, **kwargs)

                    return wrapped
                return func

        return Wrapper(operations_group, self._project_name)


class ConversationAuthoringClient(AuthoringClientGenerated):
    def get_project_client(self, project_name: str) -> ConversationAuthoringProjectClient:
        return ConversationAuthoringProjectClient(self, project_name)


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


__all__ = ["ConversationAuthoringProjectClient", "ConversationAuthoringClient"]
